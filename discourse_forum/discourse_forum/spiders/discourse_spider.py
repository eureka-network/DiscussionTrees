from pathlib import Path

import requests
from bs4 import BeautifulSoup

import scrapy
from scrapy import Selector

SITEMAP_REQUEST_CONNECT_TIMEOUT = 5
SITEMAP_REQUEST_READ_TIMEOUT = 10

# TODO: sitemap is hardcoded for forum.safe.global, do this better
def get_urlsets_from_sitemap(forum_url):
    # try to get the sitemap
    try:
        # set user-agent in headers, todo: update?
        headers = {'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

        # get sitemap all (1 of 1) posts
        response = requests.get(forum_url + "/sitemap_1.xml",
                            headers=headers,
                            timeout=(SITEMAP_REQUEST_CONNECT_TIMEOUT, SITEMAP_REQUEST_READ_TIMEOUT))

        # # get sitemap recent posts
        # response = requests.get(forum_url + "/sitemap_recent.xml",
        #                     headers=headers,
        #                     timeout=(REQUEST_CONNECT_TIMEOUT, REQUEST_READ_TIMEOUT))

        # raise exception if status code is 400 or greater
        response.raise_for_status()

        xml_parser = BeautifulSoup(response.text, "xml")

        urlsets = xml_parser.select('urlset')

        return urlsets

    except requests.exceptions.RequestException as e:
        print(e)
        
        return None

def extract_title(response):
    selector = Selector(response)
    title = selector.css('h1 a::text').get()
    return title

def extract_posts(response):
    selector = Selector(response)
    posts = selector.css('.topic-body.crawler-post').getall()
    return posts

class DiscourseSpider(scrapy.Spider):
    name = "discourse"

    def start_requests(self):
        forums = [
            "https://forum.safe.global",
        ]
        for forumurl in forums:

            # get urlsets from sitemap
            urlsets = get_urlsets_from_sitemap(forumurl)

            for urlset in urlsets:
                locations = urlset.select('url loc')
                for location in locations:
                    print(location.text)
                    yield scrapy.Request(url=location.text, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        # filename = f"discourse-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")

        # get title
        title = extract_title(response)
        print(f"title: {title}")

        # get posts
        posts = extract_posts(response)
        for post in posts:
            print(f"post: {post}")
        
        # # Get the list of topics
        # topics = response.css('.topic-body.crawler-post').getall()
        # print(f"topics: {topics}")

        # # Get the topic title and link
        # for topic in topics:
        #     print(f"topic: {topic}")
        #     topic
        #     # topic_title = topic.css('a.title::text').get()
        #     # topic_link = response.urljoin(topic.css('a.title::attr(href)').get())

        #     # Get the topic content
        #     yield scrapy.Request(topic_link, callback=self.parse_topic, meta={'topic_title': topic_title})

        # # Get the next page link
        # next_page = response.css('a.next::attr(href)').get()

        # # If there is a next page, follow it
        # if next_page:
        #     yield scrapy.Request(next_page, callback=self.parse)



    # name = 'discourse'
    # allowed_domains = ['discourse.example.com']
    # start_urls = ['https://discourse.example.com/']

    # def parse(self, response):
    #     # Get the list of topics
    #     topics = response.css('tr.topic-list-item')

    #     # Get the topic title and link
    #     for topic in topics:
    #         topic_title = topic.css('a.title::text').get()
    #         topic_link = response.urljoin(topic.css('a.title::attr(href)').get())

    #         # Get the topic content
    #         yield scrapy.Request(topic_link, callback=self.parse_topic, meta={'topic_title': topic_title})

    #     # Get the next page link
    #     next_page = response.css('a.next::attr(href)').get()

    #     # If there is a next page, follow it
    #     if next_page:
    #         yield scrapy.Request(next_page, callback=self.parse)

    # def parse_topic(self, response):
    #     # Get the topic title and content
    #     topic_title = response.meta['topic_title']
    #     topic_content = response.css('div.topic-body').get()

    #     # Save the topic content to a file
    #     Path('data').mkdir(parents=True, exist_ok=True)
    #     with open(f'data/{topic_title}.html', 'w') as f:
    #         f.write(topic_content)