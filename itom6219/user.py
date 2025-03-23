import requests
import pandas as pd
from .auth import bearer_oauth

def user_info(usernames):
    usernames_str = ",".join(usernames)
    user_fields = "user.fields=description,created_at,verified,public_metrics,id"
    url = f"https://api.twitter.com/2/users/by?usernames={usernames_str}&{user_fields}"
    
    response = requests.get(url, auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
    data = response.json().get("data", [])
    return pd.json_normalize(data)


def user_tweets(usernames, max_results=100):
    info_df = user_info(usernames)
    all_tweets = []

    for _, row in info_df.iterrows():
        user_id = row["id"]
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {
            "tweet.fields": "created_at,public_metrics",
            "max_results": max_results  # Twitter allows up to 100
        }
        response = requests.get(url, auth=bearer_oauth, params=params)

        if response.status_code != 200:
            print(f"Error fetching tweets for user {row.get('username', 'unknown')}: {response.status_code}")
            continue

        tweets = response.json().get("data", [])
        tweet_df = pd.json_normalize(tweets)
        tweet_df["username"] = row["username"]
        all_tweets.append(tweet_df)

    return pd.concat(all_tweets, ignore_index=True) if all_tweets else pd.DataFrame()

import time
from .user import user_info     # assuming this lives in the same package

def user_tweets_all(usernames, max_total=1000):
    info_df = user_info(usernames)
    all_tweets = []

    for _, row in info_df.iterrows():
        user_id = row["id"]
        username = row["username"]
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"

        params = {
            "tweet.fields": "created_at,public_metrics",
            "max_results": 100,  # max allowed per request
        }

        tweet_count = 0
        pagination_token = None

        while tweet_count < max_total:
            if pagination_token:
                params["pagination_token"] = pagination_token

            response = requests.get(url, auth=bearer_oauth, params=params)

            if response.status_code != 200:
                print(f"Error fetching tweets for user {username}: {response.status_code}")
                break

            response_data = response.json()
            tweets = response_data.get("data", [])
            meta = response_data.get("meta", {})

            if not tweets:
                break  # No more tweets available

            tweet_df = pd.json_normalize(tweets)
            tweet_df["username"] = username
            all_tweets.append(tweet_df)

            tweet_count += len(tweets)

            pagination_token = meta.get("next_token")
            if not pagination_token:
                break  # No more pages

            time.sleep(1)  # Optional: avoid hitting rate limits

    return pd.concat(all_tweets, ignore_index=True) if all_tweets else pd.DataFrame()

