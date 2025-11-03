import os
import random
import pygame
import tkinter as tk
import customtkinter as tkk # Using customtkinter for a modern look

from functools import partial
from clean_names import clean_song_name
from tkinter import ttk # Using ttk for the Treeview widget

def remove_lock_file():
    """Removes the lock file if it exists."""
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)

class Player:
    """Manages music playback, including controls like repeat, randomize, pause, and volume."""
    def __init__(self):
        """Initializes the music player and its UI components."""
        pygame.mixer.music.set_endevent(pygame.USEREVENT) # Creates a custom event for when a song ends
        
        # --- Player State Variables ---
        self.repeat = False
        self.song_status_id = None # To keep track of the after() call for checking song status
        self.randomize = False

        # --- UI Elements ---
        # Button to toggle repeating the current song
        self.repeat_button = tkk.CTkButton(root, text="Repeat: False", command=self.repeating)
        self.repeat_button.grid(row=10, column=0, padx=0, pady=10)

        # Button to toggle playing songs in random order
        self.random_button = tkk.CTkButton(root, text="Randomize: False", command=self.random_song)
        self.random_button.grid(row=4, column=0, padx=0, pady=5)

        # Button to pause the currently playing song
        self.pause_button = tkk.CTkButton(root, text="Pause", command=self.pause_song)
        self.pause_button.grid(row=5, column=0, padx=0, pady=5)

        # Button to resume a paused song
        self.resume_button = tkk.CTkButton(root, text="Resume", command=self.resume_song)
        self.resume_button.grid(row=6, column=0, padx=0, pady=5)

        # Slider to control the music volume
        self.volume_bar = tkk.CTkSlider(root, from_=0, to=100, command=self.volume)
        self.volume_bar.grid(row=11, column=0, padx=0, pady=10)

        # Label to display the name of the currently playing song
        self.playing_song = tkk.CTkLabel(root, text="")
        self.playing_song.place(x=20, y=600)

    def volume(self, value):
        """Sets the music volume based on the slider's value."""
        # The slider goes from 0 to 100, but set_volume expects a value between 0.0 and 1.0
        pygame.mixer.music.set_volume(value / 100)

    def _load(self, song_path, song_name):
        """Loads and plays a new song, canceling any existing song check."""
        # If a song status check is scheduled, cancel it before loading a new song
        if self.song_status_id:
            root.after_cancel(self.song_status_id)
            self.song_status_id = None
        
        # Load the selected song file and start playing it
        pygame.mixer.music.load(song_path)
        self.play_song(song_name)
    
    def close_player(self, running):
        """Handles the application shutdown gracefully."""
        # If the application is already running, this check prevents it from closing prematurely
        if not running:
            # Clean up the lock file before exiting
            if os.path.exists(lock_file_path):
                os.remove(lock_file_path)

            # Unbind all events to prevent errors during shutdown
            root.unbind("<<TreeviewSelect>>")
            treeview.unbind("<Double-1>")
            search_entry.unbind("<Return>")

            # Stop the music, quit the mixer, and destroy the Tkinter window
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            root.quit()
            root.destroy()
            exit() # Terminate the script
    
    def pause_song(self):
        """Pauses the currently playing music."""
        pygame.mixer.music.pause()

    def resume_song(self):
        """Resumes the music if it's paused."""
        pygame.mixer.music.unpause()

    def repeating(self):
        """Toggles the repeat mode on or off."""
        self.repeat = not self.repeat # Invert the current repeat state
        self.repeat_button.configure(text=f"Repeat: {self.repeat}")
    
    def random_song(self):
        """Toggles the randomize mode and plays a random song if enabled."""
        self.randomize = not self.randomize # Invert the current randomize state
        self.random_button.configure(text=f"Randomize: {self.randomize}")
        
        if self.randomize:
            # Pick a random song from the list of MP3 files
            random_song_name = random.choice(mp3_files)
            song_path = os.path.join(folder_var.get(), random_song_name)
            self._load(song_path, random_song_name) # Load and play the random song
    
    def play_song(self, song_name):
        """Plays the loaded song and updates the display."""
        pygame.mixer.music.play() # Start playback
        self.playing_song.configure(text=song_name) # Update the label with the song name
        self.check_song() # Start checking the song's status

    def check_song(self):
        """Periodically checks the status of the song to handle repeat/randomize logic."""
        # Check for Pygame events, specifically the custom end-of-song event
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if self.repeat:
                    pygame.mixer.music.play() # Replay the same song
                elif self.randomize:
                    self.random_song() # Play a new random song
                else: 
                    # If neither repeat nor randomize is on, stop checking
                    self.song_status_id = None
                    return
        
        # Schedule this function to run again after 500ms
        self.song_status_id = root.after(500, self.check_song)

def on_search():
    """Filters the songs in the Treeview based on the search query."""
    search_query = search_var.get().lower()
    treeview.delete(*treeview.get_children()) # Clear the current list

    # Find and display songs that match the search query
    songs = [song for song in mp3_files if search_query in song.lower()]
    for song in songs:
        treeview.insert('', 'end', text=song)

def clean():
    """Cleans up the filenames of the MP3 files in the music folder."""
    # --- IMPORTANT SAFETY FEATURE ---
    # Set to False to actually rename files.
    # Set to True to only print what would be renamed.
    DRY_RUN = True

    print(f"Found {len(mp3_files)} MP3 files to process.")
        
    for filename in mp3_files:
        cleaned_filename = clean_song_name(filename) # Uses an external function to clean the name
        
        if filename != cleaned_filename:
            print(f"\nOriginal:  {filename}")
            print(f"Cleaned:   {cleaned_filename}")
            
            if not DRY_RUN:
                try:
                    original_path = os.path.join(folder_path, filename)
                    new_path = os.path.join(folder_path, cleaned_filename)
                    # Prevent overwriting existing files
                    if os.path.exists(new_path):
                        print(f"Status:    ERROR - A file named '{cleaned_filename}' already exists. Skipping.")
                    else:
                        os.rename(original_path, new_path)
                        print("Status:    RENAMED")
                except Exception as e:
                    print(f"Status:    ERROR - Could not rename file: {e}")

    print("\n--- Processing complete. ---")

def load_songs_to_tree():
    """Cleans filenames and then loads all MP3 files into the Treeview."""
    clean() # Clean names before loading
    for song in mp3_files:
        treeview.insert('', 'end', text=song)

def on_song_selected(event):
    """Callback function for when a song is double-clicked in the Treeview."""
    selected_item = treeview.selection()
    if selected_item:
        # Get the song name from the selected Treeview item
        selected_song = treeview.item(selected_item[0], "text")
        selected_song_path = os.path.join(folder_var.get(), selected_song)
        player._load(selected_song_path, selected_song) # Load and play the song

def close_window():
    """Ensures the application closes properly using the Player's close method."""
    player.close_player(False)

# --- Functions for custom draggable title bar ---
def start_move(event):
    """Records the initial mouse position when clicking the title bar."""
    root.x = event.x
    root.y = event.y

def do_move(event):
    """Moves the window based on mouse movement while the button is held down."""
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

# --- Initialization ---
pygame.display.init() # Initialize the Pygame display module
pygame.mixer.init()   # Initialize the Pygame mixer for audio

# --- Main Tkinter Window Setup ---
root = tkk.CTk()
root.title("MP3 Player")
root.geometry("500x700")

# --- Custom Title Bar ---
# Remove the default title bar (this is OS-dependent and might not work perfectly)
# root.overrideredirect(True) 
title_bar = tkk.CTkFrame(root, height=20, corner_radius=0)
title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

# Bind mouse events for dragging the window
title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)

tkk.set_appearance_mode("Dark") # Set the theme for the application

# Title Label in the custom title bar
title_label = tkk.CTkLabel(title_bar, text="Musicply")
title_label.pack(side=tk.LEFT, padx=20)

# Custom Close Button
close_button = tkk.CTkButton(title_bar, text="✕", command=close_window, width=30, height=30)
close_button.pack(side=tk.RIGHT, padx=0)

# --- Application Paths ---
lock_file_path = "lock/locked.txt" # Path to prevent multiple instances
folder_path = 'Music'              # Default music folder

# --- Folder Path Entry ---
folder_var = tkk.StringVar()
folder_entry = tkk.CTkEntry(root, textvariable=folder_var, width=200)
folder_entry.grid(row=1, column=0, padx=5, pady=5)
folder_entry.insert(0, folder_path)  # Set the default path in the entry box

# --- Load MP3 Files ---
# List all files in the music folder that end with .mp3
mp3_files = [file for file in os.listdir(folder_var.get()) if file.endswith(".mp3")]

# --- Treeview Styling ---
# Get theme colors to make the ttk.Treeview match the customtkinter theme
bg_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkFrame"]["fg_color"])
text_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkLabel"]["text_color"])
selected_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkButton"]["fg_color"])

treestyle = ttk.Style()
treestyle.theme_use('default')
treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
# This binding helps ensure the Treeview looks focused when selected
root.bind("<<TreeviewSelect>>", lambda event: root.focus_set())

# --- Treeview Widget for Song List ---
treeview = ttk.Treeview(root, selectmode="browse")
treeview.column("#0", width=500) # Configure the main column
treeview.grid(row=9, column=0, pady=10)
treeview.bind("<Double-1>", on_song_selected) # Bind double-click to play song
load_songs_to_tree() # Populate the list

# --- Search Functionality ---
search_var = tkk.StringVar()
search_entry = tkk.CTkEntry(root, textvariable=search_var, width=200)
search_entry.grid(row=7, column=0, padx=0, pady=5)
search_button = tkk.CTkButton(root, text="Search", command=on_search)
search_button.grid(row=8, column=0, padx=5, pady=5)

# --- Instantiate the Player ---
player = Player()

# --- Pre-run Checks ---
# Check if a lock file exists to prevent running multiple instances
if os.path.exists(lock_file_path):
    print("Another instance is already running. Exiting.")
    player.close_player(False)

# Check if the designated music folder exists
if not os.path.exists(folder_path):
    print("The music folder path does not exist.")
    player.close_player(False)

# --- Create Lock File ---
# Create the lock file to indicate the application is running
with open(lock_file_path, 'w') as lock_file:
    lock_file.write("MP3 Player Lock File")

# --- Bind Events ---
# Bind the <Return> key in the search entry to trigger the search function
search_entry.bind("<Return>", lambda event: on_search())

# --- Main Loop ---
# Start the Tkinter event loop
root.mainloop()

# Bind the <Return> key to the search function
search_entry.bind("<Return>", lambda event: on_search())

root.mainloop()
