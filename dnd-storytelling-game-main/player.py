from player_attribute import PlayerAttribute
from player_attribute import PlayerInventory
import vertexai
import random
from vertexai.preview.language_models import (
    ChatModel,
    InputOutputTextPair,
    TextGenerationModel,
)
from google.cloud import texttospeech


class Character:
    def create(
        self,
        name,
        sex,
        age,
        race,
        level,
        player_class,
        attributes,
        inventory,
        background,
    ):
        self.name = name
        self.sex = sex
        self.background = background
        self.attributes = attributes
        self.race = race
        self.age = age
        self.level = level
        self.inventory = inventory
        self.c_class = player_class
        self.generated = True

    def init_from_json(self, json):
        self.name = json["name"]
        self.sex = json["sex"]
        self.background = json["description"]
        self.attributes = PlayerAttribute(json["attributes"])
        self.race = json["race"]
        self.age = json["age"]
        self.level = json["level"]
        self.inventory = PlayerInventory(json["equipment"])
        self.c_class = json["class"]
        self.generated = True

    def prepare(self, name, inhabitant):
        self.name = name
        self.inhabitant = inhabitant
        self.generated = False

    def __init__(self):
        self.generated = False

    def to_string(self):
        return """{
            "name":%s,
            "description":%s,
            "sex":%s,
            "age":%s,
            "level":%s,
            "class":%s,
            "race":%s,
            "attributes":%s,
            "equipment":%s,
            "relationship":%s
        }
        """ % (
            self.name,
            self.background,
            self.sex,
            self.age,
            self.level,
            self.c_class,
            self.race,
            self.attributes.to_string(),
            self.inventory.to_string(),
            "",
        )
    
    def get_all_info(self):
        return self.name, self.sex, self.background, self.race, self.age, self.level, self.c_class
    
    def get_all_attributes(self):
        return self.attributes.strength, self.attributes.constitution, self.attributes.dexterity, self.attributes.intelligence, self.attributes.wisdom, self.attributes.charisma

    def update_attribute(self, values):
        self.attributes.strength += values[0]
        self.attributes.constitution += values[1]
        self.attributes.dexterity += values[2]
        self.attributes.intelligence += values[3]
        self.attributes.wisdom += values[4]
        self.attributes.charisma += values[5]
        print("Attributes updated by: ", values)

    def roll_dice(self, axis=None):
        """
        Parameters
        ----------
        axis: The axis of attribution that should be considered
        (axis should be in ['strength', 'constitution', 'dexterity', 'intelligence', 'wisdom', 'charisma'])

        Returns
        -------
        'seiko' if raw result is 20
        'shippai' if raw result is 1
        raw result if axis is not in attribution
        raw result + corresponding attribution if axis is in attribution
        """

        # print(self.to_string())
        raw_result = random.randint(1, 20)
        if raw_result == 1:
            return raw_result, 'shippai'
        if raw_result == 20:
            return raw_result, 'seiko'

        if axis == 'strength':
            return raw_result, raw_result + self.attributes.strength - 5
        if axis == 'constitution':
            return raw_result, raw_result + self.attributes.constitution - 5
        if axis == 'dexterity':
            return raw_result, raw_result + self.attributes.dexterity - 5
        if axis == 'intelligence':
            return raw_result, raw_result + self.attributes.intelligence - 5
        if axis == 'wisdom':
            return raw_result, raw_result + self.attributes.wisdom - 5
        if axis == 'charisma':
            return raw_result, raw_result + self.attributes.charisma - 5

        return raw_result, raw_result

    def get_all_inventory(self):
        return self.inventory.helmet, self.inventory.chestplate, self.inventory.leggings, self.inventory.boots, self.inventory.righthand, self.inventory.lefthand, self.inventory.inventory
    
    def get_name(self):
        return self.name


def generatePlayer(mode):
    # mode = "speech"
    # mode = "text"
    if mode == "speech":
        # call speech to text
        input = "Please enter the name of the player"
    else:
        input = input(
            "Select the way to generate player: A. Description; B. Fill in the blank; C. Randomly generate"
        )
        if input.upper() == "A":
            input = input(
                "Please enter the following information: name, sex, age, race, level, player_class, attributes, background"
            )
