from neo4j import GraphDatabase
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

try:
    with driver.session() as session:
        session.run("MATCH (n) RETURN n LIMIT 1")
    print("Connected successfully!")
    sys.exit(0)
except Exception as e:
    sys.exit(1)
