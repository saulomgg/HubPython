"""
StampSynk - Useful Scripts for Everyday Use

This script is part of StampSynk, a collection of practical and efficient codes created for daily use.  
You can find scripts in various programming languages, explore new tools, and stay updated with improvements.  

This script is also available for download at **stampsynk.com**—just click and use it to download videos on Windows.  
Depending on its performance and demand, better updates will be released in the future!  

StampSynk is a personal project where I'm uploading all my codes and other online resources.  
It is constantly evolving, and your support can help it grow even further!  

Visit **stampsynk.com**, download more scripts, and be part of this journey.  

Creator: @saulomg2  
"""

import yt_dlp
import os
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, 'end')
        folder_entry.insert(0, folder)

def download_video():
    url = url_entry.get().strip()
    destination_folder = folder_entry.get().strip()
    
    if not url:
        messagebox.showerror("Error", "Enter the Bilibili video link.")
        return
    if not destination_folder:
        messagebox.showerror("Error", "Select a folder to save the video.")
        return
    
    options = {
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),  # File name
        'format': 'bestvideo+bestaudio/best',  # Best video and audio quality
        'merge_output_format': 'mp4',  # Final format
        'quiet': False,  # Show progress in terminal
        'postprocessor_args': [
            '-c:v', 'libx264',  # Use H.264 codec for video
            '-c:a', 'aac',  # Use AAC codec for audio
            '-strict', 'experimental'  # Allow experimental codec use
        ],
    }
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Video downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download video: {e}")

# GUI
window = Tk()
window.title("Bilibili Video Downloader")

# Widgets
Label(window, text="Video Link:").grid(row=0, column=0, padx=5, pady=5)
url_entry = Entry(window, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5)

Label(window, text="Save to:").grid(row=1, column=0, padx=5, pady=5)
folder_entry = Entry(window, width=50)
folder_entry.grid(row=1, column=1, padx=5, pady=5)
Button(window, text="Select Folder", command=select_folder).grid(row=1, column=2, padx=5, pady=5)

Button(window, text="Download", command=download_video).grid(row=2, column=1, pady=10)

window.mainloop()
