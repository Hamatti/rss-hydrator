from flask import Flask, Response, request
from hydrator import process_github_feed, process_youtube_feed

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello feed"


@app.route("/<path:feed_url>")
def process(feed_url):
    if "github.com" in feed_url:
        new_feed = process_github_feed(f"https://{feed_url}")
        return Response(str(new_feed), mimetype="text/xml")
    if "youtube.com" in feed_url:
        channel_id = request.args.get("channel_id")
        new_feed = process_youtube_feed(f"https://{feed_url}?channel_id={channel_id}")
        return Response(str(new_feed), mimetype="text/xml")

    return feed_url


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
