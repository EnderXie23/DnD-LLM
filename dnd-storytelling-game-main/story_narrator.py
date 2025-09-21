from openai import OpenAI
import json
from story_world import World
import story_generator_prompts as prompts
from config import Config
import re

default_parameters = {
    "temperature": 1.0,
    "max_tokens": 1024,
    "top_p": 0.8,
    "stream": False
}

class Background:
    def __init__(self, json):
        self.position = json["position"]
        self.before = json["before-adventure"]
        self.why = json["why"]
        self.problem = json["problem"]

    def to_string(self):
        return """{
            "position": %s
            "before-adventure": %s
            "why": %s
            "problem": %s
        }""" % (
            self.position,
            self.before,
            self.why,
            self.problem,
        )

    def to_narrative(self):
        return """
        %s.
        %s.
        %s
        }""" % (
            self.before,
            self.why,
            self.problem,
        )


class Narrator:
    def __init__(self, players):
        # print("Initializing Narrator...")
        # self.chat_model = ChatModel.from_pretrained("chat-bison@001")
        self.chat_client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)
        self.chat_message = []
        # self.text_model = TextGenerationModel.from_pretrained("text-bison@001")
        self.text_client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)
        self.players = players
        self.world = World()
        self.background = None
        self.session = None
        print("Narrator initialized")

    def generate_world(self, keywords):
        self.world.generate_world(keywords)

    def generate_background_story(self):
        print("Generating Background Story...", end="")
        response = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a dungeon master of a role-playing game."},
                {"role": "user", "content": prompts.prompt_background(
                    self.world.worldsetting.to_string(),
                    self.get_players(),
                    self.world.worldregion.to_string()
                )}
            ],
            **default_parameters
        )

        response = response.choices[0].message.content
        self.background = Background(json.loads(response[response.find('{'):response.rfind('}') + 1]))
        print("Done")

    def start_adventure(self):
        print("Starting Adventure...", end="")
        messages = [
            {"role": "system", "content": f"""
                You are a dungeon master of a role-playing game DnD.
                
                You will be given a player decision together with additional information.
                You will need to judge the influence of the user's decision and provide a narrative continuation.
                Write in third person view. Limit your response to 500 words.

                Additional Requirements:
                Provide where the player is. If the player is in a subregion, you can tell exactly the subregion. If the player is not in a subregion, you can describ where it is, e.g. in the forrest from subregion 1 to subregion 2.
                Provide environment depictions at the beginning.
                Use beautiful language, word choice, and advanced sentences.
                After describing the scenes, provide a few options for the adventurers to continue the game. If the option involves transitting to another subregion, please tell exactly.
                Upon meeting a scene where you need adventurers to make a decision, do NOT make the decision for them.

                World setting: {self.world.worldsetting.to_string()}
                Map: {self.world.worldregion.to_string()}
                Adventurers: {self.get_players()}
            """},
            {"role": "user", "content": f"""
                Decision: Start game
                Additional Information: {self.background.to_string()}
            """}
        ]
        self.chat_message = messages

        response = self.chat_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=self.chat_message,
            **default_parameters
        )

        self.chat_message.append({"role": "assistant", "content": response.choices[0].message.content})
        print("Done")
        return response.choices[0].message.content

    def assess(self, input, additional):
        print("Assessing user choice...")
        user_message = {
            "role": "user",
            "content": f"""
            Forget about the task of continuing the story above.Your next task is to evaluate whether the player's reaction to the existing situation is reasonable.Your output should include the following content:
            
            - difficulty:An integer in [0, 4, 8, 12, 16],the higher the number,the more difficult it is for the player to achieve the reaction.
            - reason:The reason for your difficulty assessment.
            - axis:If the player wants to achieve this reaction,which trait of theirs would be tested?
            
            When formulating your response,consider the following perspectives:
            
            - Your assessment of difficulty should be related to the player's inventory and class.For example,if the player is carrying a gun to engage in a firefight with the gang,then the difficulty of this reaction is relatively low(e.g.,6),and vice versa,it would be higher(e.g.,12).If the player,as a fool,wants to infiltrate a mansion,the difficulty of this reaction is high(e.g.,13),but if the player is a spy,the difficulty is lower(e.g.,4). Also, if the player didn't have the inventory it claimed to have, the difficulty of this reaction is higher.
            - {additional}
            - Your assessment of difficulty should be related to the previous experience of the player. For example, if the player is tired, there should be harder to climb a mountain. 
            - Your assessment of difficulty should be independent of the player's attributes.Difficulty is a description of the player's reaction and objective equipment;the player's attributes will be considered in other stages.
            - Your axis must choose at most one from['strength','constitution','dexterity','intelligence','wisdom','charisma'].If none apply,you should return None.
            - The difficulty should be: 0, if very easy; 4, if comparatively easy;8, if normal; 12, if relatively hard; 16, if very hard.
            
            An example response:
            difficulty: 19 reason: Thomas is the chairman of the biggest company in the cyberpunk world. So it is unlike for the player to reach him. axis: strength
            
            Now, the player's choice is: {input}.
            """
        }
        # print(f"Prompt: {user_message}")
        self.chat_message.append(user_message)

        response = self.chat_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=self.chat_message,
            **default_parameters
        )
        text = response.choices[0].message.content
        self.chat_message.pop()

        difficulty_match = re.search(r'difficulty:\s*(\d+)', text)
        difficulty = int(difficulty_match.group(1)) if difficulty_match else 10

        reason_match = re.search(r'reason:\s*(.*)', text)
        reason = reason_match.group(1).strip() if reason_match else ''

        axis_match = re.search(r'axis:\s*(\w+)', text)
        axis = axis_match.group(1) if axis_match else ''
        return difficulty, reason, axis

    def get_reward(self, input, additional):
        print("Getting Reward...", end="")
        base_prompt = {
            "role": "system",
            "content": f"""
                You are a dungeon master of a role-playing game.
                
                You will be given a player decision together with additional information.
                You will need to judge the reward of the user's decision.

                World setting: {self.world.worldsetting.to_string()}
                Map: {self.world.worldregion.to_string()}
                Adventurers: {self.get_players()}
            """
        }
        user_message = {
            "role": "user",
            "content": f"Decision: {input}\n" + (f"Additional Information: {additional}" if additional else "")
        }
        sys_prompt = {
            "role": "system",
            "content": """You shall decide the reward of the adventurers' decision.
            The adventurer has six attributes: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma.
            Return your decision in the format of a list of six numbers (can be negative).
            Follow the given format strictly and return the numerical results only, do not say anything else.
            
            Example output:
            [1, 2, 3, 2, 1, 3]
            """
        }
        messages = [base_prompt, user_message, sys_prompt]
        response = self.chat_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=messages,
            **default_parameters
        )
        response = response.choices[0].message.content

        # Parse the response into a list of int
        response = response[response.find('[') + 1:response.find(']')].split(",")
        print(response)
        try:
            response = [int(x) for x in response]
        except ValueError:
            return [0, 0, 0, 0, 0, 0]
        print("Done")
        return response

    def generate_conclusion(self):
        print("Generating Conclusion...", end="")
        message={
            "role": "user",
            "content": "The adventurer has met the end of the journey. Please provide a conclusion to the story."
        }
        self.chat_message.append(message)

        response = self.chat_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=self.chat_message,
            **default_parameters
        )

        print("Done")
        return response.choices[0].message.content


    def next(self, input, additional):
        print("Generating next step...", end="")
        user_message = {
            "role": "user",
            "content": f"Decision: {input}\n" + (f"Additional Information: {additional}" if additional else "")
        }
        self.chat_message.append(user_message)

        response = self.chat_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=self.chat_message,
            **default_parameters
        )

        assistant_message = {
            "role": "assistant",
            "content": response.choices[0].message.content
        }
        self.chat_message.append(assistant_message)
        print("Done")
        return response.choices[0].message.content

    def get_players(self):
        rv = ""
        for player in self.players:
            rv += player.to_string() + "\n"
        return rv
