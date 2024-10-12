#!/usr/bin/env python
# coding: utf-8

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from db import Database


class FeedNotFoundException(BaseException):
    pass


class BadURLException(BaseException):
    pass


def remove_url_params(url):
    return urljoin(url, urlparse(url).path)


def create_youtube_embed(video_feed_url):
    """Convert Youtube video URL from RSS feed
    into a Youtube embed with iframe."""
    video_id = re.findall(r"youtube.com/v/(.*)\?", video_feed_url)
    return f'<iframe width=1020 height=600 src="https://youtube.com/embed/{video_id[0]}"></iframe>'


def process_youtube_feed(feed_url):
    """Processes a given RSS feed for a Youtube channel and
    injects video embed, title and description into the feed's content
    so it can be viewable by feed readers that don't support media attributes."""

    # Get original feed
    response = requests.get(feed_url)
    if not response.ok:
        raise FeedNotFoundException(f"Feed at {feed_url} not found.")

    feed = BeautifulSoup(response.text, "xml")

    # Add content with embedded Youtube video + title & description
    # to each entry
    entries = feed.find_all("entry")

    for entry in entries:
        media_content = entry.find("media:content")
        youtube_url = media_content["url"]

        embed = create_youtube_embed(youtube_url)
        title = entry.find("media:title").text
        description = entry.find("media:description").text
        html = f"<![CDATA[{embed} <h1>{title}</h1>]]>"

        entry.append(
            BeautifulSoup(f"<content type='html'>{html}</content>", "html.parser")
        )

    return feed


def create_github_diff(commit_url, db):
    link = commit_url.replace("github.com/", "api.github.com/repos/")
    link = link.replace("/commit/", "/commits/")

    if result := db.query_url(link):
        print(f"Hit cache for {link}")
        _, diff = result[0]
    else:
        print(f"No cache hit")
        diff_response = requests.get(
            link, headers={"Accept": "application/vnd.github.diff"}
        )
        diff = diff_response.text
        db.add_url(link, diff)

    return diff


def create_github_md_html(commit_url, db):
    link = commit_url.replace("github.com/", "api.github.com/repos/")
    link = link.replace("/commit/", "/commits/")

    if result := db.query_url(link):
        print(f"Hit cache for {link}")
        _, html = result[0]
    else:
        print(f"No cache hit")
        commit_response = requests.get(link).json()

        files = [
            file
            for file in commit_response.get("files", [])
            if file["filename"].endswith("md")
            and file["filename"].lower() != "readme.md"
        ]

        html = ""
        if files:
            for file in files:
                api_url = remove_url_params(file["contents_url"])
                html_response = requests.get(
                    api_url, headers={"Accept": "application/vnd.github.html"}
                )
                html += html_response.text
        else:
            html = "No non-readme Markdown changes."

        db.add_url(link, html)

    return html


def process_github_feed(github_url):
    """
    Adds commit diff as content to each entry for GitHub commit atom feeds
    """

    db = Database()

    response = requests.get(github_url)
    if not response.ok:
        raise FeedNotFoundException()

    feed = BeautifulSoup(response.text, "xml")

    entries = feed.find_all("entry")
    for entry in entries:
        link = entry.find("link")["href"]
        html = create_github_md_html(link, db)

        entry.find("content").decompose()
        entry.append(
            BeautifulSoup(
                f'<content type="html"><![CDATA[{html}]]></content>',
                "html.parser",
            )
        )
    return feed
