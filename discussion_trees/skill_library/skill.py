from .manual_prompts import MANUAL_SKILL_PROMPTS


class Skill:
    def __init__(self):
        pass

    def order(self):
        raise NotImplementedError("Skill must implement order")
    
    def generate_prompt(self, units: list):
        raise NotImplementedError("Skill must implement generate_prompt")


class DirectPromptSkill(Skill):
    def __init__(self,
                 name: str,
                 order: int,
                 description: str,
                 prompt_template: str):
        self._name = name
        self._order = order
        self._description = description
        self._prompt_template = prompt_template

    def order(self):
        return self._order

    def generate_prompt(self, units: list):
        """Generate a prompt for the given units."""
        assert len(units) == self._order, f"Number of units must be equal to order, got {len(units)} units and order {self._order}"
        
        replacements = {}
        for index, unit in enumerate(units, start = 1):
            assert isinstance(unit, str), "Only str instances can be added."
            replacements[f"unit{index}"] = unit

        return self._prompt_template.format(**replacements)


class SkillLibrary:
    def __init__(self):
        self._skills = {}
        # add manual direct prompt skills
        for skill_name, skill in MANUAL_SKILL_PROMPTS.items():
            self._skills[skill_name] = DirectPromptSkill(
                skill_name,
                skill["order"],
                skill["description"],
                skill["prompt"])
            
    def get_skill(self, name: str):
        if name not in self._skills:
            raise Exception(f"Skill {name} not found")
        return self._skills[name]