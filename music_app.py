import os
import random
import pygame
import tkinter as tk
import customtkinter as tkk # double k

from functools import partial
from clean_names import clean_song_name
from tkinter import ttk # double t

def remove_lock_file():
    # Remove the lock file before closing
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)

class Player:
    def __init__(self):
        pygame.mixer.music.set_endevent(pygame.USEREVENT) # Set the end event to repeat the song
        
        self.repeat = False
        self.song_status_id = None
        self.randomize = False

        # Button to repeat songs
        self.repeat_button = tkk.CTkButton(root, text="Repeat: False", command=self.repeating)
        self.repeat_button.grid(row=10, column=0, padx=0, pady=10)

        # Button to randomize songs
        self.random_button = tkk.CTkButton(root, text="Randomize: False", command=self.random_song)
        self.random_button.grid(row=4, column=0, padx=0, pady=5)

        # Button to pause songs
        self.pause_button = tkk.CTkButton(root, text="Pause", command=self.pause_song)
        self.pause_button.grid(row=5, column=0, padx=0, pady=5)

        # Button to resume songs
        self.resume_button = tkk.CTkButton(root, text="Resume", command=self.resume_song)
        self.resume_button.grid(row=6, column=0, padx=0, pady=5)

        # Slider to set song volumes
        self.volume_bar = tkk.CTkSlider(root, from_=0, to=100, command=self.volume)
        self.volume_bar.grid(row=11, column=0, padx=0, pady=10)

        self.playing_song = tkk.CTkLabel(root, text="")
        self.playing_song.place(x=20, y=600)

    def volume(self, value):
        pygame.mixer.music.set_volume(value/100)


    def _load(self, song_path, random_song_name):
        if not self.song_status_id:
            pygame.mixer.music.load(song_path)
            self.play_song(random_song_name)
        else: 
            root.after_cancel(self.song_status_id)
            self.song_status_id = None
            
            pygame.mixer.music.load(song_path)
            self.play_song(random_song_name)
    
    def close_player(self, running):
        # Check the closing and lock file condition and remove the lock file
        if not running:
            if os.path.exists(lock_file_path):
                os.remove(lock_file_path)

            root.unbind("<<TreeviewSelect>>")
            treeview.unbind("<Double-1>")
            search_entry.unbind("<Return>")

            # Condition met, quit mixer, destroy window gracefully and exit the program.
            pygame.mixer.music.stop()
            pygame.mixer.quit()

            root.quit()
            root.destroy()
            
            exit()
    
    def pause_song(self):
        pygame.mixer.music.pause()


    def resume_song(self):
        pygame.mixer.music.unpause()

    def repeating(self):
        self.repeat = False if self.repeat else True
        self.repeat_button.configure(text=f"Repeat: {self.repeat}")
    
    def random_song(self):
        self.randomize = False if self.randomize else True
        self.random_button.configure(text=f"Ranomize: {self.randomize}")
        
        if self.randomize:
            # Select a random song
            random_song_name = random.choice(mp3_files)
            song_path = os.path.join(folder_var.get(), random_song_name)
            self._load(song_path, random_song_name)
    
    def play_song(self, random_song_name):
        pygame.mixer.music.play() # Play the selected song
        self.playing_song.configure(text=random_song_name)
        self.check_song()

    def check_song(self):
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if self.repeat:
                    pygame.mixer.music.play()
                elif self.randomize:
                    self.random_song()
                else: 
                    self.song_status_id = None
                    return
            
        self.song_status_id = root.after(500, self.check_song)

def on_search():
    search_query = search_var.get().lower()
    treeview.delete(*treeview.get_children())

    # Load songs matching the search query
    songs = [song for song in mp3_files if search_query in song.lower()]
    for song in songs:
        treeview.insert('', 'end', f'{song}', text=song)

def clean():
    # --- IMPORTANT SAFETY FEATURE ---
    # Set to False to actually rename files.
    # Set to True to only print what would be renamed.
    DRY_RUN = True

    print(f"Found {len(mp3_files)} MP3 files to process.")
        
    for filename in mp3_files:
        cleaned_filename = clean_song_name(filename)
        
        if filename != cleaned_filename:
            print(f"\nOriginal:  {filename}")
            print(f"Cleaned:   {cleaned_filename}")
            
            if not DRY_RUN:
                try:
                    original_path = os.path.join(folder_path, filename)
                    new_path = os.path.join(folder_path, cleaned_filename)
                    # Check for duplicate filenames before renaming
                    if os.path.exists(new_path):
                        print(f"Status:    ERROR - A file named '{cleaned_filename}' already exists. Skipping.")
                    else:
                        os.rename(original_path, new_path)
                        print("Status:    RENAMED")
                except Exception as e:
                    print(f"Status:    ERROR - Could not rename file: {e}")

    print("\n--- Processing complete. ---")

def load_songs_to_tree():
    clean()
    for song in mp3_files:
        treeview.insert('', 'end', text=song)

def on_song_selected(event):
    print("Event Type: ", event)

    selected_item = treeview.selection()
    if selected_item:
        #Selected_item is inside a tuple so to get the name of the song. I had to specify its location [0]
        selected_song = treeview.item(selected_item[0], "text")
        selected_song_path = os.path.join(folder_var.get(), selected_song)
        player._load(selected_song_path, selected_song)

def close_window():
    # Use your existing close function to ensure the lock file is removed
    player.close_player(False)

def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")


pygame.display.init()
pygame.mixer.init()

# Main Tkinter window (root)
root = tkk.CTk()
root.overrideredirect(True)
root.title("MP3 Player")
root.geometry("500x700")

# Custom Title Bar
title_bar = tkk.CTkFrame(root, height=20, corner_radius=0)
title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)

tkk.set_appearance_mode("Dark")

# Title Label
title_label = tkk.CTkLabel(title_bar, text="Musicply")
title_label.pack(side=tk.LEFT, padx=20)

# Close Button
close_button = tkk.CTkButton(title_bar, text="✕", command=close_window, width=30, height=30)
close_button.pack(side=tk.RIGHT, padx=0)


# Set the default paths
lock_file_path = "lock/locked.txt"
folder_path = 'Music'

# Create and pack a label and entry for folder path
folder_var = tkk.StringVar()
folder_entry = tkk.CTkEntry(root, textvariable=folder_var, width=200)

folder_entry.grid(row=1, column=0, padx=5, pady=5)
folder_entry.insert(0, folder_path)  # Default path


mp3_files = [file for file in os.listdir(folder_var.get()) if file.endswith(".mp3")]


bg_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkFrame"]["fg_color"])
text_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkLabel"]["text_color"])
selected_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkButton"]["fg_color"])

treestyle = ttk.Style()
treestyle.theme_use('default')
treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
root.bind("<<TreeviewSelect>>", lambda event: root.focus_set())

# Treeview widget data & Position
treeview = ttk.Treeview(root, selectmode="browse")
treeview.column("#0", width=500)
treeview.grid(row=9, column=0, pady=10)
treeview.bind("<Double-1>", on_song_selected) # Double click to play song
load_songs_to_tree()

# Entry widget for searching songs
search_var = tkk.StringVar()
search_entry = tkk.CTkEntry(root, textvariable=search_var, width=200)
search_entry.grid(row=7, column=0, padx=0, pady=5)
search_button = tkk.CTkButton(root, text="Search", command=on_search)
search_button.grid(row=8, column=0, padx=5, pady=5)

player = Player()

# Change the app condition if paths are missing
if os.path.exists(lock_file_path):
    print("Another instance is already running. Exiting.")
    player.close_player(False)

if not os.path.exists(folder_path):
    # Next Update: Music app default music folder, to avoid these
    print("The music folder path does not exist.")
    player.close_player(False)

# Create the lock file
with open(lock_file_path, 'w') as lock_file:
    lock_file.write("MP3 Player Lock File")

# Bind the <Return> key to the search function
search_entry.bind("<Return>", lambda event: on_search())

root.mainloop()
