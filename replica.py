import socket
import json
import os
import logging

HOST = "127.0.0.1"
PORT = 8888
CHECKPOINTING_FILE = "checkpoint.json"

logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("replica.log"),
        logging.StreamHandler(),
    ],
)

state = {
    "ticket_number": 0,
    "tickets_issued": []
}
if os.path.exists(CHECKPOINTING_FILE):
    with open(CHECKPOINTING_FILE, "r") as f:
        state = json.load(f)
    logging.info(f"[REPLICA] Loaded checkpoint state. Total tickets issued before crash: {state['ticket_number']}")
else:
    logging.warning("[REPLICA] No previous checkpoint found, start from a fresh state.")
    
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

logging.info("[REPLICA] Standby service promoted and running on port 8888")

while True:
    data, address = sock.recvfrom(1024)
    
    if data == b"PING":
        sock.sendto(b"ACK", address)
        logging.info("[REPLICA] Received heartbeat, sent ACK")
    else:
        try:
            request = json.loads(data.decode())
            username = request.get("username")
            password = request.get("password")
            
            if username == "TestStudent" and password == "TestPassword":
                state["ticket_number"] += 1
                ticket_id = f"TICKET-{state['ticket_number']}"
                state["tickets_issued"].append({"username": username, "ticket": ticket_id})
                
                response = {
                    "Status": "Success",
                    "Ticket #": ticket_id,
                    "Total Tickets Issued": state["ticket_number"]
                }
                logging.info(f"[REPLICA] Successfuly issued a ticked after failure: {ticket_id}")

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

        sock.sendto(json.dumps(response).encode(), address)
