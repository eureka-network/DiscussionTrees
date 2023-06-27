from pathlib import Path
from typing import Optional

import requests
from requests import Response
from bs4 import BeautifulSoup, ResultSet, Tag

import re

import sha3

import scrapy
from scrapy import Selector

from neo4j import GraphDatabase

SITEMAP_REQUEST_CONNECT_TIMEOUT = 5
SITEMAP_REQUEST_READ_TIMEOUT = 10

# TODO: sitemap is hardcoded for forum.safe.global, do this better


def get_urlsets_from_sitemap(forum_url: str) -> Optional[ResultSet]:
    """
    Fetches the sitemap XML from the specified forum URL and returns the 'urlset' elements.

    Args:
        forum_url (str): The URL of the forum.

    Returns:
        Optional[ResultSet]: The 'urlset' elements from the sitemap, or None if there was an error.
    """
    try:
        # set user-agent in headers, todo: update?
        headers: dict[str, str] = {'user-agent':
                                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

        # get sitemap all (1 of 1) posts
        response: Response = requests.get(forum_url + "/sitemap_1.xml",
                                          headers=headers,
                                          timeout=(SITEMAP_REQUEST_CONNECT_TIMEOUT, SITEMAP_REQUEST_READ_TIMEOUT))

        # # get sitemap recent posts
        # response = requests.get(forum_url + "/sitemap_recent.xml",
        #                     headers=headers,
        #                     timeout=(REQUEST_CONNECT_TIMEOUT, REQUEST_READ_TIMEOUT))

        # raise exception if status code is 400 or greater
        response.raise_for_status()

        xml_parser: BeautifulSoup = BeautifulSoup(response.text, "xml")

        urlsets: ResultSet[Tag] = xml_parser.select('urlset')

        return urlsets

    except requests.exceptions.RequestException as e:
        print(e)

        return None


def extract_title(response: Response):
    selector: Selector = Selector(response)
    title = selector.css('h1 a::text').get()
    return title


def extract_article_published_date(response: Response):
    date_published = response.xpath(
        '//meta[@property="article:published_time"]/@content').get()
    return date_published


def extract_posts(response: Response):
    # selector = Selector(response)
    posts = response.css('.topic-body.crawler-post')
    return posts


def make_safe_identifier(input_str: str) -> str:
    # Convert to lowercase
    s: str = input_str.lower()
    # Replace whitespaces with underscore
    s: str = s.replace(" ", "_")
    # Remove or replace special characters
    s: str = re.sub(r'\W', '', s)
    # Make sure it's not starting with a number
    if s[0].isdigit():
        s: str = "_" + s
    # TODO: possibly check for max length if neo4j requires it
    return s

# return first four bytes of sha3 hash of unique identifier string


def get_identifier(identifier_string: str):
    k = sha3.keccak_256()
    k.update(identifier_string.encode('utf-8'))
    digest = k.digest()
    return digest[:4]


def extract_core_from_post(post):
    author = post.css("span.creator span::text").get()
    post_content = post.css("div[class='post']").get()
    post_datePublished = post.css(
        'time[itemprop="datePublished"]::attr(datetime)').get()
    post_position = post.css('span[itemprop="position"]::text').get()

    return {'author': author,
            'content': post_content,
            'datePublished': post_datePublished,
            'position': post_position}


def extract_core_from_reply(reply):
    author = reply.css("span.creator span::text").get()
    reply_content = reply.css("div[class='post-reply']").get()
    reply_datePublished = reply.css(
        'time[itemprop="datePublished"]::attr(datetime)').get()
    reply_position = reply.css('span[itemprop="position"]::text').get()

    return {'author': author,
            'content': reply_content,
            'datePublished': reply_datePublished,
            'position': reply_position}


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

        # connect to neo4j over Bolt
        neo4j = Neo4jService('neo4j://localhost:7687',
                             'neo4j', 'IlGOk+9SoTmmeQ==')

        # get title and date thread was published / started for a thread identifier
        thread_title = extract_title(response)
        date_published = extract_article_published_date(response)
        cleaned_title = make_safe_identifier(thread_title)
        thread_unique_string = f"ID: {date_published}-{cleaned_title}"
        thread_id = get_identifier(thread_unique_string).hex()
        thread_core = {'title': thread_title,
                       'date_published': date_published}

        # get posts
        posts = extract_posts(response)

        # make a dictionary of all the posts and their properties
        post_positions_dict = {}

        for post in posts:
            post_core = extract_core_from_post(post)
            if post_core['author'] is None:
                # TODO: catch this edge case appropriately
                continue
            post_id = f"{thread_id}-{post_core['position']}"
            post_positions_dict[post_core['position']] = post_id
            neo4j.create_post(post_id, post_core, thread_id, thread_core)

        # run over the dictionary to look up subsequent pairs
        for position, post_id in post_positions_dict.items():
            preceding_post_id = post_positions_dict.get(str(int(position)-1))
            if preceding_post_id:
                neo4j.follow_post(preceding_post_id, post_id)

        # Get the next page link
        next_page = response.css('a[rel="next"]::attr(href)').get()

        # If there is a next page, follow it
        if next_page is not None:
            print(f"FLAG: DEBUG next_page content = {next_page}")
            try:
                yield scrapy.Request(response.urljoin(
                    next_page), callback=self.parse)
            # yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
            except ValueError as e:
                print(
                    f"Failed to create request for next page: {e}")


class Neo4jService(object):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_post(self, post_id, post_core, thread_id, thread_core):
        with self._driver.session() as session:
            # The query creates a User, a Post, and a Thread if they don't already exist
            # and creates relationships between them
            query = """
            MERGE (u:User {name: $username})
            MERGE (p:Post {id: $post_id})
            SET p.content = $post_content, p.date = $post_date, p.position = $post_position
            MERGE (t:Thread {id: $thread_id})
            SET t.title = $thread_title, t.datePublished = $thread_datePublished
            MERGE (u)-[:POSTED]->(p)
            MERGE (p)-[:IN]->(t)
            """
            session.run(query,
                        username=post_core['author'],
                        post_id=post_id,
                        post_content=post_core['content'],
                        post_date=post_core['datePublished'],
                        post_position=post_core["position"],
                        thread_id=thread_id,
                        thread_title=thread_core['title'],
                        thread_datePublished=thread_core['date_published'])

    def follow_post(self, previous_post_id, current_post_id):
        with self._driver.session() as session:
            query = """
            MATCH (previousPost:Post {id: $previous_post_id})
            MATCH (currentPost:Post {id: $current_post_id})
            MERGE (currentPost)-[:FOLLOWS]->(previousPost)
            """
            session.run(query, previous_post_id=previous_post_id,
                        current_post_id=current_post_id)

    def replies(self, reply_id, thread_id):
        with self._driver.session() as session:
            query = """
            MERGE (r:Reply {reply: $reply_id})
            MATCH (t:Thread {id: $thread_id})
            Merge (t)-[:FOLLOWS]->(r)
            """
            session.run(query, reply_id, thread_id)

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
