"""Document state machine"""


PREPOPULATION_QUERIES = {
    "incomplete_cleanup": {"template": "incomplete_step",
                           "parameters": {"step_type": "cleanup"},
                           "requires": ["session_id"],
                          },
    "incomplete_structure": {"template": "incomplete_step",
                             "parameters": {"step_type": "structure"},
                             "requires": ["session_id"],
                          },
    "incomplete_content": {"template": "incomplete_step",
                           "parameters": {"step_type": "content"},
                           "requires": ["session_id"],
                          },
    }


DOCUMENT_PREPOPULATION_TEMPLATES = {
    "incomplete_step": (
        "MATCH (d:Document)-[:HAS_SESSION]->(sc:SessionController) "
        "WHERE sc.session_id = $specific_session_id "
        "OPTIONAL MATCH (sc)-[:HAS_STEP]->(s:Step) "
        "WHERE s.type = $step_type AND (NOT EXISTS(s.completed) OR s.completed = false) "
        "RETURN d.identifier as document_id, s.identifier as step_id "
        ),
    }


class DocumentState:

    def __init__(self, session_id: str):
        # query library matches a query key to query templates and initial parameters
        # for retrieving and updating document state
        self._query_library = {}
        self._session_id = session_id
        self._prepopulate_manual_steps()

    def _prepopulate_manual_steps(self):
        # gather all possible required parameters
        required_parameters = {"session_id": self._session_id}

        for query_key, query in PREPOPULATION_QUERIES.items():
            # dynamically set addional required parameters
            dynamic_parameters = {}
            for required_parameter in query["requires"]:
                dynamic_parameters[required_parameter] = required_parameters[required_parameter]
            # set parameters for the query first with the prepopulation parameters,
            # then with the dynamic parameters
            set_parameters = query["parameters"].copy()
            if dynamic_parameters:
                set_parameters.update(dynamic_parameters)
            self._query_library[query_key] = {
                "template": DOCUMENT_PREPOPULATION_TEMPLATES[query["template"]],
                "parameters": set_parameters
            }

    def _formulate_query(self, transaction, query_key: str, specific_parameters: dict):
        query = self._query_library[query_key]["template"]
        
        # make a local copy of the parameters
        parameters = self._query_library.get(query_key, {}).get("parameters", {}).copy()
        if not parameters:
            raise Exception(f"Query key {query_key} not found in query library")
        parameters.update({"specific_session_id": self._session_id})

        # update parameters with specific parameters
        if specific_parameters:
            parameters.update(specific_parameters)

        # continue here TODO
        result = transaction.run(query, parameters)
        return list(result)
