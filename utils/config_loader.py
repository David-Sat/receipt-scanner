import json
from pathlib import Path


def load_few_shot_examples(examples_file):
    """
    Load few-shot examples from the specified JSON file and process them.
    """
    examples_path = Path(__file__).parent.parent / examples_file
    examples = load_json(examples_path)
    processed_examples = process_examples(examples)
    return processed_examples

def process_examples(examples):
    """
    Process the examples by converting the output to a JSON string.
    """
    for item in examples:
        item['output'] = json.dumps(item['output'])
    return examples


def load_json(path):
    """
    Load JSON data from a given file path.
    """
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {path} not found.")
        exit()
    except json.JSONDecodeError:
        print(f"Error decoding JSON file {path}.")
        exit()


def load_config(config_file='configs/config.json'):
    """
    Load the main configuration file.
    """
    config_path = Path(__file__).resolve().parent.parent / config_file

    config = load_json(config_path)
    return config
