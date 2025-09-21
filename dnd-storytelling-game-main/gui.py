import random
import wave

import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence

import deepspeech
import pyaudio
import numpy as np
import threading, time

from main import background_generator, text_to_speech
from player import Character
from player_attribute import PlayerAttribute, PlayerInventory
from tkinter import scrolledtext
from radar_image import radar_factory
import matplotlib.pyplot as plt
from image_generator import ImageGenerator
from story_generation import Generator
import os
import re
import pygame


def edit_img():
    radar = cv2.imread("resources/images/radar.png")
    radar = cv2.resize(radar, (300, 300))
    cv2.imwrite("resources/images/radar.png", radar)


def check_string(string, name):
    if string == "":
        raise ValueError(f"{name} cannot be empty")


def check_int(integer, name):
    if integer == "":
        raise ValueError(f"{name} cannot be empty")
    try:
        int(integer)
    except:
        raise ValueError(f"{name} must be an integer")


class DNDStorytellingGame:
    def __init__(self):
        self.canvas = None
        self.background_img = None
        self.window = tk.Tk()
        self.window.title('DND Storytelling Game')
        self.window.geometry('1280x720')
        self.window.resizable(False, False)
        self.encounter_num = 1
        self.show_home()

        # self.loading_imgs = [tk.PhotoImage(file="resources/loading.gif", format=f'gif - {i}') for i in range(33)]
        # self.loading_index = 0
        # self.loading_label = tk.Label(self.window, image=self.loading_imgs[self.loading_index])
        # self.loading_complete = False
        # self.loading_label.pack()

        self.loading_imgs = [
            ImageTk.PhotoImage(Image.open(f"resources/loading/{i}.png").convert("RGBA")) for i in range(1, 34)
        ]
        self.loading_index = 0

        self.is_recording = False
        self.audio_file = 'recording.wav'
        self.frames = []
        self.player_response = None

        self.difficulty = 10
        self.reason = "The adventurer was faced with a challenging monster."
        self.raw_result = 10
        self.player_utility = 10
        self.axis = 'None'

        self.loading_messages = [
            "The dragon rises to meet the adventurer...",
            "A wizard’s spell is about to unfold...",
            "An ogre prowls the dark forest...",
            "The heroes seek the lost treasure...",
            "A rumble stirs from the dungeon depths...",
            "A powerful spell gathers in the tower...",
            "The portal opens to unknown realms...",
            "Stars align as ancient forces awaken..."
        ]

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=1024)

        # Start recording and set 5 seconds timer
        threading.Thread(target=self.record_audio).start()
        threading.Timer(5, self.stop_recording).start()

    def record_audio(self):
        while self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop_recording(self):
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # Save recording file
        with wave.open(self.audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.frames))

        # call speech to text function
        text = self.convert_audio_to_text()
        self.player_response.insert(tk.END, text)

    def convert_audio_to_text(self):
        if not os.path.exists('DeepSpeech/models/english.pbmm') or not os.path.exists('DeepSpeech/models/english.scorer'):
            return 'DeepSpeech model not found'
        # Assuming the audio file is in the same directory
        model = deepspeech.Model('DeepSpeech/models/english.pbmm')
        model.enableExternalScorer('DeepSpeech/models/english.scorer')

        # read audio file
        audio = np.frombuffer(open(self.audio_file, 'rb').read(), np.int16)
        text = model.stt(audio)
        # print(f"user text: {text}")
        return text

    def set_canvas(self):
        self.stop_audio()
        self.encounter_num = 1
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()

        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/background_blurred.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)

        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 3.6,
            text='DND Storytelling Game',
            font=('Arial', 40),
            fill='white')

        start_button = tk.Button(self.window, text='Single Player', width=20, height=2, command=self.start)

        button_width = start_button.winfo_reqwidth()

        center_x = (canvas_width - button_width) / 2
        self.canvas.create_window(center_x, canvas_height / 2, window=start_button, anchor=tk.NW)
        show_members_button = tk.Button(
            self.window,
            text='Display Production Team',
            width=20,
            height=2,
            command=self.show_members)
        self.canvas.create_window(center_x, canvas_height / 72 * 42, window=show_members_button, anchor=tk.NW)
        show_img_button = tk.Button(
            self.window,
            text='Show Encounter Images',
            width=20,
            height=2,
            command=lambda: self.show_images(0))
        self.canvas.create_window(center_x, canvas_height / 72 * 48, window=show_img_button, anchor=tk.NW)
        quit_button = tk.Button(self.window, text='Quit', width=20, height=2, command=self.window.quit)
        self.canvas.create_window(center_x, canvas_height / 72 * 54, window=quit_button, anchor=tk.NW)

    def show_members(self):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/background_blurred.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)
        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 3.6,
            text='Production Team',
            font=('Arial', 40),
            fill='white')
        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 2.8,
            text='Names in Alphabetical Order',
            font=('Arial', 20),
            fill='white')
        self.canvas.create_text(
            canvas_width / 4,
            canvas_height / 1.8 - 50,
            text='Zixuan Cao',
            font=('Arial', 20),
            fill='white')
        self.canvas.create_text(
            canvas_width / 4,
            canvas_height / 1.8 + 50,
            text='Xiang Ji',
            font=('Arial', 20),
            fill='white')
        self.canvas.create_text(
            canvas_width / 4 * 3,
            canvas_height / 1.8 - 50,
            text='Minyang Xie',
            font=('Arial', 20),
            fill='white')
        self.canvas.create_text(
            canvas_width / 4 * 3,
            canvas_height / 1.8 + 50,
            text='Cover: Alan Huang, James Jiang, John Wang, Ricky Tian',
            font=('Arial', 12),
            fill='white')
        back_button = tk.Button(self.window, text='Last Page', width=10, height=2, command=self.set_canvas)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

    def show_images(self, pt):
        self.img_files = [f for f in os.listdir("resources/images/") if
                          os.path.isfile(os.path.join("resources/images/", f))]
        if pt < 0:
            self.set_canvas()
            return
        if pt >= len(self.img_files):
            self.set_canvas()
            return
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/background_blurred.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)
        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 10,
            text='Encounter Images',
            font=('Arial', 40),
            fill='white')
        if len(self.img_files) == 0:
            self.canvas.create_text(
                canvas_width / 2,
                canvas_height / 3.6 + 50,
                text='No Images Available',
                font=('Arial', 20),
                fill='white')
        else:
            self.generated_img = tk.PhotoImage(file=f'resources/images/{self.img_files[pt]}')
            self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.generated_img, anchor=tk.CENTER)
            next_button = tk.Button(self.window, text='Next Page', width=10, height=2,
                                    command=lambda: self.show_images(pt + 1))
            self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=next_button,
                                      anchor=tk.CENTER)
        back_button = tk.Button(self.window, text='Last Page', width=10, height=2,
                                command=lambda: self.show_images(pt - 1))
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

    def show_conclusion(self, conclusion):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        field_font = ('Algerian', 15)
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/old_book.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)
        self.canvas.create_text(canvas_width / 2, canvas_height / 3.6, text='Congratulations!', font=field_font,
                                fill='black')
        self.canvas.create_text(canvas_width / 2, canvas_height / 3.6 + 50, text='You have completed the game!',
                                font=field_font, fill='black')

        # Draw an area for story conclusion
        text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=40, height=14, background="#FAEED2",
                                              font=field_font)
        self.canvas.create_window(canvas_width / 2, canvas_height / 2 + 100, window=text_area, anchor=tk.CENTER)
        text_area.insert(tk.END, f"""{conclusion}\n""")

        back_button = tk.Button(self.window, text='Home', width=10, height=2, command=self.set_canvas)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

    def show_home(self):
        self.canvas = tk.Canvas(self.window, width=1280, height=720)
        self.canvas.pack(fill='both', expand=True)
        self.set_canvas()

    def start(self):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        field_font = ('Algerian', 15)

        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/old_book.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)
        # self.canvas.create_text(canvas_width / 2, 100, text='Enter the Game Settings', font=('Arial', 40), fill='black')

        # First Page
        self.canvas.create_text(canvas_width / 3 * 0.95, canvas_height / 3 * 1.5,
                                text='Enter the keywords for this \n game background',
                                font=field_font, fill='black', justify="center")  # Text

        text_widget = tk.Text(self.window, width=40, height=8)
        # text_widget.insert('end', text)
        text_widget_window = self.canvas.create_window(canvas_width / 3 * 2.17, canvas_height / 3 * 1.47,
                                                       window=text_widget)

        def get_info():
            text = text_widget.get('1.0', 'end')
            text = text.strip()
            if text == '':
                text = ["Cyberpunk", "desert", "city", "lava"]
            else:
                if ',' in text:
                    text = text.split(',')
                elif '\n' in text:
                    text = text.split('\n')
            self.make_player(text)

        back_button = tk.Button(self.window, text='Last Page', width=10, height=2, command=self.set_canvas)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

        next_button = tk.Button(self.window, text='Next Page', width=10, height=2, command=get_info)
        self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=next_button, anchor=tk.CENTER)

    # def update_loading_label(self):
    #     self.loading_index = (self.loading_index + 1) % 33
    #     self.loading_label.config(image=self.loading_imgs[self.loading_index])
    #     if not self.loading_complete:
    #         self.loading_label.after(100, self.update_loading_label)

    def update_loading_label(self):
        self.loading_index = (self.loading_index + 1) % 33

        self.canvas.itemconfig(self.image_id, image=self.loading_imgs[self.loading_index])

        if not self.loading_complete:
            self.canvas.after(100, self.update_loading_label)

    def make_player(self, story_background):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        field_font = ('Algerian', 15)
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/old_book.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)
        # ---------------------------- Second Page of Player Settings ---------------------------- #
        # Player Name
        self.canvas.create_text(canvas_width / 6, canvas_height / 10 * 2, text='Your Name', font=field_font,
                                fill='black')  # Text
        name = tk.Text(self.canvas, height=1, width=20)
        self.canvas.create_window(canvas_width / 6 * 2, canvas_height / 10 * 2, window=name, anchor=tk.CENTER)

        # Sex
        self.canvas.create_text(canvas_width / 6, canvas_height / 10 * 3, text='Sex', font=field_font,
                                fill='black')  # List of Choice
        var = tk.StringVar()
        male = tk.Radiobutton(self.canvas, text="Male", font=field_font, variable=var, value='male')
        self.canvas.create_window(canvas_width / 6 * 1.8, canvas_height / 10 * 3, window=male, anchor=tk.CENTER)
        female = tk.Radiobutton(self.canvas, text="Female", font=field_font, variable=var, value='female')
        self.canvas.create_window(canvas_width / 6 * 2.3, canvas_height / 10 * 3, window=female, anchor=tk.CENTER)

        # Age
        self.canvas.create_text(canvas_width / 6, canvas_height / 10 * 4, text='Age', font=field_font,
                                fill='black')  # Text
        age = tk.Text(self.canvas, height=1, width=5)
        self.canvas.create_window(canvas_width / 6 * 2, canvas_height / 10 * 4, window=age, anchor=tk.CENTER)

        # Race
        self.canvas.create_text(canvas_width / 6, canvas_height / 10 * 5, text='Race', font=field_font,
                                fill='black')  # Text
        race = tk.Text(self.canvas, height=1, width=20)
        self.canvas.create_window(canvas_width / 6 * 2, canvas_height / 10 * 5, window=race, anchor=tk.CENTER)

        # Level
        self.canvas.create_text(canvas_width / 6, canvas_height / 10 * 6, text='Level', font=field_font,
                                fill='black')  # Text
        level = tk.Text(self.canvas, height=1, width=20)
        self.canvas.create_window(canvas_width / 6 * 2, canvas_height / 10 * 6, window=level, anchor=tk.CENTER)

        # Class
        self.canvas.create_text(canvas_width / 6, canvas_height / 10 * 7, text='Class', font=field_font,
                                fill='black')  # Text
        player_class = tk.Text(self.canvas, height=1, width=20)
        self.canvas.create_window(canvas_width / 6 * 2, canvas_height / 10 * 7, window=player_class, anchor=tk.CENTER)

        ### Player Attributes ###
        values = list(range(11))
        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 2, text='Constitution', font=field_font,
                                fill='black')  # 6 drop down range from 0-20
        cons_drop = ttk.Combobox(self.window, values=values, height=12, width=5, state='readonly')
        cons_drop.current(0)
        self.canvas.create_window(canvas_width / 6 * 4.5, canvas_height / 10 * 2, window=cons_drop, anchor=tk.CENTER)

        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 2.5, text='Strength', font=field_font,
                                fill='black')
        stren_drop = ttk.Combobox(self.window, values=values, height=12, width=5, state='readonly')
        stren_drop.current(0)
        self.canvas.create_window(canvas_width / 6 * 4.5, canvas_height / 10 * 2.5, window=stren_drop, anchor=tk.CENTER)

        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 3, text='Dexterity', font=field_font,
                                fill='black')
        dex_drop = ttk.Combobox(self.window, values=values, height=12, width=5, state='readonly')
        dex_drop.current(0)
        self.canvas.create_window(canvas_width / 6 * 4.5, canvas_height / 10 * 3, window=dex_drop, anchor=tk.CENTER)

        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 3.5, text='Intelligence', font=field_font,
                                fill='black')
        intel_drop = ttk.Combobox(self.window, values=values, height=12, width=5, state='readonly')
        intel_drop.current(0)
        self.canvas.create_window(canvas_width / 6 * 4.5, canvas_height / 10 * 3.5, window=intel_drop, anchor=tk.CENTER)

        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 4, text='Wisdom', font=field_font,
                                fill='black')
        wis_drop = ttk.Combobox(self.window, values=values, height=12, width=5, state='readonly')
        wis_drop.current(0)
        self.canvas.create_window(canvas_width / 6 * 4.5, canvas_height / 10 * 4, window=wis_drop, anchor=tk.CENTER)

        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 4.5, text='Charisma', font=field_font,
                                fill='black')
        char_drop = ttk.Combobox(self.window, values=values, height=12, width=5, state='readonly')
        char_drop.current(0)
        self.canvas.create_window(canvas_width / 6 * 4.5, canvas_height / 10 * 4.5, window=char_drop, anchor=tk.CENTER)

        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 5.5, text='Inventory', font=field_font,
                                fill='black')  # Text
        inventory = tk.Text(self.canvas, height=4, width=30)
        self.canvas.create_window(canvas_width / 6 * 4.7, canvas_height / 10 * 5.5, window=inventory, anchor=tk.CENTER)

        self.canvas.create_text(canvas_width / 6 * 3.7, canvas_height / 10 * 7, text='Background',
                                font=field_font, fill='black')  # Text
        background = tk.Text(self.canvas, height=4, width=30)
        self.canvas.create_window(canvas_width / 6 * 4.7, canvas_height / 10 * 7, window=background, anchor=tk.CENTER)

        def get_info():
            player_name = name.get("1.0", "end-1c")
            player_sex = var.get()
            player_age = age.get("1.0", "end-1c")
            player_race = race.get("1.0", "end-1c")
            player_level = level.get("1.0", "end-1c")
            nonlocal player_class
            player_class_str = player_class.get("1.0", "end-1c")
            player_inventory = inventory.get("1.0", "end-1c")
            player_background = background.get("1.0", "end-1c")
            player_con = cons_drop.get()
            player_str = stren_drop.get()
            player_dex = dex_drop.get()
            player_int = intel_drop.get()
            player_wis = wis_drop.get()
            player_char = char_drop.get()
            try:
                check_string(player_name, 'Name')
                check_string(player_sex, 'Sex')
                check_int(player_age, 'Age')
                check_string(player_race, 'Race')
                check_int(player_level, 'Level')
                check_string(player_class_str, 'Class')
                check_string(player_background, 'Background')
            except ValueError as e:
                messagebox.showerror('Error!', e)
                return None
            ret = [player_name, player_sex, player_age, player_race, player_level, player_class_str, player_inventory,
                   player_background, player_con, player_str, player_dex, player_int, player_wis, player_char]
            print(", ".join(ret))
            return ret

        def run_background_generator(players, background):
            self.narrater, self.story_response = background_generator(players, background)
            # self.loading_label.pack(pady=0)
            # self.loading_label.pack_forget()
            self.canvas.delete(self.image_id)
            self.loading_complete = True
            self.story_begin()

        def generate_player():
            info = get_info()
            if info is None:
                return
            self.player = Character()
            self.player.create(
                info[0],
                info[1],
                int(info[2]),
                info[3],
                int(info[4]),
                info[5],
                PlayerAttribute(constitution=int(info[8]), strength=int(info[9]), dexterity=int(info[10]),
                                intelligence=int(info[11]), wisdom=int(info[12]), charisma=int(info[13])),
                PlayerInventory([], [], [], [], [], [], [info[6]]),
                info[7],
            )
            print("Generated player. ")
            for child in self.canvas.winfo_children():
                child.destroy()
            self.canvas.delete('all')
            # MODIFIED
            self.background_img = tk.PhotoImage(file='resources/background_blurred.png')
            self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)

            text = random.choice(self.loading_messages)
            self.canvas.create_text(canvas_width / 2, canvas_height / 3.6, text=text, font=field_font,
                                    fill='black', justify="center")
            # self.loading_label.pack(pady=20)
            # self.loading_label.place(x=canvas_width / 2, y=canvas_height / 2, anchor=tk.CENTER)
            self.canvas.pack()
            self.image_id = self.canvas.create_image(canvas_width / 2, canvas_height / 2,
                                                     image=self.loading_imgs[self.loading_index])
            self.loading_complete = False
            self.update_loading_label()
            threading.Thread(target=run_background_generator, args=([self.player], story_background)).start()

        # Flip the book
        back_button = tk.Button(self.window, text='Last Page', width=10, height=2, command=self.start)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

        next_button = tk.Button(self.window, text='Next Page', width=10, height=2, command=generate_player)
        self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=next_button, anchor=tk.CENTER)

    def story_begin(self):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        field_font = ('Algerian', 15)
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/old_book.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)

        image = Image.open('resources/images/map.png')
        width, height = image.size
        new_width = int(width * 0.5)
        new_height = int(height * 0.5)

        resized_image = image.resize((new_width, new_height))

        self.generated_img = ImageTk.PhotoImage(resized_image)

        # Generated Image
        # self.generated_img = tk.PhotoImage(file='resources/images/map.png')
        self.canvas.create_image(canvas_width / 3.3, canvas_height / 2.3, image=self.generated_img, anchor=tk.CENTER)

        # Scrollable wordlsetting, region, background
        text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=30,
                                              height=15, background="#FAEED2", font=field_font)
        worldsetting = self.narrater.world.worldsetting.to_narrative()
        region = self.narrater.world.worldregion.to_narrative()
        background = self.narrater.background.to_narrative()

        input = f"""World Setting:\n{worldsetting}\n\nRegion:\n{region}\n\nBackground:\n{background.strip("}")}"""
        text_area.insert(tk.END, input)
        text_area.configure(state='disabled')
        self.canvas.create_window(canvas_width / 4 * 2.9, canvas_height / 2.5, window=text_area,
                                  anchor=tk.CENTER)

        back_button = tk.Button(self.window, text='Home', width=10, height=2, command=self.set_canvas)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

        next_button = tk.Button(self.window, text='Next Page', width=10, height=2, command=self.encounter_loop)
        self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=next_button, anchor=tk.CENTER)

        play_worldsetting = tk.Button(self.window, text='Play World Setting', width=15, height=2,
                                      command=lambda: self.play_audio("worldsetting"))
        self.canvas.create_window(canvas_width / 7 * 4.2, canvas_height / 10 * 7.5, window=play_worldsetting,
                                  anchor=tk.CENTER)

        play_region = tk.Button(self.window, text='Play Region', width=10, height=2, command=lambda: self.play_audio("region"))
        self.canvas.create_window(canvas_width / 7 * 4.9, canvas_height / 10 * 7.5, window=play_region,
                                  anchor=tk.CENTER)

        play_background = tk.Button(self.window, text='Play Background', width=15, height=2,
                                    command=lambda: self.play_audio("background"))
        self.canvas.create_window(canvas_width / 7 * 5.6, canvas_height / 10 * 7.5, window=play_background,
                                  anchor=tk.CENTER)

    def play_audio(self, name):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        self.pause_button = tk.Button(self.window, text='Pause audio', width=10, height=2, command=self.stop_audio)
        self.canvas.create_window(canvas_width / 7 * 2.1, canvas_height / 10 * 8.5, window=self.pause_button,
                                  anchor=tk.CENTER)
        pygame.mixer.init()
        pygame.mixer.music.load(f"resources/audios/output_" + name + ".wav")
        pygame.mixer.music.play()

    def stop_audio(self):
        if hasattr(self, 'pause_button') and self.pause_button is not None:
            self.pause_button.destroy()
        pygame.mixer.init()
        pygame.mixer.music.unload()

    def encounter_loop(self):
        self.stop_audio()
        # self.story_response is first suggestion
        response = self.story_response

        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        field_font = ('Times New Roman', 15)
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        if hasattr(self, 'roll_button'):
            self.roll_button.destroy()
        if hasattr(self, 'reason_textbox'):
            self.reason_textbox.destroy()

        self.background_img = tk.PhotoImage(file='resources/old_book.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)

        def run_conclusion_generation():
            conclusion = self.narrater.generate_conclusion()
            self.loading_complete = True
            self.show_conclusion(conclusion)

        def conclude():
            self.stop_audio()
            conclude_button.destroy()
            inventory_button.destroy()
            play_story.destroy()
            self.canvas.create_text(canvas_width / 7 * 4.3, canvas_height / 10 * 8.5, text='Generating Conclusion...',
                                    font=field_font, fill='black', justify="center")
            self.loading_complete = False
            # self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=self.loading_label,
            #                           anchor=tk.CENTER, height=130, width=130, )
            # self.update_loading_label()

            self.loading_index = 0
            self.image_id = self.canvas.create_image(canvas_width / 7 * 6, canvas_height / 10 * 8.5,
                                                     image=self.loading_imgs[self.loading_index], anchor=tk.CENTER)
            self.update_loading_label()
            threading.Thread(target=run_conclusion_generation).start()

        def run_next_generation(choice):
            # additional_info = f"The adventurer's current status is: {self.player.to_string()}."
            # if self.encounter_num % 3 == 0 and response.find("<END>") != -1:
            #     additional_info = f"""The adventurer's current status is: {self.player.to_string()}.
            #     The adventurer has passed a challenge on day {self.encounter_num - 1}.
            #     You can give him a generous reward.
            #     """
            # choice_reward = self.narrater.get_reward(choice, additional_info)
            # print(f"choice_reward: {choice_reward}\n")
            # try:
            #     self.player.update_attribute(choice_reward)
            # except ValueError as e:
            #     print(e)

            # Why all above, Minyang?

            # Assess the decision
            additional = ''
            if self.encounter_num % 3 == 2:
                additional = f"""This is day {self.encounter_num} of the adventure. It is time that the adventurer meets a challenge. You should attach higher difficulty to this reply (e.g. add 1-3 to the original rate).
                    """
            if self.encounter_num >= 7:
                additional_info = f"""This is day {self.encounter_num} of the adventures. It is about time to conclude the adventure. You should attach lower difficulty to this reply (e.g. reduce 2-4 from the original rate).
                """
            difficulty, reason, axis = self.narrater.assess(choice, additional)
            print("difficulty: ", difficulty)
            print("reason: ", reason)
            print("axis: ", axis)

            raw_result, player_utility = self.player.roll_dice(axis)
            self.difficulty = difficulty
            self.reason = reason
            self.raw_result = raw_result
            self.player_utility = player_utility
            self.axis = axis

            if player_utility == 'shippai':
                print("Dai Shippai!")
                additional_info = f"""The difficulty of the choice the player made was {difficulty}, based on the following reasons: {reason}. 
                Unfortunately, the player experienced a significant failure in this challenge. In the next iteration, please describe the failure, the reason for the player's failure and continue the story, taking into account that this challenge was significantly unsuccessful.
                """
            elif player_utility == 'seiko':
                print("Dai Seiko!")
                additional_info = f"""The difficulty of the choice the player made was {difficulty}, based on the following reasons: {reason}. 
                                Fortunately, the player experienced a significant success in this challenge. In the next iteration, please describe the success, the reason for the player's success and continue the story, taking into account that this challenge was significantly successful.
                                """
            elif player_utility >= difficulty:
                print(f"Player utility: {player_utility}, Difficulty: {difficulty}")
                additional_info = f"""The difficulty of the choice the player made was {difficulty}, based on the following reasons: {reason}. 
                                Fortunately, the player experienced a moderate success in this challenge, due to its {axis}. In the next iteration, please describe the success, the reason for the player's success and continue the story, taking into account that this challenge was moderately successful.
                                """
            else:
                print(f"Player utility: {player_utility}, Difficulty: {difficulty}")
                additional_info = f"""The difficulty of the choice the player made was {difficulty}, based on the following reasons: {reason}. 
                                Unfortunately, the player experienced a minor failure in this challenge, due to its {axis}. In the next iteration, please describe the failure, the reason for the player's failure and continue the story, taking into account that this challenge was partially unsuccessful.
                                """

            # Get story response
            if self.encounter_num % 3 == 2:
                additional_info += f"""This is day {self.encounter_num} of the adventure. The adventurer's current status is: {self.player.to_string()}.
                It is time that the adventurer meets a slightly harder challenge. It can be a fight, a difficult decision, or a puzzle.
                The challenge will test the adventurer's abilities, but it will also provide an opportunity for growth.
                You shall wait for the choice of the adventurer, so do NOT decide the outcome of the challenge.
                """
            if self.encounter_num % 3 == 1:
                if random.randint(0, 1):
                    additional_info += f"""Today is day {self.encounter_num} of the adventure. It's time to reward the player. Based on the previous challenges and the upcoming storyline, you should make a judgment. You should increase an attribute for the player by 2. When giving rewards to the player, use this format:
                    <attribute>strength,2</attribute>
                    Additionally, describe it in natural language, such as:
                    During the player's conversation with the elder elf, the elder's vast knowledge deeply fascinated him. He conversed with the elder, gaining new insights. intelligence+2. <attribute>intelligence,2</attribute>
                    Note that the attribute should be in ['strength', 'constitution', 'dexterity', 'intelligence', 'wisdom', 'charisma'].
                    """
                else:
                    additional_info += f"""Today is day {self.encounter_num} of the adventure. It's time to reward the player. Based on the previous challenges and the upcoming storyline, you should make a judgment. You should give them a new item in their inventory. When giving rewards to the player, use this format:
                                        <inventory>rifle</inventory>
                                        Additionally, describe it in natural language, such as:
                                        During the battle with the cybernetic criminal, the player achieved a great victory and seized their rifle. <inventory>rifle</inventory>
                                        After the reward encounter, please continue the storytelling.
                                        """
            if self.encounter_num >= 7:
                additional_info += f"""The adventurer has already ventured for {self.encounter_num} days.
                It is about time to conclude the adventure. You can generate an outcome for the adventurer.
                If you decide to conclude the game, please make the story complete, with a general ending.
                The output should not contain any options for user to choose, since it is an ending.
                Then output <END> to end the adventure.
                """
            self.story_response = self.narrater.next(choice, additional_info)

            def update_attribute_inventory(player, response):
                # Extract <attribute>...</attribute> elements and apply them
                attribute_pattern = r"<attribute>(.*?)</attribute>"
                attributes = re.findall(attribute_pattern, response)

                att_update = [0, 0, 0, 0, 0, 0]
                for attribute in attributes:
                    # Split attribute and value (e.g., "strength,2")
                    attr_name, attr_value = attribute.split(',')
                    attr_value = int(attr_value)

                    # Apply the attribute change (assuming player attributes are stored in a dictionary)
                    if attr_name == 'strength':
                        att_update[0] += attr_value
                    if attr_name == 'constitution':
                        att_update[1] += attr_value
                    if attr_name == 'dexterity':
                        att_update[2] += attr_value
                    if attr_name == 'intelligence':
                        att_update[3] += attr_value
                    if attr_name == 'wisdom':
                        att_update[4] += attr_value
                    if attr_name == 'charisma':
                        att_update[5] += attr_value

                    # Remove the <attribute>...</attribute> from the response
                    response = response.replace(f"<attribute>{attribute}</attribute>", "")

                player.update_attribute(att_update)

                # Extract <inventory>...</inventory> elements and add them to inventory
                inventory_pattern = r"<inventory>(.*?)</inventory>"
                inventories = re.findall(inventory_pattern, response)

                for inventory_item in inventories:
                    # Add the item to the player's inventory (assuming it's a list)
                    player.inventory.append(inventory_item)
                    # Remove the <inventory>...</inventory> from the response
                    response = response.replace(f"<inventory>{inventory_item}</inventory>", "")

                print(f"Get new inventories: {inventories}")
                return response

            self.story_response = update_attribute_inventory(self.player, self.story_response)

            # print(f"story_response: {self.story_response}\n")
            text_to_speech(self.story_response, "story")
            keywords_generator = Generator("?")
            keyword = keywords_generator.generate_keywords(self.story_response)

            # print(f"keyword: {keyword}\n")

            start_tag = '<'
            end_tag = '>'
            close_tag = '</'
            keywords = []

            start = 0
            while True:
                if start >= len(keyword):
                    break
                start = keyword.find(start_tag, start)
                if start == -1:  # No more tags
                    break
                end = keyword.find(end_tag, start)
                if end == -1:
                    break
                close = keyword.find(close_tag, end)
                if close == -1:
                    break
                tag_content = keyword[end + 1:close].strip()
                keywords.append(tag_content)
                start = close + 1

            main_char = str(self.player.age) + " years old " + str(self.player.sex) + " " + str(
                self.player.race) + " " + str(self.player.c_class)
            # print(f"main_char: {main_char}\n")
            # print(f"keywords: {keywords}\n")

            keywords[0] = main_char
            out_keywords = ""
            for words in keywords:
                if (words != ""):
                    out_keywords += words + ", "

            # print(f"{out_keywords}\n")
            self.encounter_num += 1
            image_gen = ImageGenerator()
            image_gen.get_image("".join(out_keywords), str(self.encounter_num))

            # Update the storyline
            self.loading_complete = True

            def show_result(raw_result):
                """显示 roll 点结果"""
                self.canvas.create_text(930, 400, text=f"1d20: {raw_result}", font=("Arial", 16), fill='black')
                self.canvas.create_text(930, 500, text=f"Final Result: {self.player_utility}", font=("Arial", 16), fill='black')
                self.roll_button.config(state=tk.DISABLED)
                self.window.after(5000, self.encounter_loop)

            self.canvas.delete('all')
            self.background_img = tk.PhotoImage(file='resources/old_book.png')
            self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)
            self.canvas.create_text(400, 130, text=f"Difficulty: {self.difficulty}", font=("Arial", 16), fill='black')
            self.reason_textbox = tk.Text(self.window, height=20, width=40, font=("Arial", 12))
            self.reason_textbox.insert(tk.END, self.reason)
            self.reason_textbox.config(state=tk.DISABLED)
            self.reason_textbox.place(x=210, y=180)

            self.canvas.create_text(930, 200, text=f"Key Attribute: {self.axis}", font=("Arial", 16), fill='black')
            self.roll_button = tk.Button(self.window, text="ROLL THE DICE!",
                                         command=lambda: show_result(raw_result))
            self.roll_button.place(x=880, y=280)

        def next():
            self.stop_audio()
            # print(f"response: {response}")
            choice = self.player_response.get("1.0", "end-1c")
            if choice == "":
                messagebox.showwarning("Warning", "Please make your choice.")
                return

            choice = self.player.get_name() + ": " + choice
            print(f"choice: {choice}\n")

            # Resolve player choice
            next_button.destroy()
            record_button.destroy()
            play_story.destroy()
            inventory_button.destroy()
            text = random.choice(self.loading_messages)
            self.canvas.create_text(canvas_width / 7 * 4.3, canvas_height / 10 * 8.5, text=text, font=field_font,
                                    fill='black', justify="center")
            self.player_response.configure(state='disabled')
            self.loading_complete = False
            self.loading_index = 0
            self.image_id = self.canvas.create_image(canvas_width / 7 * 6, canvas_height / 10 * 8.5,
                                                     image=self.loading_imgs[self.loading_index], anchor=tk.CENTER)

            # self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=self.loading_label,
            #                           anchor=tk.CENTER, height=130, width=130, )
            self.update_loading_label()

            threading.Thread(target=run_next_generation, args=(choice,)).start()

        img_display_id = self.encounter_num
        while not os.path.exists(f'resources/images/img_generated_{img_display_id}.png') and img_display_id > 1:
            img_display_id -= 1
        self.generated_img = tk.PhotoImage(file=f'resources/images/img_generated_{img_display_id}.png')
        self.canvas.create_image(canvas_width / 3.3, canvas_height / 2.3, image=self.generated_img, anchor=tk.CENTER)

        text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=40,
                                              height=14, background="#FAEED2", font=field_font)
        text_area.insert(tk.END, f"""{response}\n""")
        text_area.configure(state='disabled')
        self.canvas.create_window(canvas_width / 4 * 2.9, canvas_height / 2.8, window=text_area,
                                  anchor=tk.CENTER)

        back_button = tk.Button(self.window, text='Home', width=10, height=2, command=self.set_canvas)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

        inventory_button = tk.Button(self.window, text='Check Status', width=10, height=2, command=self.inventory_page)
        self.canvas.create_window(canvas_width / 7 * 2.1, canvas_height / 10 * 8.5, window=inventory_button,
                                  anchor=tk.CENTER)

        inventory_button = tk.Button(self.window, text='World Map', width=10, height=2, command=self.world_page)
        self.canvas.create_window(canvas_width / 7 * 2.8, canvas_height / 10 * 8.5, window=inventory_button,
                                  anchor=tk.CENTER)

        play_story = tk.Button(self.window, text='Play Story', width=10, height=2,
                               command=lambda: self.play_audio("story"))
        self.canvas.create_window(canvas_width / 7 * 5, canvas_height / 10 * 8.5, window=play_story, anchor=tk.CENTER)

        if response.find("<END>") != -1: # No need to continue
            conclude_button = tk.Button(self.window, text='Conclusion', width=10, height=2, command=conclude)
            self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=conclude_button, anchor=tk.CENTER)
            return

        self.player_response = tk.Text(self.canvas, height=8, width=45, font=field_font)
        self.canvas.create_window(canvas_width / 4 * 2.9, canvas_height / 3 * 2.1, window=self.player_response,
                                  anchor=tk.CENTER)

        record_button = tk.Button(self.window, text="Start Recording", width=15, height=2, command=self.start_recording)
        self.canvas.create_window(canvas_width / 7 * 4.3, canvas_height / 10 * 8.5, window=record_button,
                                  anchor=tk.CENTER)

        next_button = tk.Button(self.window, text='Next Page', width=10, height=2,
                                command=next)
        self.canvas.create_window(canvas_width / 7 * 6, canvas_height / 10 * 8.5, window=next_button, anchor=tk.CENTER)

    def inventory_page(self):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        field_font = ('Algerian', 15)
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/old_book.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)
        strength, constitution, dexterity, intelligence, wisdom, charisma = self.player.get_all_attributes()
        data = [['Strength', 'Constitution', 'Dexterity', 'Intelligence', 'Wisdom', 'Charisma'],
                ('Player Attributes', [
                    [strength, constitution, dexterity, intelligence, wisdom, charisma]])]

        N = len(data[0])
        theta = radar_factory(N, frame='polygon')

        spoke_labels = data.pop(0)
        title, case_data = data[0]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='radar'))
        fig.subplots_adjust(top=0.85, bottom=0.05)

        ax.set_rgrids([4, 6, 8, 10])
        ax.set_title(title, position=(0.5, 1.1), ha='center')

        for d in case_data:
            line = ax.plot(theta, d)
            ax.fill(theta, d, alpha=0.25)
        ax.set_varlabels(spoke_labels)

        plt.savefig('resources/images/radar.png')
        plt.close()
        edit_img()

        p_name, p_sex, p_background, p_race, p_age, p_level, p_class = self.player.get_all_info()
        raw_inventory_list = self.player.inventory.inventory
        inventory_list = [raw_inventory_list[0]]
        # inventory_list.append(raw_inventory_list[0])
        for rinv in raw_inventory_list:
            already_in = False
            for inv in inventory_list:
                if rinv == inv:
                    already_in = True
                    continue
            if not already_in:
                inventory_list.append(rinv)

        p_inventory = inventory_list[0]
        for idx, inv in enumerate(inventory_list):
            if not idx:
                continue
            p_inventory += f", {inv}"
        # Player Name
        self.canvas.create_text(canvas_width / 6 + 10, canvas_height / 10 * 2, text='Name', font=field_font,
                                fill='black')  # Text
        self.canvas.create_text(canvas_width / 6 * 2 + 10, canvas_height / 10 * 2, text=p_name, font=field_font,
                                fill='black')

        # Sex
        self.canvas.create_text(canvas_width / 6 + 10, canvas_height / 10 * 3, text='Sex', font=field_font,
                                fill='black')  # List of Choice
        self.canvas.create_text(canvas_width / 6 * 2 + 10, canvas_height / 10 * 3, text=p_sex, font=field_font,
                                fill='black')

        # Age
        self.canvas.create_text(canvas_width / 6 + 10, canvas_height / 10 * 4, text='Age', font=field_font,
                                fill='black')  # Text
        self.canvas.create_text(canvas_width / 6 * 2 + 10, canvas_height / 10 * 4, text=p_age, font=field_font,
                                fill='black')

        # Race
        self.canvas.create_text(canvas_width / 6 + 10, canvas_height / 10 * 5, text='Race', font=field_font,
                                fill='black')  # Text
        self.canvas.create_text(canvas_width / 6 * 2 + 10, canvas_height / 10 * 5, text=p_race, font=field_font,
                                fill='black')

        # Level
        self.canvas.create_text(canvas_width / 6 + 10, canvas_height / 10 * 6, text='Level', font=field_font,
                                fill='black')  # Text
        self.canvas.create_text(canvas_width / 6 * 2 + 10, canvas_height / 10 * 6, text=p_level, font=field_font,
                                fill='black')

        # Class
        self.canvas.create_text(canvas_width / 6 + 10, canvas_height / 10 * 7, text='Class', font=field_font,
                                fill='black')  # Text
        self.canvas.create_text(canvas_width / 6 * 2 + 10, canvas_height / 10 * 7, text=p_class, font=field_font,
                                fill='black')

        # Inventory
        self.canvas.create_text(canvas_width / 6 + 10, canvas_height / 10 * 8, text='Inventory', font=field_font,
                                fill='black')  # Text
        self.canvas.create_text(canvas_width / 6 * 2 + 10, canvas_height / 10 * 8, text=p_inventory, font=field_font,
                                fill='black')

        self.generated_img = tk.PhotoImage(file='resources/images/radar.png')
        self.canvas.create_image(canvas_width / 6 * 4.5, canvas_height / 10 * 4, image=self.generated_img,
                                 anchor=tk.CENTER)

        # Flip the book
        back_button = tk.Button(self.window, text='Back', width=10, height=2, command=self.encounter_loop)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

    def world_page(self):
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        field_font = ('Algerian', 15)
        for child in self.canvas.winfo_children():
            child.destroy()
        self.canvas.delete('all')
        self.background_img = tk.PhotoImage(file='resources/old_book.png')
        self.canvas.create_image(0, 0, image=self.background_img, anchor=tk.NW)

        image = Image.open('resources/images/map.png')
        width, height = image.size
        new_width = int(width * 0.5)
        new_height = int(height * 0.5)

        resized_image = image.resize((new_width, new_height))

        self.generated_img = ImageTk.PhotoImage(resized_image)

        self.canvas.create_image(canvas_width / 3.3, canvas_height / 2.3 + 80, image=self.generated_img, anchor=tk.CENTER)

        text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=30,
                                              height=20, background="#FAEED2", font=field_font)
        worldsetting = self.narrater.world.worldsetting.to_narrative()
        region = self.narrater.world.worldregion.to_narrative()
        background = self.narrater.background.to_narrative()

        input = f"""World Setting:\n{worldsetting}\n\nRegion:\n{region}\n\nBackground:\n{background.strip("}")}"""
        text_area.insert(tk.END, input)
        text_area.configure(state='disabled')
        self.canvas.create_window(canvas_width / 4 * 2.9, canvas_height / 2.0, window=text_area,
                                  anchor=tk.CENTER)


        # World Name
        self.canvas.create_text(canvas_width / 6, canvas_height / 10 * 2 - 3, text=f'World: {self.narrater.world.worldsetting.name}', font=field_font,
                                fill='black')  # Text

        # Flip the book
        back_button = tk.Button(self.window, text='Back', width=10, height=2, command=self.encounter_loop)
        self.canvas.create_window(canvas_width / 7 * 1.1, canvas_height / 10 * 8.5, window=back_button,
                                  anchor=tk.CENTER)

    def mainloop(self):
        self.window.mainloop()


def start_game():
    game = DNDStorytellingGame()
    game.mainloop()


if __name__ == "__main__":
    start_game()
