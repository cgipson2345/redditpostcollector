# Libraries
from bs4 import BeautifulSoup   # for parsing HTML documents
import json                     # for encoding data in JSON format
import praw, prawcore           # for accessing Reddit API
import requests                 # for making HTTP requests
import os                       # for file checking
import re                       # for regex


# Constants
MB = 1024*1024 # 1MB

# File Handling
file_number = int(input("Input how many json files currently possessed\n"))
if(file_number < 0):
    print("Error, negative number input, please try again.")
    exit        # Num. of files created
cur_data_size = 0       # Total amount of data written
min_file_size = 10 * MB  # Files should be around 10 MB
min_data_size = 10 * MB # Total amount of data written should be around 500MB
data = []               # Holds data to write to file

# Reddit credentials to crawl the website
reddit = praw.Reddit(client_id='BVN377aTHCSupxRmvJxRcA',
                     client_secret='Nd-gzmX0P8vkdF8YGG0ebZaU26Z8kQ',
                     user_agent='CS172:SPR23GROUP21:v0.1 (by u/wecrawling)',
                     username='wecrawling',
                     password='crawling21')
test = False
subreddits = []
while(test!=True):
    try:
        subreddit = input("Enter which subreddit you would like to crawl\n").lower()
        reddit.subreddits.search_by_name(subreddit, exact=True)
        subreddits.append(subreddit)
        if(input("Press Y for more subreddits and N to stop\n").lower() == "n"):
            test = True
    except prawcore.exceptions.NotFound:
        print(f"{subreddit} does not exist.")
        

# Reddit's sorting options
test = False
valid_sorting_options = ["hot", "top", "controversial", "best", "rising", "new"]
sorting_options = []
while(test!=True):
    try:
        sort_option = input("Enter which sorting method to use (hot, top, best, controversial, rising, new)\n").lower()
        if sort_option not in valid_sorting_options:
            raise ValueError(f"{sort_option} is not a valid sorting option.")
        sorting_options.append(sort_option)
        more_options = input("Press Y for more sorting options and N to stop\n").lower()
        if more_options.lower() == "n":
            test = True
    except ValueError as ve:
        print(f"ERROR: {ve}. Please try again.")


# Posts
test = False
while(test!=True):
    try:
        requested_posts = int(input("Enter amount of posts, between 0-1000, to grab on each request: \n"))
        if requested_posts < 0 or requested_posts > 1000:
            raise ValueError(f"{requested_posts} is out of range")
        else:
            test = True
    except ValueError as ve:
        print(f"ERROR: {ve}. Please try again.")

# Amount of posts to grab each request
posts = list()          # Holds the amount of posts grabbed
seen_ids = set()        # Holds the id's of posts already grabbed



# Delete all files in the Data folder
#for file_name in os.listdir("Data"):
#    os.remove(os.path.join("Data", file_name))

# Go through each subreddit
for sorting_option in sorting_options:
    print(f"\nStarted with subreddits sorted by {sorting_option}:")
    for subreddit_name in subreddits:
        # Attempts to grab the requested amount of posts
        cur_subreddit = getattr(reddit.subreddit(subreddit_name), sorting_option)(limit=requested_posts)
        print(f"\tStarted crawling subreddit: {subreddit_name}")
        print(f"\t\tAttempting to grab {requested_posts} posts")
        # Loop over each post in the current subreddit
        for post in cur_subreddit:
            # Check if post id is in the seen_ids set
            if post.id not in seen_ids:
                # Add post id to seen_ids set
                seen_ids.add(post.id)
                # Store the data in dictionary
                post_data = {
                    'subreddit': subreddit_name,    # Subreddit's name
                    'body': post.selftext,          # Body
                    'title': post.title,            # Title
                    'id': post.id,                  # Id
                    'score': post.score,            # Upvotes
                    'url': post.url,                # Image in post
                    'permalink': post.permalink,    # URL of post
                    'author': str(post.author),     # Username
                }
                # If a post contains a URL to an html page, get title of that page, and add title as an additional field of the post, 
                # that is, include it in the JSON of the post, so it becomes searchable in Part B.
                if post.url.endswith('.html'):
                    # Try to get the URL in the post
                    try:
                        # Send request to the post URL, skips if 4 seconds pass
                        response = requests.get(post.url, timeout=4)
                        # Parse using BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Add the URL's title to the post's data
                        post_data['page_title'] = soup.title.string
                    # Failed to get the URL
                    except Exception as e:
                        print('\t\tERROR: Failed to retrieve page title for {}: {}'.format(post.url, e))
                # Get the comments
                post.comments.replace_more(limit=0) #replacing None with 10
                
                post_data['comments'] = []
                # Loop through the comments
                print(f"\t\t\tAttempting to grab {len(post.comments)} comments") # was .list()
                for comment in post.comments: #was .list()
                    # Store the comment data in a dictionary
                    comment_data = {
                        'id': comment.id,
                        'body': comment.body,
                        'score': comment.score,
                        'author': str(comment.author),
                    }
                    # Check if the comment contains a URL
                    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', comment.body)
                    # Go through urls if it exists
                    if urls:
                        # Try to get the URL in the comment
                        try:
                            # Send request to the comment URL, skips if 4 seconds pass
                            response = requests.get(urls[0], timeout=4)
                            # Parse using BeautifulSoup
                            soup = BeautifulSoup(response.content, 'html.parser')
                            # Add the URL's title to the comment's data
                            comment_data['page_title'] = soup.title.string
                        # Failed to get the URL
                        except Exception as e:
                            print('\t\t\tERROR: Failed to retrieve page title for {}: {}'.format(urls[0], e))
                    # Append the current comment data to the post's dictionary
                    post_data['comments'].append(comment_data)
                # Append the current data to the current post
                posts.append(post_data)
            # Post already seen so move on through for loop
        print("\tFinished crawling subreddit:",subreddit_name)
    print(f"Finished crawling subreddits sorted by {sorting_option}")

print("\nStart writing to files...\n")
# Write to files until end of posts
# Go through each post
for post_data in posts:
    if len(json.dumps(data)) >= min_file_size:
        filename = f"Data/fileNum{file_number}.json"
        file_number += 1
        with open(filename,"w") as f:
            for d in data:
                json.dump(d, f)
                f.write('\n')
            f.flush()    
            file_size_mb = os.path.getsize(filename) / MB
            print(f"\t{filename} size: {file_size_mb:.2f} MB")
        # Clear the data list
        data = []
    # Append the current data to the data list
    data.append(post_data)
    #print(json.dumps(data))
    cur_data_size += len(json.dumps(post_data))
    # Write the remaining data into the last file

if (data):
    filename = f"Data/fileNum{file_number}.json"
    file_number += 1
    with open(filename, "w") as f:
        for d in data:
            json.dump(d, f)
            f.write('\n')
        f.flush()
        # Clear the data list
    data = []

print("\nDone writing to files...\n")
print(f"{(cur_data_size)/MB:.2f} MB of data stored in {file_number} files")


