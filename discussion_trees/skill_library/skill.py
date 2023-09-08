import json
import yaml
import os

from discussion_trees.builder.group import Group, GroupList

from .manual_skills import MANUAL_SKILLS


DIRECT_PROMPT_SKILL_TYPE = "DirectPromptSkill"


class Skill:
    def __init__(self):
        pass

    def order(self):
        raise NotImplementedError("Skill must implement order")
    
    def generate(self, units: list):
        raise NotImplementedError("Skill must implement generate_prompt")
    
    def process_response(self, response):
        raise NotImplementedError("Skill must implement process_response")
    
    def description(self):
        raise NotImplementedError("Skill must implement description")


class DirectPromptSkill(Skill):
    def __init__(self,
                 name: str,
                 order: int,
                 description: str,
                 prompt_template: str,
                 post_process_code: str = None):
        self._name = name
        self._order = order
        self._description = description
        self._prompt_template = prompt_template
        self._post_process_code = post_process_code

    def order(self):
        return self._order

    def generate(self, units: list):
        """Generate a prompt for the given units."""
        assert len(units) == self._order, f"Number of units must be equal to order, got {len(units)} units and order {self._order}"
        
        replacements = {}
        for index, unit in enumerate(units, start = 1):
            assert isinstance(unit, str), "Only str instances can be added."
            replacements[f"unit{index}"] = unit

        return self._prompt_template.format(**replacements)
    
    def process_response(self, input: list, response):
        """Process the response."""
        if self._post_process_code is None:
            return response
        else:
            assert isinstance(input, list), "Input must be a list"
            assert len(input) == self._order, f"Number of units must be equal to order, got {len(input)} units and order {self._order}"

            global_context = {
                "json": json,
            }
            local_context = {
                "input": input,
                "response": response
            }
            print(f"local context: {local_context}")
            try:
                exec(self._post_process_code, global_context, local_context)
            except Exception as e:
                raise Exception(f"Error while executing post process code: {e}")
            
            print(f"post process code result: {local_context['post_response']}")
            return local_context["post_response"]
    
    @property
    def description(self):
        # todo: generate an active description based on self
        return self._name


class ComputeMapSkill(Skill):
    def __init__(
            self,
            name: str,
            order: int,
            depth: int,
            description: str,
            code: str
        ):
        assert isinstance(code, str), "Code must be a string"
        assert code != "", "Code must not be empty"
        self._name = name
        self._order = order
        self._depth = depth
        self._description = description
        self._code = code

    def order(self):
        return self._order
    
    def map_groups(self):
        # build the segment and the 
        pass

    def generate(self, units: list):
        pass

    def compute(self, state: list):
        """Compute the action on the state of this group with this skill."""
        assert len(state) == self._order, f"Group order must be equal to skill order, got {len(state)} and {self._order}"

        global_context = {
            "json": json,
        }
        local_context = {
            "state": state,
        }
        raise NotImplementedError("ComputeMapSkill must implement compute")

class SkillLibrary:
    def __init__(self, skills_dir: str):
        self._skills = {}

        if not os.path.isdir(skills_dir):
            raise ValueError(f"Skills directory {skills_dir} is not a valid directory")

        # add manual skills from yaml files
        for skill in MANUAL_SKILLS.values():
            file_path = os.path.join(skills_dir, skill["skill_file"])
            print(f"Loading skill from {file_path}")
            self.load_skill_from_yaml(file_path)
            
    def get_skill(self, name: str):
        if name not in self._skills:
            raise Exception(f"Skill {name} not found")
        return self._skills[name]
    
    def load_skill_from_yaml(self, yaml_file_path: str):
        with open(yaml_file_path, 'r') as f:
            skill_config = yaml.safe_load(f)

        skill_name = skill_config["metadata"]["name"]

        if skill_config["skill_type"] == DIRECT_PROMPT_SKILL_TYPE:
            self._skills[skill_name] = DirectPromptSkill(
                name=skill_name,
                order=skill_config["order"],
                description=skill_config["description"],
                prompt_template=skill_config["prompt_template"],
                post_process_code=skill_config["post_process_code"])
        else:
            raise Exception(f"Unknown skill type {skill_config['skill_type']}")
    
