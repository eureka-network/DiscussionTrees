MANUAL_SKILL_PROMPTS = {
    "cleanup": {
        "order": 5,
        "description": "Cleanup the text",
        "prompt": "CLEANUP PROMPT",
    },


    "contentOnePointJSON": {
        "order": 1,
        "description": "extract content and relations from a single unit as JSON",
#<s>[INST] <<SYS>>\nYou are a helpful assistent. Always answer completely, correctly and to the point as asked.\n<</SYS>>\n\n
        "prompt": """
Given the paragraph:

'{unit1}',

extract all the entities and the relations between these entities in a structured JSON format.
Only use the information provided in the above paragraph.
Do not infer or hallucinate any data outside of the paragraph's content.
Your response should be in the following JSON format:

{{ "entities": [ {{ "entity_id": "e1", "type": "EntityType", "value": "EntityName", "evidence": "Verbatim textual evidence from the paragraph" }}, ... ],
   "relations": [ {{ "relation_id": "r1", "type": "RelationType", "from": "e1", "to": "e2", "evidence": "Verbatim textual evidence from the paragraph" }}, ... ] }}

Please only provide the answer.
""",
#[/INST]
    },


    "contentOnePointTABLE": {
        "order": 1,
        "description": "extract content and relations from a single unit as a table",
# <s>[INST] <<SYS>>\nYou are a helpful assistent excellent at extracting semantical meaning from text. Always answer completely, correctly and to the point as asked.\n<</SYS>>\n\n
        "prompt": """
Given the paragraph:

'{unit1}',

extract all the entities and the relations between these entities in a structured table format.
Only use the information provided in the above paragraph.
Please provide textual evidence as a verbatim copy from the paragraph.
Do not infer or hallucinate any data outside of the paragraph's content.
Your response should be in the following structured format:

Entities:
EntityID, EntityType, EntityName, Textual evidence from the paragraphs
...
Relations:
RelationID, RelationType, FromEntityID, ToEntityID, Textual evidence from the paragraphs
...

Please only provide the answer.
""", #[/INST]
    },
        

    "entitiesOnePointJSON": {
        "order": 1,
        "description": "extract entities from a single unit",
        "prompt": """
<s>[INST] <<SYS>>\nYou are a helpful assistent. Always answer completely, correctly and to the point as asked.\n<</SYS>>\n\n
Given the paragraph:

'{unit1}',

extract all the important entities in a structured JSON format.
Only use the information provided in the above paragraph.
Do not infer or hallucinate any data outside of the paragraph's content.
Please provide textual evidence as a verbatim copy from the paragraph.
Your response should be in the following JSON format:

{{ "entities": [ {{ "entity_id": "e1", "type": "EntityType", "value": "EntityName", "evidence": "Verbatim textual evidence from the paragraph" }}, ... ] }}

...

Please only provide the answer as a table. Do not include any other text in your answer.
[/INST]
""",
    },
                
        
    "eventsOnePoint": {
        "order": 1,
        "description": "extract events from a single unit",
        "prompt": """
Given the paragraph:

'{unit1}',

extract all the important events in a structured table format.
Only use the information provided in the above paragraph.
Do not infer or hallucinate any data outside of the paragraph's content.
Your response should be in the following format:

Events:
EventID, EventType, EventName, Textual evidence from the paragraphs
...

Please only provide the answer as a table. Do not include any other text in your answer.
""",
    },
}