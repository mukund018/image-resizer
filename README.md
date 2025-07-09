# Advanced Image Resizer (Python + Tkinter)

This is a simple GUI-based Image Resizer built using Python and Tkinter. It allows you to resize multiple images either by specifying custom width and height or by giving a percentage scale.

## Features
- Select multiple image files (.jpg, .png, .jpeg)
- Choose an output folder to save resized images
- Resize using:
  - Specific Width & Height (in pixels), OR
  - Percentage (scales image by % and overrides width/height)
- Automatically saves resized images with a `_resized` suffix
- User-friendly graphical interface
- Built using the Pillow library for image processing

## Requirements
- Python 3.x
- Pillow (`pip install pillow`)

## How to Run
1. Make sure Python is installed on your system.
2. Install the Pillow library if not already installed:
3. Download or clone the project.
4. Run the script:

## How to Use
1. Click "Choose Images" to select one or more images.
2. Click "Choose Folder" to select where to save the resized images.
3. Enter either:
- Width and Height in pixels, OR
- Resize % (e.g., 50 to reduce size by half)
4. Click "Resize Images" to start.

All resized images will be saved in the selected folder with `_resized` added to the filename.

## Example
If you resize `cat.jpg` by 50%, it will generate `cat_resized.jpg` in the chosen output folder.

## Author
Created by Mukund K  
GitHub: [https://github.com/mukund018](https://github.com/mukund018)

