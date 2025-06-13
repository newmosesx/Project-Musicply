#!/home/tracsbrum/vsmanuel/venv/bin/python
import os
import random
import pygame
import tkinter as tk
import time
import customtkinter as tkk
from tkinter import ttk

lock_file_path = "/home/tracsbrum/Music/S Music/lock/locked.txt"

if os.path.exists(lock_file_path):
    print("Another instance is already running. Exiting.")
    exit()

# Create the lock file
with open(lock_file_path, 'w') as lock_file:
    lock_file.write("MP3 Player Lock File")

folder_path = '/home/tracsbrum/Music/Added Songs'
pygame.display.init()

# Create the main Tkinter window
root = tkk.CTk()
root.title("MP3 Player")
root.geometry("4000x300")

tkk.set_appearance_mode("Dark")


# Create and pack a folder selection frame
folder_frame = tkk.CTkFrame(root,)
folder_frame.grid(row=0, column=0, sticky="nsew")

# Create and pack a label and entry for folder path
tkk.CTkLabel(folder_frame, text="Folder Path:").grid(row=0, column=0, padx=5, pady=5)
folder_var = tkk.StringVar()
folder_entry = tkk.CTkEntry(folder_frame, textvariable=folder_var, width=200)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
folder_entry.insert(0, folder_path)  # Default path

mp3_files = [file for file in os.listdir(folder_var.get()) if file.endswith(".mp3")]

name = None
def play_random_song():
    global name

    if name:
        name.destroy()

    if not mp3_files:
        print("No mp3 files found in the folder.")
        return

    # Select a random song
    random_song = random.choice(mp3_files)
    name = tkk.CTkLabel(root, text=random_song)
    name.place(x=300, y=315)
    song_path = os.path.join(folder_var.get(), random_song)


    # Initialize pygame mixer
    pygame.mixer.init()
    try:
        # Load and play the selected song
        pygame.mixer.music.load(song_path)
        # Set the end event to random the song when it finishes
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        pygame.mixer.music.play()

        # Event loop to handle the end of the song
        while True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    play_random_song()
        
            root.update()
            time.sleep(0.1)  # Adjust the sleep time as needed

    except pygame.error as e:
        print(f"Error playing the song: {random_song}")
        play_random_song()

def pause_song():
    pygame.mixer.music.pause()

def resume_song():
    pygame.mixer.music.unpause()

def play_song(song_path):
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(song_path)

        # Set the end event to restart the song when it finishes
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        
        # Play the selected song
        pygame.mixer.music.play()

        # Event loop to handle the end of the song
        while True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    pygame.mixer.music.play()

            root.update()
            time.sleep(0.1)  # Adjust the sleep time as needed

    except pygame.error as e:
        print(f"Error playing the song: {e}")

    # Quit pygame mixer
    pygame.mixer.quit()

def load_songs_in_folder(folder_path):
    mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]
    return mp3_files

def on_search():
    search_query = search_var.get().lower()
    treeview.delete(*treeview.get_children())

    # Load songs matching the search query
    songs = [song for song in load_songs_in_folder(folder_var.get()) if search_query in song.lower()]
    for song in songs:
        treeview.insert('', 'end', f'{song}', text=song)

def on_song_selected(event):
    global name

    if name:
        name.destroy()

    selected_item = treeview.selection()
    if selected_item:
        #try:
        #Selected_item is inside a tuple so to get the name of the song. I had to specify its location [0]
        selected_song = treeview.item(selected_item[0], "text")
        #except:
        name = tkk.CTkLabel(root, text=selected_song)
        name.place(x=300, y=315)

        selected_song_path = os.path.join(folder_var.get(), selected_song)
        play_song(selected_song_path)

def load_songs_to_tree(folder_path):
    songs = load_songs_in_folder(folder_path)
    """
    Song files which contain {} will output errors,
    the if statment below helps rename this files.
    """
    for song in songs:
        song_path = os.path.join(folder_path, song)
        if "{" in song or "}" in song:
            new_name = song.replace("{", "").replace("}","")
            old_file = os.path.join(folder_path, song)
            new_file = os.path.join(folder_path, new_name)
            os.rename(old_file, new_file)
            song = new_name
            song_path = f"{folder_path}/{song}"
        treeview.insert('', 'end', values=(song_path), text=song)

def close_app():
    global close_flag
    close_flag = True

def check_close_condition():
    if close_flag:
        root.destroy()
        if os.path.exists(lock_file_path):
            os.remove(lock_file_path)
    else:
        root.after(100, check_close_condition)

def remove_lock_file():
    # Remove the lock file before closing
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)


# Set the close operation to trigger the custom function
root.protocol("WM_DELETE_WINDOW", remove_lock_file)


# Set the close flag initially to False
close_flag = False

# Start the periodic check for the close condition
root.after(100, check_close_condition)


# Create and pack a button to load songs
load_button = tkk.CTkButton(folder_frame, text="Load Songs", command=lambda: load_songs_to_tree(folder_var.get()))
load_button.grid(row=2, column=1, padx=20, pady=5)

random_button = tkk.CTkButton(root, text="Random", command=play_random_song)
random_button.grid(row=3, column=0, padx=0, pady=5)

pause_button = tkk.CTkButton(root, text="Pause", command=pause_song)
pause_button.grid(row=4, column=0, padx=0, pady=5)

resume_button = tkk.CTkButton(root, text="Resume", command=resume_song)
resume_button.grid(row=5, column=0, padx=0, pady=5)

# Create and pack a button to play the selected song
play_button = tkk.CTkButton(root, text="Play Selected Song", command=lambda: on_song_selected(None))
play_button.grid(row=9, column=0, padx=0, pady=10)

# Create and pack a button to close the application
close_button = tkk.CTkButton(root, text="Close", command=close_app)
close_button.grid(row=10, column=0, padx=0, pady=10)


bg_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkFrame"]["fg_color"])
text_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkLabel"]["text_color"])
selected_color = root._apply_appearance_mode(tkk.ThemeManager.theme["CTkButton"]["fg_color"])

treestyle = ttk.Style()
treestyle.theme_use('default')
treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
root.bind("<<TreeviewSelect>>", lambda event: root.focus_set())

# Treeview widget data & Position
treeview = ttk.Treeview(root, columns=("Song"), selectmode="browse")
treeview.grid(row=8, column=0, pady=10)
treeview.bind("<Double-1>", on_song_selected)

# Create and pack an entry widget for search
search_var = tkk.StringVar()
search_entry = tkk.CTkEntry(root, textvariable=search_var, width=200)
search_entry.grid(row=6, column=0, padx=0, pady=5)
search_button = tkk.CTkButton(root, text="Search", command=on_search)
search_button.grid(row=7, column=0, padx=5, pady=5)

# Bind the <Return> key to the search function
search_entry.bind("<Return>", lambda event: on_search())
root.mainloop()