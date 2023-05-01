import praw

reddit = praw.Reddit(client_id='BVN377aTHCSupxRmvJxRcA',
                     client_secret='Nd-gzmX0P8vkdF8YGG0ebZaU26Z8kQ',
                     user_agent='CS172:SPR23GROUP21:v0.1 (by u/wecrawling)',
                     username='wecrawling',
                     password='crawling21')

ucr = reddit.subreddit("ucr").hot(limit=10)
for post in ucr:
    print(post.selftext) # body
    print(post.title) # title
    print(post.id) # id
    print(post.score) # upvotes
    print(post.url) # image in post
    print(post.permalink) # url of post

post.comments.replace_more(limit=None)
for comment in post.comments.list():
    print(comment.body)
