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


def user_tweets(usernames):
    info_df = user_info(usernames)
    all_tweets = []

    for _, row in info_df.iterrows():
        user_id = row["id"]
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {"tweet.fields": "created_at,public_metrics"}
        response = requests.get(url, auth=bearer_oauth, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching tweets for user {row['username']}: {response.status_code}")
            continue
        
        tweets = response.json().get("data", [])
        tweet_df = pd.json_normalize(tweets)
        tweet_df["username"] = row["username"]
        all_tweets.append(tweet_df)

    return pd.concat(all_tweets, ignore_index=True) if all_tweets else pd.DataFrame()
