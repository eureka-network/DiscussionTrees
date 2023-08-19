from discussion_trees.graph_store import Reader, Writer, Graph

class Document:
    def __init__(
            self,
            graph: Graph,
            identifier: str,
            readOnly=True):
        self._identifier = identifier
        self._cached = False
        self._flushed = False
        self._readOnly = readOnly
        self._graph = graph
        self._reader = self._graph.new_reader()
        if not self._readOnly:
            self._writer = self._graph.new_writer()
        else:
            self._writer = None
        
    def exists(self):
        if self._cached:
            return True
        else:
            exists = self._reader.document_exists(self._identifier)
            if exists:
                self._cache()
            return exists
    
    def _cache(self):
        pass
        # if not self._cached:
        #     self._cached = True
        #     self._name = self._reader.get_document_name(self._identifier)
        #     # self._cid = self._reader.get_document_cid(self._identifier)
        #     # self._meta_cid = self._reader.get_document_meta_cid(self._identifier)


    # def get_unit_count(self, refresh=False):
    #     if not self._cached or refresh:
    #         self._db_connection