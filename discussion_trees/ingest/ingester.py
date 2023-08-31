import os
import cbor2
# import hashlib

from discussion_trees.graph_store import Graph
from discussion_trees.document_store import Document, UnitData

from discussion_trees.hasher import calculate_sha256_from_file, calculate_sha256

# todo: remove once confirmed
# def calculate_sha256_from_file(file_path):
#     """Calculate the SHA256 hash of a file."""
#     sha256 = hashlib.sha256()
#     with open(file_path, 'rb') as file:
#         # Reading in chunks to handle large files
#         for chunk in iter(lambda: file.read(4096), b''):
#             sha256.update(chunk)
#     return sha256.hexdigest()


# def calculate_sha256(data):
#     """Calculate the SHA256 hash of a string or bytes."""
#     sha256 = hashlib.sha256()
    
#     if isinstance(data, str):
#         sha256.update(data.encode('utf-8'))
#     elif isinstance(data, bytes):
#         sha256.update(data)
#     else:
#         raise TypeError("Expected data to be of type str or bytes")
    
#     return sha256.hexdigest()


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
        document_hash = calculate_sha256_from_file(document_path)
        document_name = filepath_to_document_name(document_path)
        document_identifier = f"{document_name}_{document_hash[:8]}"

        # Check if the document already exists in the graph store
        document = Document(self._graph, document_identifier, readOnly=True)
        if document.exists():
            print(f"Document '{document_identifier}' already exists in the graph store")
            # todo: check if the document has changed, or all units have been ingested
            print(f"Skipping document '{document_identifier}'")
            return
        else:
            print(f"Document '{document_identifier}' does not exist in the graph store")
        document.make_writable()
        document.create(document_name, document_hash)

        # read the document from file, and store in an ordered list of UnitData
        units_data  = []
        position = 0
        with open(document_path, 'r') as txt_document:
            lines = txt_document.readlines()
            for line in lines:
                content = line.strip() # remove leading and trailing whitespace
                if content: # avoid adding empty lines
                    position += 1
                    data = {
                        "position": position,
                        "content": content,
                        "document_hash": document_hash,
                    }
                    encoded_data = cbor2.dumps(data)
                    digest = calculate_sha256(encoded_data)
                    units_data.append(UnitData(position, content, digest))
        
        document.merge(units_data, autoFlush=True)
        del document # explicitly dereference document

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
            # Check if the current directory is/has "ignore" in its path,
            # then ignore this directory
            if 'ignore' in dirpath.split(os.path.sep):
                print(f"Ignoring directory '{dirpath}'")
                continue 
            
            # Filter only the *.txt and *.md files 
            # use a pre-processor to convert pdf to markdown first
            for filename in filenames:
                if filename.endswith('.txt') or filename.endswith('.md'):
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