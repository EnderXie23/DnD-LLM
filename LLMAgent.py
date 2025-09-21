import os
from dotenv import load_dotenv
from openai import OpenAI

class LLMAgent:
    def __init__(self, model_name, temperature=0.6, max_new_tokens=1000, top_p=0.9, frequency_penalty=0.0,
                 presence_penalty=0.0, base_url="https://api.deepseek.com", api_key=None):
        self.model_name = model_name
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.base_messages = []

        # get the api key from the environment variable
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY") if api_key is None else api_key,
            base_url=base_url
        )

    def run_basic_inference(self, messages=None):
        assert isinstance(messages, list), "messages should be a list"
        completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            logprobs=True,
        )
        output = completion.choices[0].message.content
        return output

    def run_parse_inference(self, message):
        base_prompt = """You are a helpful json parser for the DnD game module.
                    You will be given a raw text describing the scene and / or some information about the game module.
                    Then you will need to parse the raw text into a json format, at the same time splitting the text into different sections.
                    The first part shall be public to all players, while the second part shall be private to the DM.
                    If there is no public / private content, you can just omit the first / second part.
                    Below is an example of raw text that you need to parse into json format:
                    Raw Text:

                    ```
                    Day 1 - Crossing South of the Village
                    South of the village, the land becomes increasingly barren, the terrain more rugged, the forests denser, and the paths more treacherous.
                    Then, at a clearing by a stream, you discover a fragment of rose-colored silk under a rock.
                    If the player characters search the area for additional clues, allow each of them to roll a DC 15 Investigation check.
                    ```

                    Now below is the json format that you need to parse the raw text into:

                    ```
                    {
                        "name": "Day 1 - Crossing South of the Village",
                        "public": "South of the village, the land becomes increasingly barren, the terrain more rugged, the forests denser, and the paths more treacherous. Then, at a clearing by a stream, you discover a fragment of rose-colored silk under a rock.",
                        "private": "If the player characters search the area for additional clues, allow each of them to roll a DC 15 Investigation check."
                    }
                    ```

                    You only need to output the json format of the raw text.
                    You do NOT need to output the formatting string "```".
                    Got it?
                    """
        self.base_messages = [
            {"role": "system", "content": base_prompt},
            {"role": "assistant", "content": "Got it!"},
        ]
        messages = self.base_messages + [{"role": "user", "content": message}]

        return self.run_basic_inference(messages).replace("```\n", "").replace("```", "")

    def run_dm_generator(self, message):
        base_prompt = """
        You are the Dungeon Master (DM) for a DnD game module.
        You will be given a raw text describing the scene and / or some information about the game module.
        Based on the given information provided, you will need to generate a response that fits the context of the game module.
        Also, you shall try to make the response as engaging and interesting as possible.
        You can add some imaginary elements to make the game more fun, but do not violate the rules of the game.
        Limit your answer to 150 words.
        Got it?
        """
        self.base_messages = [
            {"role": "system", "content": base_prompt},
            {"role": "assistant", "content": "Got it!"},
        ]
        messages = self.base_messages + [{"role": "user", "content": message}]

        return self.run_basic_inference(messages)
