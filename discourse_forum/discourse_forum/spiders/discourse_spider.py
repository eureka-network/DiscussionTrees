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
import time

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


def get_post_id(thread_id: str, post_position: int):
    return f"{thread_id}-{post_position}"


def get_position_from_post_id(post_id: str):
    return int(post_id.split('-')[1])


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

        # page = response.url.split("/")[-2]
        # filename = f"discourse-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")

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
            post_id = get_post_id(thread_id, post_core['position'])
            post_positions_dict[post_core['position']] = post_id
            neo4j.create_post(post_id, post_core, thread_id, thread_core)

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
        else:
            # if there is no next_page to follow, we simply
            # add the FOLLOWS relationship:
            positions = neo4j.get_all_post_positions(thread_id)
            post_count = len(positions)

            if post_count >= 2:
                for i in range(post_count - 1):
                    previous_position = positions[i]
                    current_position = positions[i + 1]

                    previous_post_id = get_post_id(
                        thread_id, previous_position)
                    current_post_id = get_post_id(thread_id, current_position)

                    neo4j.follow_post(previous_post_id, current_post_id)

        # close the neo4j db connection
        neo4j.close()


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
            self.close()

    def follow_post(self, previous_post_id, current_post_id):
        with self._driver.session() as session:
            query = """
            MATCH (previousPost:Post {id: $previous_post_id})
            MATCH (currentPost:Post {id: $current_post_id})
            MERGE (currentPost)-[:FOLLOWS]->(previousPost)
            """
            session.run(query, previous_post_id=previous_post_id,
                        current_post_id=current_post_id)
        self.close()

    def get_all_post_positions(self, thread_id: int) -> list[int]:
        """Returns a list of all post positions from a thread."""
        with self._driver.session() as session:
            query = """
                MATCH (p:Post)-[:IN]->(t:Thread {id: $thread_id})
                WITH p
                ORDER BY p.position ASC
                RETURN p.position as position
            """
            result = session.run(query, thread_id=thread_id)
            positions = [int(record['position']) for record in result]
            positions.sort()
            return positions
