# RSS Hydrator Proxy

A micro web service that turns RSS feeds into versions with more content.

## Supported feeds

### GitHub commits feed

GitHub provides a commit feed at `https://github.com/{owner}/{repo}/commits.atom` but the feed only contains the commit message. That's enough if you use it as a way to see when new commits happen but I mainly follow TIL (Today I learned) repositories where people document what they've learned.

With those repositories, I'm more interested in the commit diff itself and not the commit message.

Feeding in a GitHub feed URL (without the `https://` part), the service will create a new feed where it shows the diff of the commit directly in the content body, thus making these commits more useful in an RSS feed.

### Youtube feed

Youtube's RSS feed (found at `https://www.youtube.com/feeds/videos.xml?channel_id={ID}`) uses `<media:content>` elements that not all RSS readers support.

This hydrator will embed the video and add the title and description directly into a `<content>` element to make it better for those RSS readers that don't support them.

## Usage

Add the feed URL (without the `https://` part) at the end of this service's domain and use that as the feed URL you provide to your feed reader.

## AWS & Docker stuff

I mainly followed [this guide](https://aws.amazon.com/tutorials/serve-a-flask-app/).

### Docker

```shell
docker build -t hydrator
docker run -p 5000:5000 hydrator
```

### AWS

```shell
aws lightsail create-container-service --service-name hydrator-service --power small --scale 1
aws lightsail push-container-image --service-name hydrator-service --label hydrator-container --image hydrator
aws lightsail create-container-service-deployment --service-name hydrator-service --containers file://containers.json --public-endpoint file://public-endpoint.json
```

If I want to delete it, run

```shell
aws lightsail delete-container-service --service-name hydrator-service
```
