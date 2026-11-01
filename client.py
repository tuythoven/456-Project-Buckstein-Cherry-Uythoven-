import json
import socket
import time

SERVICE_ADDR = ("127.0.0.1", 8888)
REQUEST_INTERVAL = 1
RESPONSE_TIMEOUT = 2
LOGIN = json.dumps({"username": "TestStudent", "password": "TestPassword"}).encode()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(RESPONSE_TIMEOUT)

print("[CLIENT] Requesting tickets from the service. Ctrl+C to stop.")

while True:
    try:
        sock.sendto(LOGIN, SERVICE_ADDR)
        data, _ = sock.recvfrom(1024)
        reply = json.loads(data.decode())
        print(f"[CLIENT] {reply.get('Ticket #')} (total issued: {reply.get('Total Tickets Issued')})")
    except (socket.timeout, ConnectionResetError):
        print("[CLIENT] No response - service may be down. Retrying...")
    time.sleep(REQUEST_INTERVAL)