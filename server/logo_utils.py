import customtkinter as ctk
from PIL import Image
import os

def setup_logo(window):
    """Sets up the Principal logo in the top-left corner of the window."""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "assets", "principal_logo.png")
        
        # Create assets directory if it doesn't exist
        os.makedirs(os.path.join(script_dir, "assets"), exist_ok=True)
        
        # Load the original image to get its dimensions
        original_image = Image.open(logo_path)
        original_width, original_height = original_image.size
        
        # Calculate new width while maintaining aspect ratio
        target_height = 40  # Slightly smaller height for better fit
        target_width = int((original_width / original_height) * target_height)
        
        # Load and resize the logo maintaining aspect ratio
        logo_image = ctk.CTkImage(
            light_image=original_image,
            dark_image=original_image,
            size=(target_width, target_height)
        )
        
        # Create label for logo with padding
        logo_label = ctk.CTkLabel(
            window,
            image=logo_image,
            text="",  # No text, only image
            padx=10,  # Add horizontal padding
            pady=5    # Add vertical padding
        )
        return logo_label
        
    except Exception as e:
        print(f"Error setting up logo: {e}")
        return None 