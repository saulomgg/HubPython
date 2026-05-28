"""
Image Generator using Stable Diffusion

This script allows users to generate images from text prompts using the Stable Diffusion model.
It features a simple graphical interface for selecting the save directory.

Requirements:
- Python
- torch
- diffusers
- tkinter

Usage:
1. Run the script.
2. Enter a text prompt describing the desired image.
3. Choose a folder to save the generated image.
4. The image will be created and saved in the selected directory.

Author: saulomg2  
Website: https://stampsynk.com  
"""

import torch
from diffusers import StableDiffusionPipeline
from tkinter import Tk
from tkinter import filedialog

# Check if GPU is available, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the model
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to(device)  # Move the model to CPU

# Request the prompt
prompt = input("Enter the prompt to generate the image: ")

# Open a dialog window to select the save directory
Tk().withdraw()  # Hide the main Tkinter window
save_path = filedialog.askdirectory(title="Select a folder to save the image")  # Open the selection window

# Check if the user selected a folder
if save_path:
    # Generate the image
    image = pipe(prompt).images[0]

    # Create the full path to save the image (image filename)
    save_path_with_filename = save_path + "/generated_image.png"

    # Save the image
    image.save(save_path_with_filename)
    print(f"Image generated and saved at: {save_path_with_filename}")
else:
    print("No folder was selected. The process was canceled.")
