#!/usr/bin/env python3
"""
Visualization Viewer for Resume Scoring Accuracy

This script displays the generated visualizations in a simple GUI window.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import glob

class VisualizationViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Scoring Accuracy Visualizations")
        self.root.geometry("1000x800")
        
        # Find all visualization files
        self.image_files = self.find_visualization_files()
        self.current_image_index = 0
        
        self.setup_ui()
        if self.image_files:
            self.load_image()
        else:
            self.show_no_images_message()
    
    def find_visualization_files(self):
        """Find all visualization files"""
        patterns = [
            "accuracy_heatmap_*.png",
            "difference_heatmap_*.png", 
            "accuracy_barchart_*.png"
        ]
        
        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern))
        
        # Sort by modification time, newest first
        files.sort(key=os.path.getmtime, reverse=True)
        return files
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Resume Scoring Accuracy Visualizations", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.previous_image)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.image_counter = ttk.Label(nav_frame, text="0/0")
        self.image_counter.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.next_image)
        self.next_button.pack(side=tk.LEFT)
        
        # Image display
        self.image_label = ttk.Label(main_frame)
        self.image_label.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # Image info
        self.image_info = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.image_info.grid(row=3, column=0, columnspan=3)
        
        # Refresh button
        refresh_button = ttk.Button(main_frame, text="Refresh Images", command=self.refresh_images)
        refresh_button.grid(row=4, column=0, columnspan=3, pady=(20, 0))
        
        # Update button states
        self.update_navigation_buttons()
    
    def load_image(self):
        """Load and display the current image"""
        if not self.image_files:
            return
            
        try:
            image_path = self.image_files[self.current_image_index]
            
            # Load and resize image
            image = Image.open(image_path)
            image.thumbnail((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Update display
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Keep a reference
            
            # Update counter
            self.image_counter.configure(
                text=f"{self.current_image_index + 1}/{len(self.image_files)}"
            )
            
            # Update info
            self.image_info.configure(text=f"File: {image_path}")
            
            # Update button states
            self.update_navigation_buttons()
            
        except Exception as e:
            self.image_info.configure(text=f"Error loading image: {e}")
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        if not self.image_files:
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            return
            
        self.prev_button.configure(state="normal" if self.current_image_index > 0 else "disabled")
        self.next_button.configure(state="normal" if self.current_image_index < len(self.image_files) - 1 else "disabled")
    
    def previous_image(self):
        """Show the previous image"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()
    
    def next_image(self):
        """Show the next image"""
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()
    
    def refresh_images(self):
        """Refresh the list of image files"""
        self.image_files = self.find_visualization_files()
        self.current_image_index = 0
        
        if self.image_files:
            self.load_image()
        else:
            self.show_no_images_message()
    
    def show_no_images_message(self):
        """Show a message when no images are found"""
        self.image_label.configure(image="", text="No visualization files found.\nRun the accuracy test and visualization script first.")
        self.image_counter.configure(text="0/0")
        self.image_info.configure(text="")
        self.update_navigation_buttons()

def main():
    """Main function to run the visualization viewer"""
    print("🔍 Resume Scoring Accuracy Visualization Viewer")
    print("=" * 50)
    print("Starting GUI application...")
    
    try:
        root = tk.Tk()
        app = VisualizationViewer(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("Falling back to file listing...")
        
        # Fallback: just list the files
        files = glob.glob("*.png")
        if files:
            print("\nAvailable visualization files:")
            for file in sorted(files, key=os.path.getmtime, reverse=True):
                print(f"  - {file}")
        else:
            print("No visualization files found.")

if __name__ == "__main__":
    main()