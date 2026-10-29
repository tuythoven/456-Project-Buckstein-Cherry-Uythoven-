import socket
import json
import random
import os
import logging

HOST = "127.0.0.1"
PORT = 8888
CRASH_PROBABILITY = 0.10
CHECKPOINTING_FILE = "checkpoint.json"

logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("ticketing.log"),
        logging.StreamHandler(),
    ],
)

state = {
    "ticket_number": 0,
    "tickets_issued": []
}

def checkpoint():
    with open(CHECKPOINTING_FILE, "w") as f:
        json.dump(state, f)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((HOST, PORT))

logging.info("Ticketing Service up and running!")
checkpoint()

while True:
    data, addr = sock.recvfrom(1024)

    if data == b"PING":
        sock.sendto(b"ACK",addr)
        logging.info("Received heartbeat, ACK sent")

    else:
        # Totally unpredictable crash
        if random.random() < CRASH_PROBABILITY:
            logging.warning("Node experienced crash. Exiting.")
            os._exit(1)

        try:
            request = json.loads(data.decode())

            username = request.get("username")
            password = request.get("password")

            if username == "TestStudent" and password == "TestPassword":
                state["ticket_number"] += 1
                ticket_id = f"TICKET-{state['ticket_number']}"
                state["tickets_issued"].append({"username": username, "ticket": ticket_id})
                checkpoint()
                
                response = {
                    "Status": "Success",
                    "Ticket #": ticket_id,
                    "Total Tickets Issued": state["ticket_number"]
                }
                logging.info(f"Successfully issued ticket: {ticket_id}")

            else:
                response = {
                    "Status": "Failed",
                    "Message": "Invalid Login"
                }
                logging.warning("Failed login attempt.")

        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            response = {
                "Status": "Failed",
                "Message": "Invalid Request"
            }
            logging.error("Malformed client request received.")

        sock.sendto(json.dumps(response).encode(), addr)
 
