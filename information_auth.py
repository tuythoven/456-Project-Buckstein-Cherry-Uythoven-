import socket
import json
import random
import os

HOST = "127.0.0.1"
PORT = 8888
CRASH_PROBABILITY = 0.10

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((HOST, PORT))

print("Up and running!")

while True:
    data, addr = sock.recvfrom(1024)

    if data == b"PING":
        sock.sendto(data, (HOST,PORT))
        print("Received heartbeat, ACK sent")

    else:
        # Totally unpredictable crash
        if random.random() < CRASH_PROBABILITY:
            print("Crashed")
            os._exit(1)

        try:
            request = json.loads(data.decode())

            username = request.get("username")
            password = request.get("password")

            if username == "TestStudent" and password == "TestPassword":
                response = {
                    "Status": "Success",
                    "Ticket #": "TICKET-BlahBlahBlah"
                }

            else:
                response = {
                    "Status": "Failed",
                    "Message": "Invalid Login"
                }

        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            response = {
                "Status": "Failed",
                "Message": "Invalid Request"
            }

        sock.sendto(json.dumps(response).encode(), addr)
