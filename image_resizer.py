import os
import json
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, StringVar, BooleanVar
from tkinterdnd2 import TkinterDnD, DND_FILES
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageDraw, ImageFont

def add_placeholder(entry, placeholder):
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(foreground="black")
    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground="gray")
    entry.insert(0, placeholder)
    entry.config(foreground="gray")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

class AdvancedImageProcessor:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.style = ttk.Style("superhero")
        self.style.master = self.root
        self.settings_file = "image_processor_settings.json"
        self.settings = self.load_settings()

        # Variables
        self.selected_files = StringVar()
        self.output_folder = StringVar()
        self.percent_var = StringVar(value="80")
        self.format_var = StringVar(value="WEBP")
        self.mode_var = StringVar(value="resize")
        self.quality_var = StringVar(value="85")
        self.watermark_text = StringVar()
        self.preserve_metadata = BooleanVar(value=True)
        self.optimize_compression = BooleanVar(value=True)
        self.naming_var = StringVar(value="{filename}_{operation}")
        self.watermark_position = StringVar(value="bottom-right")
        self.watermark_opacity = StringVar(value="128")
        self.current_files = []
        self.is_processing = False

        self.create_widgets()
        self.setup_window()
        self.apply_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "theme": "superhero",
            "last_output_folder": "",
            "default_quality": 85,
            "default_format": "WEBP",
        }

    def save_settings(self):
        try:
            self.settings.update({
                "last_output_folder": self.output_folder.get(),
                "default_quality": int(self.quality_var.get()) if self.quality_var.get().isdigit() else 85,
                "default_format": self.format_var.get()
            })
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def apply_settings(self):
        if self.settings.get("last_output_folder"):
            self.output_folder.set(self.settings["last_output_folder"])
        self.quality_var.set(str(self.settings.get("default_quality", 85)))
        self.format_var.set(self.settings.get("default_format", "WEBP"))

    def create_widgets(self):
        self.root.title("Advanced Image Processor Pro")
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Advanced Image Resizer & Converter", font=("Segoe UI", 18, "bold")).pack(pady=(10, 10))

        # File Selection
        select_frame = ttk.LabelFrame(main_frame, text="File Selection")
        select_frame.pack(fill="x", pady=8)
        ttk.Button(select_frame, text="Choose Images", command=self.choose_images, bootstyle=PRIMARY).pack(side="left", padx=5, pady=6)
        ttk.Button(select_frame, text="Output Folder", command=self.choose_folder, bootstyle=SUCCESS).pack(side="left", padx=5, pady=6)
        self.file_count_label = ttk.Label(select_frame, text="No files selected", font=("Segoe UI", 9))
        self.file_count_label.pack(side="left", padx=12)

        # Drag & Drop
        drop_area = ttk.Label(main_frame, text="🖱️ Drop images here", bootstyle="info", width=35, anchor="center", font=("Segoe UI", 10, "italic"))
        drop_area.pack(pady=8)
        drop_area.drop_target_register(DND_FILES)
        drop_area.dnd_bind('<<Drop>>', self.on_drop)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.pack(fill="x", pady=8)
        modes = ttk.Frame(options_frame)
        modes.pack()
        ttk.Radiobutton(modes, text="Resize", variable=self.mode_var, value="resize", bootstyle=PRIMARY).pack(side="left", padx=5)
        ttk.Radiobutton(modes, text="Convert", variable=self.mode_var, value="convert", bootstyle=INFO).pack(side="left", padx=5)

        ttk.Label(options_frame, text="Resize %:").pack(anchor="w")
        ttk.Entry(options_frame, textvariable=self.percent_var, width=10).pack(anchor="w", pady=2)

        ttk.Label(options_frame, text="Quality (1-100):").pack(anchor="w")
        ttk.Entry(options_frame, textvariable=self.quality_var, width=10).pack(anchor="w", pady=2)

        ttk.Label(options_frame, text="Output Format:").pack(anchor="w")
        ttk.Combobox(options_frame, textvariable=self.format_var, values=["WEBP", "PNG", "JPEG", "JPG", "AVIF", "BMP", "TIFF"], state="readonly", width=10).pack(anchor="w", pady=2)

        ttk.Checkbutton(options_frame, text="Preserve EXIF metadata", variable=self.preserve_metadata).pack(anchor="w")
        ttk.Checkbutton(options_frame, text="Optimize Compression", variable=self.optimize_compression).pack(anchor="w")

        ttk.Label(options_frame, text="Output Naming Pattern:").pack(anchor="w")
        ttk.Entry(options_frame, textvariable=self.naming_var, width=30).pack(anchor="w", pady=2)

        # Watermarking
        wm_frame = ttk.LabelFrame(main_frame, text="Watermark", padding=8)
        wm_frame.pack(fill="x", pady=8)
        ttk.Label(wm_frame, text="Text:").pack(anchor="w")
        wm_entry = ttk.Entry(wm_frame, textvariable=self.watermark_text, width=25)
        wm_entry.pack(anchor="w", pady=2)
        add_placeholder(wm_entry, "Enter watermark text...")
        ttk.Label(wm_frame, text="Position:").pack(anchor="w")
        ttk.Combobox(wm_frame, textvariable=self.watermark_position, values=["top-left","top-right","bottom-left","bottom-right","center"], state="readonly", width=12).pack(anchor="w", pady=2)
        ttk.Label(wm_frame, text="Opacity (50-255):").pack(anchor="w")
        ttk.Entry(wm_frame, textvariable=self.watermark_opacity, width=10).pack(anchor="w", pady=2)

        # Progress & Buttons
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', bootstyle="success-striped")
        self.progress_bar.pack(fill="x", pady=14)
        self.progress_label = ttk.Label(main_frame, text="Ready to process images", font=("Segoe UI", 9))
        self.progress_label.pack()

        btns = ttk.Frame(main_frame)
        btns.pack(pady=12)
        ttk.Button(btns, text="Start", command=self.start_processing, bootstyle=SUCCESS, width=20).pack(side="left", padx=10)
        ttk.Button(btns, text="Clear", command=self.clear_all, bootstyle=SECONDARY, width=10).pack(side="left", padx=10)

    def setup_window(self):
        self.root.geometry("550x750")
        self.root.minsize(500, 600)
        self.root.resizable(False, False)

    def choose_images(self):
        files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.avif")])
        if files:
            self.current_files = list(files)
            self.selected_files.set(", ".join(files))
            self.update_file_count()

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        image_files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".avif"))]
        if image_files:
            self.current_files = image_files
            self.selected_files.set(", ".join(image_files))
            self.update_file_count()
            messagebox.showinfo("Files Added", f"{len(image_files)} image(s) added.")
        else:
            messagebox.showwarning("Invalid", "No supported image files.")

    def update_file_count(self):
        count = len(self.current_files)
        self.file_count_label.config(text=f"{count} file(s) selected" if count else "No files selected")

    def add_watermark(self, img, text, position, opacity):
        if not text.strip():
            return img
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        font_size = max(16, min(img.size) // 30)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        margin = 20
        positions = {
            "top-left": (margin, margin),
            "top-right": (img.width - text_w - margin, margin),
            "bottom-left": (margin, img.height - text_h - margin),
            "bottom-right": (img.width - text_w - margin, img.height - text_h - margin),
            "center": ((img.width - text_w) // 2, (img.height - text_h) // 2)
        }
        draw.text(positions.get(position, (margin, margin)), text, font=font, fill=(255, 255, 255, int(opacity)))
        return Image.alpha_composite(img.convert("RGBA"), overlay).convert(img.mode)

    def process_single_image(self, img_path, output_folder, settings):
        try:
            with Image.open(img_path) as img:
                img_copy = img.copy()
                if settings['mode'] == "resize":
                    percent = settings['percent']
                    new_size = (int(img.width * percent / 100), int(img.height * percent / 100))
                    img_copy = img_copy.resize(new_size, Image.Resampling.LANCZOS)
                if settings['watermark_text']:
                    img_copy = self.add_watermark(img_copy, settings['watermark_text'], settings['watermark_position'], settings['watermark_opacity'])

                output_format = settings['format'].upper()
                base_name = Path(img_path).stem
                out_name = settings['naming_pattern'].format(
                    filename=base_name,
                    operation=settings['mode'],
                    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
                    format=output_format.lower()
                )
                out_path = Path(output_folder) / f"{out_name}.{output_format.lower()}"
                save_kwargs = {"format": output_format}

                if settings['preserve_metadata'] and 'exif' in img.info:
                    save_kwargs['exif'] = img.info['exif']

                if output_format in ["JPEG", "JPG"]:
                    img_copy = img_copy.convert("RGB")
                    save_kwargs['quality'] = settings['quality']
                    if settings['optimize_compression']:
                        save_kwargs['optimize'] = True
                elif output_format == "WEBP":
                    save_kwargs['quality'] = settings['quality']
                elif output_format == "PNG":
                    save_kwargs['compress_level'] = 6

                img_copy.save(out_path, **save_kwargs)
                return str(out_path)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            return None

    def start_processing(self):
        if not self.current_files:
            messagebox.showwarning("No Files", "Select image files to process")
            return
        if not self.output_folder.get():
            messagebox.showwarning("No Folder", "Select output folder")
            return
        try:
            quality = int(self.quality_var.get())
            percent = int(self.percent_var.get())
            opacity = int(self.watermark_opacity.get())
            if not (1 <= quality <= 100 and 1 <= percent <= 500 and 50 <= opacity <= 255):
                raise ValueError("Invalid input values")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.processing_settings = {
            'mode': self.mode_var.get(),
            'percent': percent,
            'quality': quality,
            'format': self.format_var.get(),
            'watermark_text': self.watermark_text.get(),
            'watermark_position': self.watermark_position.get(),
            'watermark_opacity': opacity,
            'preserve_metadata': self.preserve_metadata.get(),
            'optimize_compression': self.optimize_compression.get(),
            'naming_pattern': self.naming_var.get()
        }

        self.is_processing = True
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(self.current_files)
        self.progress_label.config(text="Processing images...")
        threading.Thread(target=self.process_images_threaded, daemon=True).start()

    def process_images_threaded(self):
        success, fail = 0, 0
        for i, path in enumerate(self.current_files):
            if not self.is_processing: break
            result = self.process_single_image(path, self.output_folder.get(), self.processing_settings)
            if result:
                success += 1
            else:
                fail += 1
            self.root.after(0, lambda val=i+1: self.update_progress(val))
        self.root.after(0, lambda: self.processing_complete(success, fail))

    def update_progress(self, val):
        self.progress_bar['value'] = val
        self.progress_label.config(text=f"Processing {val} of {len(self.current_files)}")

    def processing_complete(self, success, fail):
        self.is_processing = False
        self.progress_label.config(text=f"✅ Done: {success} succeeded, {fail} failed")
        self.save_settings()
        messagebox.showinfo("Completed", f"Processed: {success}\nFailed: {fail}\nSaved to: {self.output_folder.get()}")

    def clear_all(self):
        self.current_files = []
        self.selected_files.set("")
        self.progress_bar['value'] = 0
        self.file_count_label.config(text="No files selected")
        self.progress_label.config(text="Ready to process images")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedImageProcessor()
    app.run()
