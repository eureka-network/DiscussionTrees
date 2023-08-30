from discussion_trees.graph_store import Graph

from .document import Document
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
    def load_document_ids(self, segment: str = None):
        """Load all document identifiers from the graph store into memory segment store."""
        if segment is not None:
            raise NotImplementedError("Segmenting documents not implemented yet")
        # simply get all documents
        all_records = self._reader.get_all_documents()
        for record in all_records:
            self._segment_store[record["identifier"]] = {
                "name": record["name"],
                "cached": False,
                "flushed": True,
                "document": None,
                "state": {},
                }
        self._retrieve_all_session_documents()
        self._load_state_for_session_documents()
    
    def get_document(self, identifier: str):   
        """Load a document into memory segment store."""
        assert identifier in self._segment_store, f"Document {identifier} expected in segment store, but failed"
        if self._segment_store[identifier]["document"] is None:
            print(f"Loading document {identifier} into segment store")
            document = Document(self._graph, identifier, readOnly=False)
            # by asserting .exists() we also cache the document properties and unit digest list
            assert document.exists(), f"Document {identifier} expected to exist in graph store, but failed"
            self._segment_store[identifier]["document"] = document
            self._segment_store[identifier]["cached"] = True
            return document
        else:
            print(f"Document {identifier} already cached in segment store")
            assert isinstance(self._segment_store[identifier]["document"], Document), f"Document {identifier} expected to be a Document instance, but failed"
            assert self._segment_store[identifier]["document"].exists(), f"Document {identifier} expected to exist in graph store, but failed"
            assert self._segment_store[identifier]["cached"], f"Document {identifier} expected to be cached, but failed"
            return self._segment_store[identifier]["document"]

    def include_all_documents_in_session(self):
        """Mark all documents as part of the session."""
        for identifier, cache_entry in self._segment_store.items():
            if not identifier in self._session_list:
                print(f"Marking document {identifier} as part of session ({self._session_id})")
                cache_entry["flushed"] = False
                self._session_list.append(identifier)
        self._mark_documents_for_session()

    def include_document_in_session(self, identifier: str):
        """Mark a document as part of the session."""
        assert identifier in self._segment_store, f"Document {identifier} expected in segment store, but failed"

        if identifier in self._session_list:
            print(f"Document {identifier} already part of session ({self._session_id})")
            return
        else:
            print(f"Marking document {identifier} as part of session ({self._session_id})")
            self._session_list.append(identifier)
            self._segment_store[identifier]["flushed"] = False
            self._mark_documents_for_session()

    def number_of_documents_in_session(self):
        """Return the number of documents that are part of the session."""
        return len(self._session_list)

    def get_incompleted_document_ids_for_step(self, step: str):
        """Return the list of document ids that are not yet completed for the step."""
        result = []
        for identifier in self._session_list:
            assert identifier in self._segment_store, f"Document {identifier} expected in segment store, but failed"
            # step might not have been added for session document yet,
            # so append default empty state
            step_state = self._segment_store[identifier]["state"].get(step, {})
            if step_state.get("status") != "completed":
                result.append(identifier)
        return result

    # todo: should this be optional for a specific step?
    def _load_state_for_session_documents(self):
        """Load the state for all documents that are part of the session."""
        for identifier in self._session_list:
            result_steps = self._reader.get_state_for_session_documents(self._session_id, identifier)
            for step in result_steps:
                self._segment_store[identifier]["state"][step["identifier"]] = {
                    "type": step["type"],
                    "status": step["status"],
                    }

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