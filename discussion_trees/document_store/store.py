from discussion_trees.graph_store import Graph

from .state import DocumentState

class Store:
    def __init__(self, graph: Graph, session_id: str):
        self._document_state = DocumentState(session_id)
        self._session_id = session_id
        self._graph = graph
        self._reader = self._graph.new_reader()
        self._writer = self._graph.new_writer()
        self._session_list = []
        self._segment_store = {}

    # todo: later segment documents for distributing the work load
    def load_documents(self, segment: str = None):
        if segment is not None:
            raise NotImplementedError("Segmenting documents not implemented yet")
        # simply get all documents
        all_records = self._reader.get_all_documents()
        for record in all_records:
            self._segment_store[record["identifier"]] = {
                "name": record["name"],
                "cached": False,
                "flushed": False,
                }
        self._retrieve_all_session_documents()
            
    def include_all_documents_in_session(self):
        """Mark all documents as part of the session."""
        for identifier, cache_entry in self._segment_store.items():
            if not identifier in self._session_list:
                print(f"Marking document {identifier} as part of session ({self._session_id})")
                cache_entry["flushed"] = False
                self._session_list.append(identifier)
        self._mark_documents_for_session()

    def _retrieve_all_session_documents(self):
        """Retrieve all documents that are part of the session."""
        all_sessioned_records = self._reader.get_all_session_documents(self._session_id)
        print(f"Retrieved {len(all_sessioned_records)} documents for session {self._session_id} from graph store")
        for record in all_sessioned_records:
            assert record["identifier"] in self._segment_store, f"Document {record['identifier']} expected in cache, but failed"
            if record["identifier"] in self._session_list:
                # don't append twice the same session
                continue
            else:
                self._session_list.append(record["identifier"])
        print(f"Session {self._session_id} contains {len(self._session_list)} documents")

    def _mark_documents_for_session(self):
        """Mark all documents that are part of the session with the session controller."""
        print(f"session list contains: {self._session_list}")
        for identifier in self._session_list:
            cache_entry = self._segment_store[identifier]
            if not cache_entry["flushed"]:
                self._writer.merge_session_controller(self._session_id, identifier)
                self._flush_document(identifier)
                cache_entry["flushed"] = True
                print(f"Marked document {identifier} as part of session {self._session_id}")

    def _flush_document(self, identifier: str):
        """Flush a document to the graph store."""
        cache_entry = self._segment_store[identifier]
        if not cache_entry["flushed"]:
            print(f"TODO: flush document to graph store")
            pass