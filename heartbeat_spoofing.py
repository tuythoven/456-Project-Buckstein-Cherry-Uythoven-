import socket

HOST = "127.0.0.1"
PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"[SPOOF] Listening on {HOST}:{PORT} — impersonating the service")

while True:
    data, addr = sock.recvfrom(1024)
    if data == b"PING":
        sock.sendto(b"ACK", addr)
        print(f"[SPOOF] Forged ACK sent to {addr}")