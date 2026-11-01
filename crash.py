import socket
import time
 
SERVICE_ADDR = ("127.0.0.1", 8888)
REQUESTS = 30
DELAY = 0.1  # seconds between requests, just so it's visible on screen
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
print(f"[TRIGGER] Sending up to {REQUESTS} dummy requests to force the crash...")
 
for i in range(1, REQUESTS + 1):
    sock.sendto(b'{"username":"a","password":"b"}', SERVICE_ADDR)
    print(f"[TRIGGER] Sent request {i}")
    time.sleep(DELAY)
 
print("[TRIGGER] Done sending. Check the service terminal for 'Crashed'.")