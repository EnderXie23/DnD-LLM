# This file takes in the raw data text and try to parse it into a json format
# using a llm api call.
import json
from tqdm import tqdm
from LLMAgent import LLMAgent


class LLMParser:
    def __init__(self, model_name):
        self.agent = LLMAgent(model_name)

    def parse(self, message):
        return self.agent.run_parse_inference(message)

if __name__ == '__main__':
    parser = LLMParser("deepseek-chat")
    # Read raw input from file
    with open("input.txt", "r", encoding='utf-8') as f:
        text = f.read()
        texts = text.split("\n\n")

    json_objs = []
    progress_bar = tqdm(total=len(texts), desc="Processing texts")
    i = 0  # Initialize index

    while i < len(texts):
        text = texts[i]
        try:
            response = parser.parse(text)
            json_objs.append(json.loads(response))  # Parse and add the JSON object
            i += 1  # Move to the next text only if successful
            progress_bar.update(1)  # Update the progress bar
        except Exception as e:
            print(f"\nError in parsing text {i}: {e}. Retrying...")
    progress_bar.close()

    # save output to a file as json
    with open("output.json", "w", encoding='utf-8') as f:
        json.dump(json_objs, f, indent=4)
