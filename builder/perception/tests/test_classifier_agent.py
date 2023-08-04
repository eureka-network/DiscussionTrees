from ..classifier_agent import ClassifierPrompt


def test_classifier_prompt():
    message_1 = "Dolphins are mammals"
    message_2 = "Whales live under water"
    classifier_prompt = ClassifierPrompt(message_1, message_2)
    prompt = classifier_prompt.generate_prompt()
    should_be_prompt = "Hello world"
    assert prompt == should_be_prompt


if __name__ == '__main__':
    test_classifier_prompt()
