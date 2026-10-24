import socket
import time
 
SERVICE_ADDR = ("127.0.0.1", 8888)
MONITOR_ADDR = ("127.0.0.1", 9999)
REPLAY_INTERVAL = 1
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)
 
print("[REPLAY] Querying the live service for a real ACK...")
sock.sendto(b"PING", SERVICE_ADDR)
payload, _ = sock.recvfrom(1024)
print(f"[REPLAY] Captured {payload} from the real service")
 
print("[REPLAY] Kill the real service now, then replay begins")
 
while True:
    sock.sendto(payload, MONITOR_ADDR)
    print(f"[REPLAY] Replayed {payload} to {MONITOR_ADDR}")
    time.sleep(REPLAY_INTERVAL)