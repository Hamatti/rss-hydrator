from flask import Flask
from rss_proxy import process_github_feed, process_youtube_feed

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello feed'

@app.route('/<path:feed_url>')
def process(feed_url):
    if 'github.com' in feed_url:
        new_feed = process_github_feed(f'https://{feed_url}')
        return new_feed.prettify()
    if 'youtube.com' in feed_url:
        new_feed = process_youtube_feed(f'https://{feed_url}')
        return new_feed.prettify()

    return feed_url 


app.run(host='0.0.0.0', port='9898')
