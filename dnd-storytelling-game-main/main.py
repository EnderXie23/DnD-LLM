from player_attribute import PlayerAttribute, PlayerInventory
from player import Character
from image_generator import ImageGenerator
import os
from tqdm import tqdm
from story_generation import Generator
from story_narrator import Narrator
from pydub import AudioSegment

import deepspeech
import pyttsx3
import numpy as np

background = """
The players are all members of a mercenary company called the Silver Blades. 
They have been hired by a local lord to investigate a series of disappearances in the nearby village of Willow Creek. 
The lord believes that the disappearances are the work of goblins, and he has asked the Silver Blades to track down the goblins and bring them to justice.
"""

james = Character()
james.create(
    "James",
    "Male",
    20,
    "human",
    10,
    "fighter",
    PlayerAttribute(10, 10, 10, 10, 10, 10),
    PlayerInventory([], [], [], [], [], [], []),
    "An unknown fighter from a rural village named Vancouver",
)
alan = Character()
alan.create(
    "Alan",
    "Male",
    20,
    "vampire",
    10,
    "archer",
    PlayerAttribute(10, 10, 10, 10, 10, 10),
    PlayerInventory([], [], [], [], [], [], []),
    "A well known vampire from a royal family named Seattle",
)
jj = Character()
jj.create(
    "JJ",
    "Male",
    20,
    "half-elf",
    10,
    "cleric",
    PlayerAttribute(10, 10, 10, 10, 10, 10),
    PlayerInventory([], [], [], [], [], [], []),
    "A half-elf, embarking on a divine quest to heal the world and bring unity through their unique heritage and "
    "unwavering faith.",
)

def text_to_speech(content: str, name):
    count = 0
    pt = 0
    audios = []
    TOKEN_SIZE = 200

    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)

    # print("Total length of content: ", len(content))
    # progress_bar = tqdm(total=len(content), desc="Processing texts")
    while pt < len(content):
        if pt + TOKEN_SIZE < len(content):
            end = content.rfind(".", pt, pt + TOKEN_SIZE)
            if end == -1:
                end = content.rfind(" ", pt, pt + TOKEN_SIZE)
            if end == -1:
                end = pt + TOKEN_SIZE
            curr_content = content[pt:end]
            pt = end + 1
        else:
            curr_content = content[pt:]
            pt = len(content)

        # progress_bar.update(len(curr_content))
        count += 1

        # Save current text as WAV.
        output_filename = f"resources/audios/output_{name}_{count}.wav"
        engine.save_to_file(curr_content, output_filename)
        engine.runAndWait()
        # print(f'Audio content written to file "{output_filename}"')
        audios.append(output_filename)

    # progress_bar.close()
    combined = AudioSegment.empty()
    for audio in audios:
        combined += AudioSegment.from_wav(audio)
        os.remove(audio)

    combined.export(f"resources/audios/output_{name}.wav", format="wav")


def speech_to_text(audio: object) -> object:
    model = deepspeech.Model('DeepSpeech/models/english.pbmm')
    model.enableExternalScorer('DeepSpeech/models/english.scorer')

    audio = np.frombuffer(open('DeepSpeech/audio/2830-3980-0043.wav', 'rb').read(), np.int16)

    text = model.stt(audio)

    return text


def background_generator(players, keywords):
    print("Begin generating background...")
    narrater = Narrator(players)
    narrater.generate_world(keywords)

    image_gen = ImageGenerator()
    if type(keywords) == list:
        image_gen.get_image(", ".join(keywords),"1")
    else:
        image_gen.get_image(keywords,"1")

    # print(
    #     f"{narrater.world.worldsetting.to_narrative()}\n\n{narrater.world.worldregion.to_narrative()}\n\n"
    # )
    text_to_speech(narrater.world.worldsetting.to_narrative(), "worldsetting")
    text_to_speech(narrater.world.worldregion.to_narrative(), "region")

    narrater.generate_background_story()
    # print(
    #     f"Position: {narrater.background.position} \n\n{narrater.background.to_narrative()}\n\n"
    # )
    text_to_speech(narrater.background.to_narrative(), "background")

    response = narrater.start_adventure()
    # print(f"{response}\n")
    text_to_speech(response, "story")
    return narrater, response


def main(players, keywords):
    narrater, _ = background_generator(players, keywords)
    while True:
        user_input = input("")
        response = narrater.next(user_input, "")
        text_to_speech(response, "story")
        # print(f"{response}\n")


if __name__ == "__main__":
    main([james, alan, jj], ["Cyberpunk", "desert", "city", "lava"])
