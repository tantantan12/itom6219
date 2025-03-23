
import requests
import pandas as pd
import time
from .auth import bearer_oauth
from .user import user_info

def user_info(usernames):
    usernames_str = ",".join(usernames)
    user_fields = "user.fields=description,created_at,verified,public_metrics,id"
    url = f"https://api.twitter.com/2/users/by?usernames={usernames_str}&{user_fields}"
    
    response = requests.get(url, auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
    data = response.json().get("data", [])
    return pd.json_normalize(data)




def build_params(max_results=100, exclude_replies=False, exclude_retweets=False):
    # Build tweet.fields
    tweet_fields = ",".join([
        "id", "text", "created_at", "public_metrics", "conversation_id",
        "in_reply_to_user_id", "lang", "source"
    ])

    # Build exclude parameter
    exclude = []
    if exclude_replies:
        exclude.append("replies")
    if exclude_retweets:
        exclude.append("retweets")

    params = {
        "tweet.fields": tweet_fields,
        "max_results": max_results
    }

    if exclude:
        params["exclude"] = ",".join(exclude)

    return params


def user_tweets(usernames, max_results=100, exclude_replies=False, exclude_retweets=False):
    info_df = user_info(usernames)
    all_tweets = []

    params = build_params(max_results, exclude_replies, exclude_retweets)

    for _, row in info_df.iterrows():
        user_id = row["id"]
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        response = requests.get(url, auth=bearer_oauth, params=params)

        if response.status_code != 200:
            print(f"Error fetching tweets for user {row.get('username', 'unknown')}: {response.status_code}")
            continue

        tweets = response.json().get("data", [])
        tweet_df = pd.json_normalize(tweets)
        tweet_df["username"] = row["username"]
        all_tweets.append(tweet_df)

    return pd.concat(all_tweets, ignore_index=True) if all_tweets else pd.DataFrame()


def user_tweets_all(usernames, max_total=1000, exclude_replies=False, exclude_retweets=False):
    info_df = user_info(usernames)
    all_tweets = []

    for _, row in info_df.iterrows():
        user_id = row["id"]
        username = row["username"]
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"

        tweet_count = 0
        pagination_token = None

        while tweet_count < max_total:
            remaining = max_total - tweet_count
            batch_size = min(100, remaining)
            params = build_params(batch_size, exclude_replies, exclude_retweets)

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
                break

            tweet_df = pd.json_normalize(tweets)
            tweet_df["username"] = username
            all_tweets.append(tweet_df)

            tweet_count += len(tweets)

            pagination_token = meta.get("next_token")
            if not pagination_token:
                break

            time.sleep(1)

    return pd.concat(all_tweets, ignore_index=True) if all_tweets else pd.DataFrame()
