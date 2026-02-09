import json
import os

from dotenv import load_dotenv

from ballchasing_client.ballchasing_client import BallChasingClient


def main():
    load_dotenv(".env")
    token = os.environ.get("BC_API_TOKEN")
    if not token:
        raise Exception("BC_API_TOKEN not found in environment variables.")
    # Initialize the BallChasingClient
    client = BallChasingClient(token)
    print("Pinging BallChasing API")
    ping_results = []
    print(json.dumps(client.ping(), indent=4))

    print("\b\b ", end="", flush=True)
    print("\rAttempting to trigger rate limit done.", end="", flush=True)
    print()
    for r in ping_results:
        print(json.dumps(r, indent=4))


if __name__ == "__main__":
    main()
