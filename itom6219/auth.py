import os

def bearer_oauth(r):
    bearer_token = os.getenv("BEARER_TOKEN")
    if not bearer_token:
        raise Exception("Missing BEARER_TOKEN environment variable")
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "itom6219"
    return r
