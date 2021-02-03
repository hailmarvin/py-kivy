import tweepy
import os
import time
import random

## API Credentials
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
# myFollowers = []
# myFollowing = []

def get_user(username):
    user = api.get_user(username)
    return user

def get_friends(username):
    friends = []
    for friend in api.friends(username):
        friends.append(friend.screen_name)

    return friends

def get_followers(username):
    followers = []
    for follower in api.followers(username):
        followers.append(follower.screen_name)

    return followers