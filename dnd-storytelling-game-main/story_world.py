import json
import os

import story_generator_prompts as prompts
from player import Character
from openai import OpenAI
from config import Config
import re
from world_map import Map


class World:
    def __init__(self):
        print("Initializing World...")
        self.chat_client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)
        self.text_client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)
        self.worldsetting = None
        self.worldregion = None
        self.regions = {}
        self.structures = {}
        self.npcs = {}
        print("World initialized")

    def generate_world(self, keywords):
        parameters = {
            "temperature": 1.0,
            "max_tokens": 1024,
            "top_p": 0.8,
            "stream": False
        }

        print("Generating World Setting...", end="")

        message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompts.prompt_worldsetting(keywords)},
        ]
        worldsetting_string = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=message,
            **parameters
        )
        worldsetting_string = worldsetting_string.choices[0].message.content

        start_index = worldsetting_string.find('{')
        end_index = worldsetting_string.rfind('}')
        worldsetting_string = worldsetting_string[start_index:end_index + 1]

        self.worldsetting = Worldsetting(json.loads(worldsetting_string))
        # print(f"World Setting: {worldsetting_string}")

        print("Done")
        print("Generating World Region...", end="")

        message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompts.prompt_region(
                context=self.worldsetting,
                size="large",
                name=self.worldsetting.name,
            )},
        ]
        worldregion = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=message,
            **parameters
        )
        worldregion = worldregion.choices[0].message.content

        start_index = worldregion.find('{')
        end_index = worldregion.rfind('}')
        worldregion = worldregion[start_index:end_index + 1]

        self.worldregion = Region()
        self.worldregion.init_from_json(json.loads(worldregion))
        for subregion in self.worldregion.subregions:
            if not subregion in self.regions:
                self.regions[subregion] = Region()
                self.regions[subregion].prepare(subregion, self.worldregion)

        # print(f"World Region: {worldregion}")
        self.map_generator = Map(self.worldregion, use_image=True)
        self.map_generator.draw_map()
        print("Done")

    def generate_region(self, site_name, parent_site):
        parameters = {
            "temperature": 1.0,
            "max_tokens": 512,
            "top_p": 0.8,
            "stream": False
        }

        message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompts.prompt_region(
                    context=self.worldsetting,
                    name=site_name,
                    parent_region=json.dumps(parent_site),
                )
             }
        ]
        response = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=message,
            **parameters
        )
        response = response.choices[0].message.content

        # response = json.loads(
        #     self.text_model.predict(
        #         prompts.prompt_region(
        #             context=self.worldsetting,
        #             name=site_name,
        #             parent_region=json.dumps(parent_site),
        #         ),
        #         **parameters,
        #     )
        # )

        generated_region = Region()
        generated_region.init_from_json(response)
        for subregion in generated_region.subregions:
            if not subregion in self.regions:
                self.regions[subregion] = Region()
                self.regions[subregion].prepare(subregion, self.worldregion)
        self.regions[generated_region.name] = generated_region

    def generate_structure(self, site_name, parent_site):
        parameters = {
            "temperature": 1.0,
            "max_tokens": 512,
            "top_p": 0.8,
            "stream": False
        }

        message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompts.prompt_structure(
                        self.worldsetting, site_name, json.dumps(parent_site)
                    )
             }
        ]
        response = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=message,
            **parameters
        )
        response = response.choices[0].message.content

        generated_structure = Structure()
        generated_structure.init_from_json(
            json.loads(
                response
            )
        )
        for npc in generated_structure.npcs:
            if not npc in self.npcs:
                self.npcs[npc] = Character(npc, generated_structure)
        self.structures[generated_structure["name"]] = generated_structure

    def generate_npc(self, npc_name, parent_site):
        parameters = {
            "temperature": 1.0,
            "max_tokens": 512,
            "top_p": 0.8,
            "stream": False
        }
        generated_npc = Character()

        message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompts.prompt_npc(npc_name, json.dumps(parent_site))}
        ]
        response = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=message,
            **parameters
        )
        response = response.choices[0].message.content

        generated_npc.init_from_json(
            response
        )
        self.npcs[generated_npc["name"]] = generated_npc


class Worldsetting:
    def __init__(self, json):
        self.name = json["name"]
        self.geography = json["geography"]
        self.econimic = json["economic and technology"]
        self.society = json["society"]
        self.inhabitants = json["inhabitants"]
        self.ability = json["ability-system"]
        self.lore = json["history"]

    def to_string(self):
        return """{
            "name":%s,
            "geography":%s,
            "economic and technology":%s,
            "society":%s,
            "inhabitants":%s,
            "ability-system":%s,
            "lore":%s
            }""" % (
            self.name,
            self.geography,
            self.econimic,
            self.society,
            self.inhabitants,
            self.ability,
            self.lore,
        )

    def to_narrative(self):
        return """
            %s.  
            %s  
            %s  
            %s  
            %s  
            %s  
            %s  
            """ % (
            self.name,
            self.geography,
            self.econimic,
            self.society,
            self.inhabitants,
            self.ability,
            self.lore,
        )


class Region:
    def init_from_json(self, json):
        self.name = json["name"]
        self.types = json["type"]
        self.description = json["description"]
        self.subregions = json["sub-regions"]
        self.structures = json["structures"]
        self.inhabitants = json["inhabitants"]
        self.generated = True

    def prepare(self, name, parent):
        self.name = name
        self.parent = parent
        self.generated = False

    def __init__(self):
        self.generated = False

    def to_string(self):
        return """{
            "name":%s,
            "type":%s,
            "description":%s,
            "sub-regions":%s,
            "structures":%s,
            "inhabitants":%s,
            }""" % (
            self.name,
            json.dumps(self.types),
            self.description,
            json.dumps(self.subregions),
            json.dumps(self.structures),
            json.dumps(self.inhabitants),
        )

    def to_narrative(self):
        return """
                Region Name: %s
                Region Type: %s
                Description: %s
                Sub-regions: %s
                Landmarks: %s
                inhabitants: %s
                """ % (
            self.name,
            json.dumps(self.types),
            self.description,
            json.dumps(self.subregions),
            json.dumps(self.structures),
            json.dumps(self.inhabitants),
        )


class Structure:
    def init_from_json(self, json):
        self.name = json["name"]
        self.types = json["type"]
        self.description = json["description"]
        self.npcs = json["npc"]
        self.generated = True

    def __init__(self):
        self.generated = False

    def prepare(self, name, parent):
        self.name = name
        self.parent = parent
        self.generated = False

    def to_string(self):
        return """{
            "name":%s,
            "type":%s,
            "description":%s,
            "npc":%s
            }""" % (
            self.name,
            json.dumps(self.types),
            self.description,
            json.dumps(self.sublocations),
            json.dumps(self.npcs),
        )
