from collections import namedtuple

from discussion_trees.graph_store import Reader, Writer, Graph


UnitData = namedtuple('UnitData', ['position', 'content', 'digest'])
UnitPosition = namedtuple('UnitPosition', ['position', 'digest'])

class Document:
    def __init__(
            self,
            graph: Graph,
            identifier: str,
            readOnly=True):
        self._identifier = identifier
        self._cached = False
        self._flushed = False
        self._exists = None
        self._readOnly = readOnly
        self._graph = graph
        self._reader = self._graph.new_reader()
        if not self._readOnly:
            self._writer = self._graph.new_writer()
        else:
            self._writer = None
        self._name = None 
        self._number_of_stored_units = None
        self._cached_units = {} # dictionary to store units by their digest
        self._position_digest_list = [] # list to store position and digest of units in order
        self._unstored_units = [] # list to mark units that have not been persisted yet
        
    def exists(self):
        if self._exists is not None:
            return self._exists
        if self._cached: # todo this could be collapsed in above, but for now keep separate
            return True
        else:
            exists = self._reader.document_exists(self._identifier)
            self._exists = exists
            if exists:
                self._cache()
            return exists
    
    def create(self, name):
        if self._exists is None:
            self.exists()
        if self._cached or self._exists:
            raise Exception("Document already exists")
        if self._readOnly:
            raise Exception("Document is read-only")
        self._writer.add_document(self._identifier, name)
        self._cache()
        assert self._name == name, "Document creation failed"
        

    def get_number_of_stored_units(self):
        if not self._cached:
            self._cache()
        return self._number_of_stored_units

    def make_writable(self):
        if self._readOnly:
            self._writer = self._graph.new_writer()
            self._readOnly = False

    def merge(self, units_data: list, autoFlush=True):
        if self._readOnly:
            raise Exception("Document is read-only")

        for unit in units_data:
            # check if the unit already exists in cache
            if unit.digest in self._cached_units:
                # check if the unit is at the same position
                if unit.position != self._cached_units[unit.digest].position:
                    raise Exception(f"Unit position {unit.position} mismatch on cached unit {self._cached_units[unit.digest].position}")
                # check if the unit has the same content
                if unit.content != self._cached_units[unit.digest].content:
                    raise Exception("Unit content mismatch")
                if unit.position > self._number_of_stored_units:
                    raise Exception("Unit position exceeds number of stored units, but was cached")
                continue # skip this unit, it is already stored and cached
            elif unit.position <= self._number_of_stored_units:
                    print(f"Unit position is already stored, but not cached: {unit.position}. Warning: skipping")
                    continue # skip this unit, it is already stored but not cached
            else:
                if unit.position != self._number_of_stored_units + 1:
                    raise Exception("Unit position mismatch on new unit")
                self._cached_units[unit.digest] = unit
                self._unstored_units.append(unit.digest)
                self._number_of_stored_units += 1
                self._position_digest_list.append(UnitPosition(unit.position, unit.digest))

        if autoFlush:
            self.flush()
                
    def flush(self):
        if self._readOnly:
            raise Exception("Document is read-only")
        if len(self._unstored_units) == 0:
            print("Nothing to flush")
            return
        print(f"Flushing {len(self._unstored_units)} units")
        expected_number_of_stored_units = self._number_of_stored_units
        units_segment = []
        for digest in self._unstored_units:
            assert digest in self._cached_units.keys(), "Unstored unit digest not found in cache"
            unit_parameters = {
                "unit_id": f"{self._identifier}-{self._cached_units[digest].position}-{digest[:8]}",
                "document_id": self._identifier,
                "position": self._cached_units[digest].position,
                "content": self._cached_units[digest].content,
                "digest": digest
            }
            units_segment.append(unit_parameters)
        self._writer.add_units_segment(units_segment)
        # read the new total number of stored units from the graph store (todo: possibly overlap of merged units?)
        self._number_of_stored_units = self._reader.get_number_of_stored_units(self._identifier)
        assert self._number_of_stored_units == expected_number_of_stored_units, \
            f"Number of stored units ({self._number_of_stored_units}) does not match expected ({expected_number_of_stored_units})"
        self._unstored_units = []
        self._flushed = True

    def _cache(self):
        if not self._cached:
            self._number_of_stored_units = self._reader.get_number_of_stored_units(self._identifier)
            self._name = self._reader.get_document_properties(self._identifier)["name"]
            # self._cid = self._reader.get_document_cid(self._identifier)
            # self._meta_cid = self._reader.get_document_meta_cid(self._identifier)

            if self._number_of_stored_units > 0:
                units_list = self._reader.get_list_of_unit_digests(self._identifier)
                for unit in units_list:
                    self._position_digest_list.append(UnitPosition(unit["position"], unit["digest"]))

            assert len(self._position_digest_list) == self._number_of_stored_units, "Number of units does not match number of digests"
            self._cached = True



    # def get_unit_count(self, refresh=False):
    #     if not self._cached or refresh:
    #         self._db_connection