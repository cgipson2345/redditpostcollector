# Libraries
from bs4 import BeautifulSoup   # for parsing HTML documents
import json                     # for encoding data in JSON format
import praw                     # for accessing Reddit API
import requests                 # for making HTTP requests
import os                       # for files

# Reddit credentials to crawl the website
reddit = praw.Reddit(client_id='BVN377aTHCSupxRmvJxRcA',
                     client_secret='Nd-gzmX0P8vkdF8YGG0ebZaU26Z8kQ',
                     user_agent='CS172:SPR23GROUP21:v0.1 (by u/wecrawling)',
                     username='wecrawling',
                     password='crawling21')

# Subreddits to crawl
subreddits = ['ucr'] # Can add more subreddits later

# Filename to hold posts
# Still need code to collect at least 500MB of raw data, ~10MB per file
filename = 'posts.json'
# Open file to write data
if os.path.exists(filename):
    os.remove(filename)
file = open(filename, 'w')

# Posts list to hold each post's data
posts = list()

# Go through each subreddit
for subreddit_name in subreddits:
    # Currently grabs the 10 hottest posts, can change to what we want later
    cur_subreddit = reddit.subreddit(subreddit_name).hot(limit=10)
    # Loop over each post in the current subreddit
    for post in cur_subreddit:
        # Store the data in dictionary
        post_data = {
            'subreddit': subreddit_name,    # Subreddit's name
            'body': post.selftext,          # Body
            'title': post.title,            # Title
            'id': post.id,                  # Id
            'score': post.score,            # Upvotes
            'url': post.url,                # Image in post
            'permalink': post.permalink,    # URL of post
        }
        # If a post contains a URL to an html page, get title of that page, and add title as an additional field of the post, 
        # that is, include it in the JSON of the post, so it becomes searchable in Part B.
        if post.url.endswith('.html'):
            # Try to get the URL in the post
            try:
                # Send request to the post URL
                response = requests.get(post.url)
                # Parse using BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                # Add the URL's title to the post's data
                post_data['page_title'] = soup.title.string
            # Failed to get the URL
            except Exception as e:
                print('ERROR: Failed to retrieve page title for {}: {}'.format(post.url, e))
        # Append the current data to the current post
        posts.append(post_data)
# Write data into file
with file as f:
    # Get each post's data
    for post_data in posts:
        # Write JSON data
        json.dump(post_data, f)
        # One post per row
        f.write('\n')
# Close file
file.close()