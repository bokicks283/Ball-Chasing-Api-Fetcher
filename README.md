# Rocket League Ballchasing Data Sync

> The goal of this project is to sync the ballchasing api with an excel dashboard.

## Setup
1. create a file called .env in the root of the repo (Main folder)
2. copy the values from example.env.
3. paste your ballchasing api key for the value of BC_API_TOKEN (dont worry about the MYSQL_DB_PASS for now.)
4. create conda env for this project
   `conda create python=3.14.2 -n bc-api-fetcher`
5. activate conda env
   `conda activate bc-api-fetcher`
6. install dependencies
   `pip install -r requirements.txt`
7. run the script with the command
   `python .\src\main.py`
