import time

from discussion_trees.graph_store import Graph
from discussion_trees.meaning_function import TogetherLlm, OpenAiLlm, MeaningFunction, MeaningFunctionConfig
from discussion_trees.document_store import Store, Action
from discussion_trees.skill_library import SkillLibrary, Skill

from .strategy import Strategy
from .trajectory import Trajectory

class Builder:
    def __init__(self, config):
        print("Hello, builder !")
        self._config = config
        # graph
        self._graph = Graph(
            self._config.neo4j_credentials[0], # uri
            self._config.neo4j_credentials[1], # user
            self._config.neo4j_credentials[2]) # password
        
        # document store
        self._document_store = Store(self._graph, self._config.builder_session_id)
        self._document_store.load_document_ids()

        # include task document if no documents are in session,
        # and a task document was specified, or
        # if no task document was specified, include all documents
        if self._document_store.number_of_documents_in_session() == 0:
            if self._config.builder_task_document:
                print(f"Current session has no documents. Including task document '{self._config.builder_task_document}' in session.")
                self._document_store.include_document_in_session(self._config.builder_task_document)
            else:
                print("Current session has no documents and no task document was specified. Including all documents in session.")
                self._document_store.include_all_documents_in_session()
            print(f"Session now has {self._document_store.number_of_documents_in_session()} documents.")

        # meaning function
        meaning_function_config = MeaningFunctionConfig()
        meaning_function_config.load_environment_variables()
        self._together_llm = TogetherLlm(meaning_function_config)
        self._openai_llm = OpenAiLlm(meaning_function_config)

        # strategy
        self._strategy = Strategy(self._document_store)
        self._trajectory = self._strategy.construct_trajectory("default")

        # skill library (initialises manual direct prompt skills)
        self._skill_library = SkillLibrary(self._config.skill_library_dir)

    def run(self, trajectory: Trajectory):
        # self._together_llm.start()

        for phase in trajectory:
            print(f"Running phase {phase['document_id']} {phase['step'].step_type}")
            # todo: the difference between a step and a skill is not yet sharp,
            #       in particular there should live python code that allows to store and query the db
            #       and possibly more advanced logic and dependencies on previous results.
            #       for now, I'm simply coupling them in builder with "step_type" and "skill_name"
            skill = self._skill_library.get_skill(phase["step"].step_type)
            assert isinstance(skill, Skill), f"Expected to retrieve a Skill instance for {phase['step'].step_type}, but got {type(skill)}"
            document = self._document_store.get_document(phase["document_id"])
            actions = self._document_store.get_actions_for_document(phase["document_id"])
            step_identifier = actions.get_step_identifier(phase["step"].step_type)
            skill_description = self._openai_llm.description + ": " + skill.description
            new_actions = []
            for index, group in enumerate(phase["groups"], start = 1):
                # hack: to minimise LLM calls, only run specific phases (depends on my local .env file)
                if index >= 7:
                    continue
                units = []
                unit_identifiers = []
                for unit_position in group:
                    unit_data = document.get_unit_data(unit_position)
                    units.append(unit_data.content)
                    unit_identifiers.append(unit_data.identifier)
                prompt = skill.generate_prompt(units)
                print(f"Prompt for position {unit_position}:\n\n{prompt}\n\n")
                response = self._openai_llm.prompt(prompt, wrap_system_prompt=True)
                processed_response = skill.process_response(response)
                new_actions.append(Action(
                    step_id = step_identifier,
                    trajectory_id = trajectory.get_run_identifier(1), # for now we only have one run
                    run = 1,
                    timestamp = int(time.time()), # seconds since epoch
                    skill_description = skill_description,
                    inputs = unit_identifiers,
                    outputs = [processed_response],
                ))
                print(f"Processed response:\n\n{processed_response}\n\n")
            actions.merge_actions_under_step(
                phase["step"].step_type,
                actions = new_actions,
                autoFlush = True,
            )    
            
        # self._together_llm.stop()
