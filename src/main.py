import requests
import os
from dotenv import load_dotenv

def main():
    load_dotenv("../.env")
    token = os.environ.get("BC_API_TOKEN")
    

if __name__ == "__main__":
    main()
