from openai import OpenAI
from config import Config

import re
import json

import random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
# from story_world import Region
from image_generator import ImageGenerator


class Map:
    def __init__(self, region, use_image=False):
        self.text_client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)
        self.region = region  # class Region in story_world.py:
        # self.name = json["name"]
        # self.description = json["description"]
        # self.subregions = json["sub-regions"]
        # self.structures = json["structures"]
        # self.inhabitants = json["inhabitants"]
        # self.generated = True

        self.color = self._predict_color()
        self.use_image = use_image

    def _generate_subregion_img(self):
        if not self.use_image:
            return
        prompt = f"""Generate stable diffusion prompts for each subregion. The world region is {self.region}.
        The subregions are {self.region.subregions}.
        
        Your response should be in the form like this, without any other content:
        {{
            "{self.region.subregions[0]}":"...",
            "{self.region.subregions[1]}":"..."
        }}
        An example of prompt: A simple desert landscape with sand dunes, clear blue sky, and a warm setting sun. Sparse cacti and shrubs, with distant mountains. A peaceful and empty atmosphere.
        
        Please note that, the picture should not be so detailed.
        """

        parameters = {
            "temperature": 1.0,
            "max_tokens": 512,
            "top_p": 0.8,
            "stream": False
        }

        print("Generating subregion image...")

        message = [
            {"role": "system", "content": "You are a stable diffusion model prompt generator."},
            {"role": "user", "content": prompt},
        ]
        j = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=message,
            **parameters
        )
        j = j.choices[0].message.content
        prompts = {}
        prompts = json.loads(j)

        img_gen = ImageGenerator()

        for i, subregion in enumerate(self.region.subregions):
            # img_gen.get_image(prompts[f"subregion_{i}"], 0, f"resources/subregions/subregion{i}.png")
            img_gen.get_image(prompts[subregion], 0, f"resources/subregions/subregion{i}.png")

        return

    def _predict_color(self):
        prompt = f"""
        There's a imaginary D&D world, called {self.region.name}, the type of it being {self.region.types}. {self.region.description}
        
        There are some subregions of {self.region.name}. They are {self.region.subregions}. Please imagine, if you choose a color to represent a subregion, what color will you choose? Please give me the color in RGB form.
        
        Your answer should look like this:
        {{"The Emerald Jungle":[76,153,0], "The Obsidian Mountains":[51,51,0], "The Golden Plains":[204,204,0], "The Shattered Desert":[255,255,51], "The Azure Coast":[51,153,255]}}
        
        Please DON'T say anything else.
        """

        parameters = {
            "temperature": 1.0,
            "max_tokens": 512,
            "top_p": 0.8,
            "stream": False
        }

        print("Predicting colors...")

        message = [
            {"role": "system", "content": "You are a helpful art assistant and you are a painter."},
            {"role": "user", "content": prompt},
        ]
        j = self.text_client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=message,
            **parameters
        )
        j = j.choices[0].message.content
        # j = "{"The Emerald Jungle":[76,153,0], "The Obsidian Mountains":[51,51,0], "The Golden Plains":[204,204,0], "The Shattered Desert":[255,255,51], "The Azure Coast":[51,153,255]}"
        color = json.loads(j)
        print(f"Predicted color: {color}")
        return color

    def generate_random_polygon(self, center, size, num_vertices):
        angle_step = 2 * np.pi / num_vertices
        vertices = []
        for i in range(num_vertices):
            angle = i * angle_step
            radius = random.uniform(size * 0.8, size)
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            vertices.append([x, y])
        return vertices

    def draw_map(self):
        if self.use_image:
            self._generate_subregion_img()

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')

        fig.patch.set_facecolor([255 / 255, 229 / 255, 204 / 255])

        polygons = []
        names = list(self.color.keys())

        centers = []

        def is_valid_center(center, centers, tolerance):
            for post_center in centers:
                if min(abs(center[0]-post_center[0]), abs(center[1]-post_center[1])) < tolerance:
                    return False
            return True

        for idx, (name, color) in enumerate(zip(names, self.color.values())):
            num_vertices = random.randint(10, 20)
            size = random.uniform(0.15, 0.30)

            max_try = 100
            center = (0, 0)
            for i in range(max_try):
                center = [random.uniform(0.05, 0.95), random.uniform(0.05, 0.95)]
                if is_valid_center(center, centers, tolerance=0.1):
                    centers.append(center)
                    break
                if i == max_try - 1:
                    print(f"Invalid map after {max_try} tries. Centers: {centers}")

            vertices = self.generate_random_polygon(center, size, num_vertices)
            polygon = Polygon(vertices, closed=True, edgecolor='black', facecolor=np.array(color)/255, lw=1.5)
            ax.add_patch(polygon)

            ax.text(center[0], center[1] + 0.05, name, color="black", ha="center", va="center", fontsize=16)

            polygons.append((vertices, name))

            if self.use_image:
                img_path = f"resources/subregions/subregion{idx}.png"
                img = mpimg.imread(img_path)

                imagebox = OffsetImage(img, zoom=0.15)
                ab = AnnotationBbox(imagebox, (center[0], center[1] - 0.05), frameon=False,
                                    boxcoords="axes fraction", xycoords="axes fraction")
                ax.add_artist(ab)

        plt.xlim(0, 1)
        plt.ylim(0, 1)
        ax.axis('off')
        name = f"Map of {self.region.name}"
        plt.title(name, fontsize=20)

        plt.savefig('resources/images/map.png', bbox_inches='tight', pad_inches=0.1)
        plt.close()
        print("World map saved.")


# if __name__ == "__main__":
#     # color_dict = {
#     #     "The Emerald Jungle": [76, 153, 0],
#     #     "The Obsidian Mountains": [51, 51, 0],
#     #     "The Golden Plains": [204, 204, 0],
#     #     "The Shattered Desert": [255, 255, 51],
#     #     "The Azure Coast": [51, 153, 255]
#     # }
#     region = Region()
#     j = """{
#       "name": "Eryndral",
#       "type": ["Continent"],
#       "size": "large",
#       "description": "Eryndral is a sprawling continent filled with diverse landscapes, from dense jungles and towering mountain ranges to vast deserts and fertile plains. The continent is home to a rich tapestry of cultures and civilizations, each with their own unique traditions and beliefs. Magic is a fundamental aspect of life in Eryndral, with both divine and arcane magic being widely practiced. The gods of Eryndral are revered by many, and their influence is felt in every corner of the land. The continent is also home to a variety of powerful creatures, including dragons, who hold significant influence over the land and its inhabitants. The history of Eryndral is marked by numerous conflicts and alliances, with various factions vying for power and control. Despite the challenges, Eryndral remains a land of great opportunity and adventure, where heroes are born and legends are made.",
#       "sub-regions": ["The Emerald Jungle", "The Obsidian Mountains", "The Golden Plains", "The Shattered Desert", "The Azure Coast"],
#       "structures": [],
#       "inhabitants": ["Humans", "Elves", "Dwarves", "Gnomes", "Halflings", "Dragons", "Giants", "Orcs", "Tieflings"]
#     }"""
#     j = json.loads(j)
#     region.init_from_json(j)
#
#     map_drawer = Map(region, use_image=True)
#     map_drawer.draw_map()
