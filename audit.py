import json
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ADDR = ("127.0.0.1", 8888)
LOGIN = json.dumps({"username": "TestStudent", "password": "TestPassword"}).encode()
GOOD_STATE = {
    "ticket_number": 2,
    "tickets_issued": [
        {"username": "TestStudent", "ticket": "TICKET-1"},
        {"username": "TestStudent", "ticket": "TICKET-2"},
    ],
}
FORGED_TICKET = "TICKET-1000"  # what the replica issues if it trusts a counter of 999

CHECKPOINTS = {
    "valid checkpoint (control)": json.dumps(GOOD_STATE),
    "truncated JSON": '{"ticket_number": 2, "tickets_iss',
    "empty file": "",
    "wrong schema": '{"foo": 1}',
    "tampered counter": json.dumps({**GOOD_STATE, "ticket_number": 999}),
}

workdir = Path(tempfile.mkdtemp())
for script in ("heartbeat.py", "replica.py"):
    shutil.copy(Path(__file__).resolve().parent / script, workdir)


def result(name, passed, detail):
    print(f"[{'PASS' if passed else 'FAIL'}] {name}\n    {detail}")


def attack_1_false_failover():
    print("\n=== Attack 1: false failover (primary alive but not answering heartbeats) ===")
    primary = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    primary.bind(ADDR)  # holds the port, but never ACKs a PING
    primary.settimeout(3)
    monitor = subprocess.Popen([sys.executable, "heartbeat.py"], cwd=workdir,
                               stderr=subprocess.PIPE, text=True)
    time.sleep(10)  # long enough for 3 missed heartbeats and the failover

    # Send a client request. If our "primary" still receives it, no other node took the port.
    socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(LOGIN, ADDR)
    try:
        while primary.recvfrom(1024)[0] == b"PING":  # skip queued heartbeats
            pass
        primary_still_owns_port = True
    except socket.timeout:
        primary_still_owns_port = False

    monitor.terminate()
    log = monitor.communicate()[1]
    primary.close()

    keywords = ("CRASH DETECTED", "FAILOVER_TRIGGERED", "SERVICE RESTORED", "Address already in use")
    for line in log.splitlines():
        if any(k in line for k in keywords):
            print("    log:", line)

    result("No split-brain", primary_still_owns_port,
           "only the original primary received the client request" if primary_still_owns_port
           else "another node is answering on the primary's port")
    claimed_restored = "SERVICE RESTORED" in log
    result("Monitor log is truthful", not (claimed_restored and primary_still_owns_port),
           "monitor logged SERVICE RESTORED, but the replica never took over the port")


def get_ticket():
    """Send one login to the service; return the ticket, or None if nobody answers."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        try:
            s.sendto(LOGIN, ADDR)
            return json.loads(s.recvfrom(1024)[0]).get("Ticket #")
        except (socket.timeout, ConnectionResetError):
            return None


def attack_2_bad_checkpoints():
    print("\n=== Attack 2: corrupted / tampered checkpoint ===")
    for name, content in CHECKPOINTS.items():
        (workdir / "checkpoint.json").write_text(content)
        replica = subprocess.Popen([sys.executable, "replica.py"], cwd=workdir,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        ticket = get_ticket()
        replica.kill()
        replica.wait()
        # Graceful = replica still serves AND did not accept the forged counter.
        graceful = ticket is not None and ticket != FORGED_TICKET
        result(name, graceful,
               f"replica {'DOWN' if ticket is None else 'up'}; next ticket = {ticket}")


attack_1_false_failover()
attack_2_bad_checkpoints()
shutil.rmtree(workdir, ignore_errors=True)