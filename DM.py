import os
from LLMAgent import LLMAgent
import random
import json

class DungeonMaster:
    def __init__(self, model_name, game_data):
        self.agent = LLMAgent(model_name)
        self.game_data = game_data
        self.current_day = 2
        self.player_decisions = []
        self.available_actions = []
        self.is_game_over = False

    def get_day_description(self):
        name = self.game_data[self.current_day]['name']
        info = self.game_data[self.current_day]['public']
        priv_info = self.game_data[self.current_day]['private']
        message = "The public information given is about " + name + ": " + info + "."
        message += "Also, as the DM, you know some private info: " + priv_info + "."
        message += ("How will you describe this scene to the players? "
                    "You shall tell the players only the public information."
                    "You shall return the description only, with no additional information.")
        return self.agent.run_dm_generator(message)

    def get_player_actions(self):
        info = self.game_data[self.current_day]['public']
        priv_info = self.game_data[self.current_day]['private']
        message = "You are the DM for a DnD game module. Now you have some information about the game module:" + info + ".\n"
        message += "Also, as the DM, you know some private info: " + priv_info + ".\n"
        message += "A player can choose from the following types of actions: search, fight and rest.\n"
        message += "Help judge on this day, what actions can be taken by the player and is not meaningless?\n"
        message += "You shall return the actions in plain text. Limit your response to 30 words.\n"
        messages = [
            {"role": "system", "content": message},
        ]
        return "You can: " + self.agent.run_basic_inference(messages) + " What's your choice?"

    def resolve_player_action(self, resp):
        if self.is_game_over:
            return "The game is over."

        info = self.game_data[self.current_day]['public']
        priv_info = self.game_data[self.current_day]['private']
        message = "You are the DM for a DnD game module. Now you have some information about the game module:" + info + ".\n"
        message += "Also, as the DM, you know some private info: " + priv_info + ".\n"
        message += "A player has made the decision: " + resp + ".\n"
        message += "You shall return the outcome of the player's decision. You can reveal some private info if needed."
        message += "Your response shall be in plain text, with no format whatsoever."

        self.player_decisions.append(message)

        return self.agent.run_dm_generator(message)

        # Managing player decisions here:
        # if action == "search":
        #     outcome = self.roll_dice_for_clues()
        #     if outcome:
        #         return "You find additional clues to continue your journey."
        #     else:
        #         return "The search yielded no useful information."
        # elif action == "fight":
        #     return self.resolve_fight()
        # elif action == "rest":
        #     return "You rest for the night, gaining some strength."
        # else:
        #     return "Unknown action."

    def roll_dice_for_clues(self):
        return random.choice([True, False])

    def resolve_fight(self):
        outcome = random.choice(["victory", "defeat"])
        if outcome == "victory":
            return "The party emerges victorious after a tough battle!"
        else:
            self.is_game_over = True
            return "The party was defeated. The game ends here."

    def advance_to_next_day(self):
        if self.current_day < len(self.game_data) - 1:
            self.current_day += 1
            return f"Advancing to Day {self.current_day + 1}!"
        else:
            self.is_game_over = True
            return "The adventure has reached its conclusion."

    def summary(self):
        return {
            "current_day": self.current_day,
            "player_decisions": self.player_decisions,
            "is_game_over": self.is_game_over,
        }

# Read game data from output.json
with open('output.json') as f:
    game_data = json.load(f)
dm = DungeonMaster("deepseek-chat", game_data)
print(dm.get_day_description())
# print(dm.get_player_actions())
# player_resp = input()
# print(dm.resolve_player_action(player_resp))

# print(dm.player_action("proceed"))
# print(dm.player_action("search"))
# print(dm.reveal_private_info())
# print(dm.player_action("ask_llm"))
# print(dm.summary())
