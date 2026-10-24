import logging
import socket
import time

HOST = "127.0.0.1"
PORT = 8888
# Can change these for changes in ping time and response time and drop time
INTERVAL_T = 1
RESPONSE_WINDOW = 1
MISSED_THRESHOLD = 3
MONITOR_PORT = 9999 # fixed port so the monitor has a known, reachable address

logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("monitoring.log"),
        logging.StreamHandler(),
    ],
)

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST,MONITOR_PORT))
    sock.settimeout(RESPONSE_WINDOW)

    misses = 0
    logging.info("Monitor started.")
    logging.info("Pinging service within a ceratin interval and response window.")
    logging.info("Failure threshold set.")

    while True:
        time.sleep(INTERVAL_T)
        try:
            sock.sendto(b"PING", (HOST, PORT))
            data, addr = sock.recvfrom(1024)
            if data == b"ACK":
                if misses > 0:
                    logging.info("Service recovered.")
                misses = 0

        except socket.timeout:
            misses += 1
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            logging.warning(
                f"Missed a heartbeat response"
                f"({misses}/{MISSED_THRESHOLD})"
            )

            if misses >= MISSED_THRESHOLD:
                logging.error(
                    "[ALERT] Critical Service Failure Detected! "
                    f" {MISSED_THRESHOLD} consecutive missed replies. \n")


if __name__ == "__main__":
    run()
