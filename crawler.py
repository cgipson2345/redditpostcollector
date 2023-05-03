# Libraries
from bs4 import BeautifulSoup   # for parsing HTML documents
import json                     # for encoding data in JSON format
import praw                     # for accessing Reddit API
import requests                 # for making HTTP requests
import os                       # for files

# Constants
MB = 1024*1024 # 1MB

# Reddit credentials to crawl the website
reddit = praw.Reddit(client_id='BVN377aTHCSupxRmvJxRcA',
                     client_secret='Nd-gzmX0P8vkdF8YGG0ebZaU26Z8kQ',
                     user_agent='CS172:SPR23GROUP21:v0.1 (by u/wecrawling)',
                     username='wecrawling',
                     password='crawling21')

# Subreddits to crawl
subreddits = ['ucr','ucmerced','ucla','UCDavis','berkely','UCSD',
              'UCSantaBarbara','UCSC','UCI','UofCalifornia',
              'CSULB','CSULA','csuf'] # Can add more subreddits later

# Delete all files in the Data folder
for file_name in os.listdir("Data"):
    os.remove(os.path.join("Data", file_name))

# Posts list to hold each post's data
posts = list()

# Go through each subreddit
print("\nStart crawling subreddits...\n")
for subreddit_name in subreddits:
    print("Started crawling subreddit:",subreddit_name)
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
    print("Finished crawling subreddit:",subreddit_name)
print("\nFinished crawling subreddits...")

# Current file that is written too
file_number = 0
#currently set file to 1 mb and raw data to 10 mb for testing
min_file_size = 1 * MB  # File size
min_data_size = 10 * MB  # Raw data size
#this tests current file size
data = []
running_total = 0

print("\nStart writing to files...\n")
# Write to files until the minimum amount of data is passed
while running_total <= min_data_size:
    # Go through each post
    for post_data in posts:
        if len(json.dumps(data)) >= min_file_size:
            filename = f"Data/fileNum{file_number}.json"
            with open(filename,"w") as f:
                for d in data:
                    json.dump(d, f)
                    f.write('\n')
                file_size_mb = os.path.getsize(filename) / MB
                print(f"File {filename} size: {file_size_mb:.2f} MB")
            # Increase the file number and clear the data list
            file_number += 1
            data = []
        # Append the current data to the data list
        data.append(post_data)
        #print(json.dumps(data))
        running_total += len(json.dumps(post_data))

        # Write the remaining data into the last file
        if data and sum(os.path.getsize(f"Data/{f}") for f in os.listdir("Data")) >= min_data_size:
            filename = f"Data/fileNum{file_number}.json"
            with open(filename, "w") as f:
                for d in data:
                    json.dump(d, f)
                    f.write('\n')
            # Clear the data list
            data = []
print("\nDone writing to files...\n")
print(f"{(running_total)/MB:.2f} MB of data stored in {file_number} files")