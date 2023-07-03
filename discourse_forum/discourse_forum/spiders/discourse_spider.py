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

# # Note: upon paginatation, the date published is the date of the first post on the page... wtf Discourse?
# def extract_article_published_date(response: Response):
#     date_published = response.xpath(
#         '//meta[@property="article:published_time"]/@content').get()
#     return date_published

# Discourse puts a unique identifier in the URL for easy lookup. Get it.
def extract_identifier(url):
    """Extracts unique thread identifier from URL."""
    try:
        return re.search(r"/(\d+)(\?|$)", url).group(1)
    except AttributeError:
        return "No identifier found in URL."

def extract_posts(response: Response):
    # selector = Selector(response)
    posts = response.css('.topic-body.crawler-post')
    return posts


def extract_block_quotes(response: Response):
    block_quotes = response.css('blockquote')
    return block_quotes


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


def extract_block_quotes_from_post(post):
    quotes = post.css('aside.quote')
    output = []
    for quote in quotes:
        quote_content = quote.css('blockquote p::text').get()
        data_username = quote.attrib.get('data-username')
        data_post = quote.attrib.get('data-post')
        data_topic = quote.attrib.get('data-topic')

        if quote_content is None:
            # ignore quotes without content
            continue

        output.append({
            'quote_content': quote_content,
            'data_username': data_username,
            'data_post': data_post,
            'data_topic': data_topic
        })
    return output


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
                    yield scrapy.Request(url=location.text, callback=self.parse)

    def parse(self, response):
        # a thread page with posts

        page = response.url.split("/")[-2]
        filename = f"discourse-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        # connect to neo4j over Bolt
        neo4j = Neo4jService('neo4j://localhost:7687',
                             'neo4j', 'IlGOk+9SoTmmeQ==')

        # get title and date thread was published / started for a thread identifier
        thread_title = extract_title(response)
        thread_discourse_id = extract_identifier(response.url)
        cleaned_title = make_safe_identifier(thread_title)
        thread_unique_string = f"ID: SAFEFORUM-{thread_discourse_id}-{cleaned_title}"
        thread_id = get_identifier(thread_unique_string).hex()
        thread_core = {'title': thread_title,
                       'discourse_id': thread_discourse_id}

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
            # get quotes
            block_quotes = extract_block_quotes_from_post(post)
            neo4j.block_quotes(
                post_core['author'], post_id, post_core['content'], block_quotes)

        # run over the dictionary to look up subsequent pairs
        for position, post_id in post_positions_dict.items():
            preceding_post_id = post_positions_dict.get(str(int(position)-1))
            if preceding_post_id:
                neo4j.follow_post(preceding_post_id, post_id)

        # Get the next page link
        next_page = response.css('a[rel="next"]::attr(href)').get()

        # If there is a next page, follow it
        if next_page is not None:
            try:
                yield scrapy.Request(response.urljoin(
                    next_page), callback=self.parse)
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
            SET t.title = $thread_title, t.discourse_id = $thread_discourse_id
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
                        thread_discourse_id=thread_core['discourse_id'])

    def follow_post(self, previous_post_id, current_post_id):
        with self._driver.session() as session:
            query = """
            MATCH (previousPost:Post {id: $previous_post_id})
            MATCH (currentPost:Post {id: $current_post_id})
            MERGE (currentPost)-[:FOLLOWS]->(previousPost)
            """
            session.run(query, previous_post_id=previous_post_id,
                        current_post_id=current_post_id)

    def block_quotes(self, username, post_id, post_content, block_quotes):
        for quote in block_quotes:
            block_quote_username = quote['data_username']
            block_quote_content = quote['quote_content']
            block_quote_data_post = quote['data_post']
            block_quote_data_topic = quote['data_topic']

            with self._driver.session() as session:
                query = """
                MATCH (u:User {name: $username})
                MATCH (bu:User {name: $block_quote_username})
                MATCH (p:Post {id: $post_id, content: $post_content})
                MERGE (q:Quote {content: $block_quote_content})
                MERGE (u)-[:POSTED]->(p)
                MERGE (bu)-[:POSTED]->(q)
                MERGE (q)-[:QUOTE]->(p)
                MERGE (p)-[:IN_TOPIC]->(:DataPost {topic: $block_quote_data_post})
                MERGE (q)-[:IN_TOPIC]->(:DataTopic {topic: $block_quote_data_topic})
                """
                session.run(query,
                            username=username,
                            block_quote_username=block_quote_username,
                            post_id=post_id,
                            post_content=post_content,
                            block_quote_content=block_quote_content,
                            block_quote_data_post=block_quote_data_post,
                            block_quote_data_topic=block_quote_data_topic)
