#!/usr/bin/env python
# coding: utf-8

import re
import requests
from bs4 import BeautifulSoup
import urllib


YOUTUBE_RSS_URL = 'https://www.youtube.com/feeds/videos.xml?playlist_id=PLd97ZOKZpSMbaOJcTzZdy-Ia72o0J7SeX'
YOUTUBE_VIDEO_URL = 'https://www.youtube.com/v/G0A6Tx0JYn0?version=3'

AREENA_RSS_URL = 'https://areena-feeds.yle.fi/areena/v1/series/1-62829974.rss'


class FeedNotFoundException:
    pass

class BadURLException:
    pass


def create_youtube_embed(video_feed_url):
    video_id = re.findall(r'youtube.com/v/(.*)\?', video_feed_url)
    return f'<iframe src="https://youtube.com/embed/{video_id[0]}"></iframe>'

def process_youtube_feed(feed_url):
    """Processes a given RSS feed for a Youtube channel and 
    injects video embed, title and description into the feed's content
    so it can be viewable by feed readers that don't support media attributes."""
    response = requests.get(feed_url)
    if not resp.ok:
        raise FeedNotFoundException(f'Feed at {feed_url} could not be requested')

    feed = BeautifulSoup(resp.text, 'xml')
    entries = feed.find_all('entry')
    for entry in entries:
        media_content = entry.find('media:content')
        youtube_url = media_content['url']
        if not 'youtube' in youtube_url:
            raise BadURLException(f'"youtube" not found in {youtube_url}')
        embed = create_youtube_embed(youtube_url)
        title = entry.find('media:title').encode_contents()
        description = entry.find('media:description').text
        html = f'{embed} <h1>{title}</h1> <pre>{description}</pre>'
        entry.append(BeautifulSoup(f'<content>{html}</content>', 'html.parser'))
        
    return feed

def process_areena_feed(feed_url):
    response = requests.get(feed_url)
    if not response.ok:
        raise FeedNotFoundException()

    feed = BeautifulSoup(response.text, 'xml')
    items = feed.find_all('item')
    for item in items:
        link = item.find('link').string
        embed = BeautifulSoup(f'<content><faux-embed src="{link}"></faux-embed></content>', 'html.parser') #  TODO: figure out the right embed format
        item.append(embed)
    return feed

def process_github_feed(github_url):
    """
    Adds commit diff as content to each entry for GitHub commit atom feeds
    """

    response = requests.get(github_url)
    if not response.ok:
        raise FeedNotFoundException()

    feed = BeautifulSoup(response.text, 'xml')
    entries = feed.find_all('entry')
    for entry in entries[:2]:
        link = entry.find('link')['href']
        link = link.replace('github.com/', 'api.github.com/repos/')
        link = link.replace('/commit/', '/commits/')

        diff_response = requests.get(link, headers={'Accept': 'application/vnd.github.diff' })
        diff = diff_response.text

        content = entry.find('content').decompose()
        entry.append(BeautifulSoup(f'<content type="html"><pre>{diff}</pre></content>', 'html.parser'))
    return feed


