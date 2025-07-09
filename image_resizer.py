import os
from tkinter import filedialog, Tk, Label, Entry, Button, StringVar, messagebox
from PIL import Image

# Function to resize image
def resize_image(image_path, output_folder, width, height, percent=None):
    img = Image.open(image_path)
    original_size = img.size

    # If percentage is given, calculate new width and height
    if percent:
        width = int(original_size[0] * percent / 100)
        height = int(original_size[1] * percent / 100)
    
    resized_img = img.resize((width, height))

    # Save the resized image
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    new_name = f"{name}_resized{ext}"
    save_path = os.path.join(output_folder, new_name)

    resized_img.save(save_path)
    return original_size, (width, height)

# Choose image files
def choose_files():
    files = filedialog.askopenfilenames(
        title="Choose images",
        filetypes=[("Image files", "*.jpg *.png *.jpeg")]
    )
    if files:
        selected_files.set(", ".join(files))
        print("Selected files:", files)

# Choose folder to save resized images
def choose_output_folder():
    folder = filedialog.askdirectory(title="Choose output folder")
    if folder:
        output_folder.set(folder)

# Start the resizing process
def start_resizing():
    files = root.tk.splitlist(selected_files.get())
    folder = output_folder.get()
    width = width_var.get()
    height = height_var.get()
    percent = percent_var.get()

    if not files or not folder:
        messagebox.showerror("Error", "Please select images and output folder.")
        return
    
    try:
        percent_val = int(percent) if percent.strip() else None

        if percent_val:
            width = height = 0  # Will be overridden by percent
        else:
            if not width.strip() or not height.strip():
                messagebox.showerror("Error", "Enter width & height OR percentage.")
                return
            width = int(width)
            height = int(height)

        for file in files:
            original, resized = resize_image(file, folder, width, height, percent_val)
            print(f"{file}: {original} → {resized}")

        messagebox.showinfo("Done", "Images resized successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {str(e)}")

# GUI setup
root = Tk()
root.title("Advanced Image Resizer")
root.geometry("500x400")

selected_files = StringVar()
output_folder = StringVar()
width_var = StringVar()
height_var = StringVar()
percent_var = StringVar()

# GUI Widgets
Label(root, text="1. Select Images").pack()
Button(root, text="Choose Images", command=choose_files).pack(pady=5)

Label(root, text="2. Select Output Folder").pack()
Button(root, text="Choose Folder", command=choose_output_folder).pack(pady=5)

Label(root, text="3. Resize Settings").pack()
Label(root, text="Width (px):").pack()
Entry(root, textvariable=width_var).pack()

Label(root, text="Height (px):").pack()
Entry(root, textvariable=height_var).pack()

Label(root, text="OR Resize % (Overrides Width/Height)").pack()
Entry(root, textvariable=percent_var).pack()

Button(root, text="Resize Images", bg="green", fg="white", command=start_resizing).pack(pady=20)

# Start the GUI
root.mainloop()
