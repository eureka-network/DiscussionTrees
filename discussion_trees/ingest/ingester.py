import os
import hashlib

from discussion_trees.graph_store import Graph
from discussion_trees.document_store import Document

def calculate_sha256(file_path):
    """Calculate the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        # Reading in chunks to handle large files
        for chunk in iter(lambda: file.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def filepath_to_document_name(filepath):
    """Convert a filepath to a document name by extracting filename."""
    return os.path.splitext(os.path.basename(filepath))[0]

class DocumentIngester:
    def __init__(self, graph):
        self._graph = graph
    
    def ingest(self, document_path):
        """Ingest a .txt document into the graph store,
           treating each line as a unit."""
        
        # Calculate the document's SHA256 hash
        document_hash = calculate_sha256(document_path)
        document_name = filepath_to_document_name(document_path)
        document_identifier = f"{document_name}_{document_hash[:8]}"

        print(f"Document name: '{document_name}'") 
        print(f"Document hash: '{document_hash}'")
        print(f"Document identifier: '{document_identifier}'")

        # Check if the document already exists in the graph store
        document = Document(self._graph, document_identifier, readOnly=True)
        if document.exists():
            print(f"Document '{document_identifier}' already exists in the graph store")
            return
        else:
            print(f"Document '{document_identifier}' does not exist in the graph store")

        # with open(document_path, 'r') as txt_document:
        #     lines = txt_document.readlines()
        #     for line in lines:
        #         line = line.strip() # remove leading and trailing whitespace
        #         if line: # avoid adding empty lines
        #             pass # continue here
class Ingester:
    def __init__(self, config):
        print("Hello, ingester !")
        self._config = config
        # graph
        self._graph = Graph(
            self._config.neo4j_credentials[0], # uri
            self._config.neo4j_credentials[1], # user
            self._config.neo4j_credentials[2]) # password


    def ingest(self):
        # Ensure the knowledge_base_dir points to a valid directory
        if not os.path.isdir(self._config.knowledge_base_dir):
            raise ValueError(f"'{self._config.knowledge_base_dir}' is not a valid directory!")

        # Build the list of documents in the knowledge base directory
        documents = []
        
        # Walk through the knowledge_base_dir and its subdirectories
        for dirpath, _, filenames in os.walk(self._config.knowledge_base_dir):
            # Filter only the *.txt and *.pdf files
            for filename in filenames:
                if filename.endswith('.txt') or filename.endswith('.pdf'):
                    full_path = os.path.join(dirpath, filename)
                    documents.append(full_path)

        print(f"Found {len(documents)} documents in the knowledge base directory")
        print(f"First 10 documents: {documents[:10]}")

        # If the ingester_task_document is not None, use it to select the specific document
        if self._config.ingester_task_document is not None:
            specific_document = os.path.join(self._config.knowledge_base_dir, self._config.ingester_task_document)
            
            if specific_document not in documents:
                raise ValueError(f"INGESTER_TASK_DOCUMENT '{specific_document}' was not found in the knowledge base directory")
            else:
                print(f"Using INGESTER_TASK_DOCUMENT '{specific_document}'")
                documents = [specific_document]

        # Ingest the documents
        document_ingester = DocumentIngester(self._graph)
        for document in documents:
            print(f"Ingesting document '{document}'")
            document_ingester.ingest(document)

        pass # continue here