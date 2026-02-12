import json
import os

from dotenv import load_dotenv

from ballchasing_client.ballchasing_client import BallChasingClient
from ballchasing_client.model.ballchasing_model import ReplayQuery


def main():
    load_dotenv(".env")
    token = os.environ.get("BC_API_TOKEN")
    if not token:
        raise Exception("BC_API_TOKEN not found in environment variables.")

    with BallChasingClient(token) as client:
        query = ReplayQuery(
            limit=100000,
            count=200
        )
        replays = client.list_replays(query)
        replay_ids = [replay["id"] for replay in replays]
        unique_replay_ids = list(set(replay_ids))
        print(f"Found {len(replays)} replays, {len(unique_replay_ids)} unique")
        json.dump(replays, open("replays.json", "w"), indent=4)


if __name__ == "__main__":
    main()
