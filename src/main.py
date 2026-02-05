import json
import os
import time
from dotenv import load_dotenv
from rlstore.ballchasing_client import BallChasingClient

def main():
    load_dotenv(".env")
    token = os.environ.get("BC_API_TOKEN")
    if not token:
        raise Exception("BC_API_TOKEN not found in environment variables.")
    # Initialize the BallChasingClient
    client = BallChasingClient(token)
    # Play fancy animation and simulate load time.
    print("Pinging BallChasing API", end="", flush=True)
    spinner = ["|", "/", "-", "\\"]
    for i in range(6):
        print(f"\rPinging BallChasing API {spinner[i % 4]}", end="", flush=True)
        time.sleep(0.25)
    else:
        print("\b\b ", end="", flush=True)
    print()
    print(json.dumps(client.ping(), indent=4))
    
if __name__ == "__main__":
    main()
