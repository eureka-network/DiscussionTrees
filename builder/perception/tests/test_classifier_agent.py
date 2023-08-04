from ..classifier_agent import generate_classifier_prompt, ClassifierAgent, ContextClassifier


def test_classifier_prompt():
    message_1 = "Dolphins are mammals"
    message_2 = "Whales live under water"
    prompt = generate_classifier_prompt(message_1, message_2)
    should_be_prompt = """
        Is this reply post:
        
        ---
        Whales live under water
        ---

        in support, against or its relation is undetermined, regarding post:

        ---
        Dolphins are mammals
        ---

        Your reply should be a single value of the following allowed options ["SUPPORTS", "AGAINST", "UNDETERMINED"]
    """
    assert prompt == should_be_prompt


def test_agent_classifier():
    # Start with two unrelated messages
    message_1 = "Dolphins are mammals"
    message_2 = "Whales live under water"
    agent = ClassifierAgent()
    prediction = agent.classify_context(message_1, message_2)
    assert prediction == ContextClassifier.UNDETERMINED


if __name__ == '__main__':
    test_classifier_prompt()
    test_agent_classifier()
