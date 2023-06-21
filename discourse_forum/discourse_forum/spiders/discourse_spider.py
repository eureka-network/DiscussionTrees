from pathlib import Path

import requests
from bs4 import BeautifulSoup

import re

import scrapy
from scrapy import Selector

from neo4j import GraphDatabase

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

def extract_article_published_date(response):
    date_published = response.xpath('//meta[@property="article:published_time"]/@content').get()
    return date_published

def extract_posts(response):
    # selector = Selector(response)
    posts = response.css('.topic-body.crawler-post')
    return posts

def make_safe_identifier(input_str):
    # Convert to lowercase
    s = input_str.lower()
    # Replace whitespaces with underscore
    s = s.replace(" ", "_")
    # Remove or replace special characters
    s = re.sub(r'\W', '', s)
    # Make sure it's not starting with a number
    if s[0].isdigit():
        s = "_" + s
    # TODO: possibly check for max length if neo4j requires it
    return s

def extract_core_from_post(post):
    author = post.css("span.creator span::text").get()
    post_content = post.css("div[class='post']").get()
    return {'author': author, 'post_content': post_content}

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
        # a thread page with posts

        # page = response.url.split("/")[-2]
        # filename = f"discourse-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")

        # connect to neo4j over Bolt
        # neo4j = Neo4jService('neo4j://localhost:7687', 'neo4j', 'IlGOk+9SoTmmeQ==')

        # get title and date thread was published / started for a thread identifier
        thread_title = extract_title(response)
        date_published = extract_article_published_date(response)
        cleaned_title = make_safe_identifier(thread_title)
        print(f"ID: {date_published}-{cleaned_title}")

        # get posts
        posts = extract_posts(response)
        for post in posts:
            post_core = extract_core_from_post(post)
            print(f"author: {post_core['author']}")
            print(f"post_content: {post_core['post_content']}")
        
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

class Neo4jService(object):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_post(self, username, post, thread):
        with self._driver.session() as session:
            # The query creates a User, a Post and a Thread if they don't already exist
            # and creates relationships between them
            query = """"
            MERGE (u:User (name: $username))
            MERGE (p:Post (id: $post_id))
            SET p.content = $post_content, p.date = $post_date
            MERGE (t:Thread (id: $thread_id))
            SET t.title = $thread_title
            MERGE (u)-[:POSTED]->(p)
            MERGE (p)-[:IN]->(t)
            """
            session.run(query,
                        username=username,
                        post_id=post['id'], post_content=post['content'], post_date=post['date'],
                        thread_id=thread['id'], thread_title=thread['title'])



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