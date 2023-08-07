"""
Graph store connects to a neo4j instance to store the knowledge base and the constructed worlds.
"""

# todo: restructure repo start the package at the top level of repository

# Import the neo4j db reader
from .reader import Reader
# Import the graph class wrapping around neo4j connection
from .graph import Graph

package_version = "0.1"
