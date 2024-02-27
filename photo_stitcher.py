import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading


class PhotoStitcherGUI:
    def __init__(self, root):
        self.loading_label = None
        self.root = root
        self.root.title("პოტოები შემაერთებელი")
        self.images = []  # This will store the PhotoImage objects for display
        self.image_paths = []
        self.selected_index = None  # To keep track of which image is selected

        # Canvas for displaying thumbnails
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        # self.canvas.bind("<Button-1>", self.select_thumbnail)  # Bind left mouse click to select a thumbnail
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Frame for buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.Y, side=tk.RIGHT)

        # Buttons
        self.btn_add_photos = tk.Button(self.button_frame, text="დაამატე ფოტო", command=self.add_photos)
        self.btn_add_photos.pack(fill=tk.X)

        self.btn_remove_photo = tk.Button(self.button_frame, text="წაშალე მონიშნული", command=self.remove_photo)
        self.btn_remove_photo.pack(fill=tk.X)

        self.btn_move_up = tk.Button(self.button_frame, text="გადაანაცვლე ზემოთ", command=lambda: self.move_photo(-1))
        self.btn_move_up.pack(fill=tk.X)

        self.btn_move_down = tk.Button(self.button_frame, text="გადაანაცვლე ქვემოთ", command=lambda: self.move_photo(1))
        self.btn_move_down.pack(fill=tk.X)

        # Transformations frame
        self.transform_frame = tk.Frame(self.button_frame)
        self.transform_frame.pack(fill=tk.X)

        # Transformation buttons
        self.btn_rotate_left = tk.Button(self.transform_frame, text="შეატრიალე მარცხნივ", command=self.rotate_left)
        self.btn_rotate_left.pack(side=tk.LEFT)

        self.btn_rotate_right = tk.Button(self.transform_frame, text="შეატრიალე მარჯვნივ", command=self.rotate_right)
        self.btn_rotate_right.pack(side=tk.LEFT)

        self.btn_mirror_horizontal = tk.Button(self.transform_frame, text="შეარეველე ჰორიზონტალურად",
                                               command=self.mirror_horizontal)
        self.btn_mirror_horizontal.pack(side=tk.LEFT)

        self.btn_mirror_vertical = tk.Button(self.transform_frame, text="შეარეველე ვერტიკალურად",
                                             command=self.mirror_vertical)
        self.btn_mirror_vertical.pack(side=tk.LEFT)

        #exports
        self.btn_stitch_horizontal = tk.Button(self.button_frame, text="შეაერთე ჰორიზონტალურად",
                                               command=lambda: self.stitch_photos_thread('horizontal'))
        self.btn_stitch_horizontal.pack(fill=tk.X)

        self.btn_stitch_vertical = tk.Button(self.button_frame, text="შეაერთე ვერტიკალურად",
                                             command=lambda: self.stitch_photos_thread('vertical'))
        self.btn_stitch_vertical.pack(fill=tk.X)



    def rotate_left(self):
        if self.selected_index is not None:
            self.rotate_image(-90)

    def rotate_right(self):
        if self.selected_index is not None:
            self.rotate_image(90)

    def mirror_horizontal(self):
        if self.selected_index is not None:
            self.mirror_image('horizontal')

    def mirror_vertical(self):
        if self.selected_index is not None:
            self.mirror_image('vertical')

    def rotate_image(self, angle):
        path = self.image_paths[self.selected_index]
        img = Image.open(path)
        img = img.rotate(angle, expand=True)
        img.save(path)
        self.update_thumbnails()

    def mirror_image(self, direction):
        path = self.image_paths[self.selected_index]
        img = Image.open(path)
        if direction == 'horizontal':
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        else:  # vertical
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img.save(path)
        self.update_thumbnails()

    def add_photos(self):
        file_paths = filedialog.askopenfilenames(title="აირჩიე ფოტო",
                                                 filetypes=(("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"),
                                                            ("All files", "*.*")))
        for path in file_paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
        self.update_thumbnails()

    def remove_photo(self):
        if self.selected_index is not None and 0 <= self.selected_index < len(self.image_paths):
            del self.image_paths[self.selected_index]
            self.selected_index = None  # Reset selection
            self.update_thumbnails()

    def move_photo(self, direction):
        if self.selected_index is None:
            return

        new_index = self.selected_index + direction
        if 0 <= new_index < len(self.image_paths):
            # Swap the selected photo with its neighbor
            self.image_paths[self.selected_index], self.image_paths[new_index] = self.image_paths[new_index], \
                self.image_paths[self.selected_index]
            self.selected_index = new_index  # Update the selected index to follow the moved photo
            self.update_thumbnails()
            self.highlight_selected()

    def select_thumbnail(self, event):
        # Assuming thumbnails are 100x100 pixels spaced by 10 pixels
        index = event.y // 110  # Calculate which thumbnail was clicked
        if index < len(self.image_paths):
            self.selected_index = index
            self.highlight_selected()

    def highlight_selected(self):
        # Assuming you have variables or a way to determine the selected image index
        selected_index = self.selected_index  # Placeholder for the actual way you determine this
        thumbnail_size = 100  # Should match the size used in update_thumbnails
        padding = 10  # Should match the padding used in update_thumbnails
        thumbnails_per_row = 4  # Should match the count used in update_thumbnails

        if selected_index is not None:  # Check if there's a selected image
            row = selected_index // thumbnails_per_row
            col = selected_index % thumbnails_per_row
            x_position = (col * (thumbnail_size + padding)) + padding
            y_position = (row * (thumbnail_size + padding)) + padding

            # Adjust highlight size if necessary
            highlight_padding = 5  # Adjust if you want some space between the thumbnail and highlight
            highlight_size = thumbnail_size + 2 * highlight_padding

            # Clear previous highlights if any
            self.canvas.delete("highlight")

            # Create a new highlight
            self.canvas.create_rectangle(x_position - highlight_padding, y_position - highlight_padding,
                                         x_position + highlight_size - highlight_padding,
                                         y_position + highlight_size - highlight_padding,
                                         outline="red", width=2, tags="highlight")

    def on_canvas_click(self, event):
        # Constants used in thumbnail layout
        thumbnail_size = 100  # Same as used in update_thumbnails
        padding = 10  # Space between thumbnails
        thumbnails_per_row = 4

        # Calculate clicked row and column based on event.x and event.y
        col = event.x // (thumbnail_size + padding)
        row = event.y // (thumbnail_size + padding)

        # Calculate index of clicked image
        index = row * thumbnails_per_row + col

        if index < len(self.image_paths):
            # Check if the click is within the bounds of the actual images
            self.selected_index = index
            self.highlight_selected()
        else:
            # Click was outside of any image, you can handle this case if needed
            pass

    def update_thumbnails(self):
        self.canvas.delete("all")  # Clear existing thumbnails
        self.images.clear()  # Clear old references
        thumbnail_size = 100  # Fixed size for thumbnails
        padding = 10  # Space between thumbnails
        thumbnails_per_row = 4
        row_width = thumbnail_size * thumbnails_per_row + padding * (thumbnails_per_row - 1)

        for i, path in enumerate(self.image_paths):
            img = Image.open(path)
            # Resize image to fill the square while maintaining aspect ratio
            img.thumbnail((thumbnail_size, thumbnail_size))
            photo = ImageTk.PhotoImage(img)
            self.images.append(photo)  # Keep reference

            # Calculate position
            row = i // thumbnails_per_row
            col = i % thumbnails_per_row
            x_position = (col * (thumbnail_size + padding)) + padding
            y_position = (row * (thumbnail_size + padding)) + padding

            self.canvas.create_image(x_position, y_position, anchor=tk.NW, image=photo)

        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))  # Update scroll region

        # Ensure the canvas is large enough to hold the last row of thumbnails
        self.canvas.config(width=row_width + padding * 2, height=((len(self.image_paths) // thumbnails_per_row + 1) * (
                thumbnail_size + padding)) + padding)

    def display_loading_message(self, show):
        if show:
            # Display loading message
            self.loading_label = tk.Label(self.root, text="Stitching photos, please wait...")
            self.loading_label.pack()  # Make sure to pack or place the label so it becomes visible
        else:
            # Hide loading message
            if self.loading_label is not None:
                self.loading_label.destroy()
                self.loading_label = None  # Reset self.loading_label to None after destroying it

    def stitch_photos_thread(self, direction):
        self.display_loading_message(True)
        self.root.update_idletasks()  # Force UI update

        # Run the stitching operation in a separate thread to prevent UI blocking
        threading.Thread(target=lambda: self.stitch_photos(direction), daemon=True).start()

    def stitch_photos(self, direction):
        if not self.image_paths:
            messagebox.showerror("Error", "No images to stitch.")
            return

        # Load images
        images = [Image.open(img_path) for img_path in self.image_paths]

        if direction == 'horizontal':
            # Target height is the minimum height of all images
            target_height = min(img.height for img in images)
            # Resize images to have the same height
            resized_images = [
                img.resize((int(img.width * target_height / img.height), target_height), Image.Resampling.LANCZOS) for
                img in images]
            # Stitch images horizontally
            total_width = sum(img.width for img in resized_images)
            new_img = Image.new('RGB', (total_width, target_height))
            x_offset = 0
            for img in resized_images:
                new_img.paste(img, (x_offset, 0))
                x_offset += img.width
        else:  # vertical
            # Target width is the minimum width of all images
            target_width = min(img.width for img in images)
            # Resize images to have the same width
            resized_images = [
                img.resize((target_width, int(img.height * target_width / img.width)), Image.Resampling.LANCZOS) for img
                in images]
            # Stitch images vertically
            total_height = sum(img.height for img in resized_images)
            new_img = Image.new('RGB', (target_width, total_height))
            y_offset = 0
            for img in resized_images:
                new_img.paste(img, (0, y_offset))
                y_offset += img.height

        self.root.after(0, self.display_loading_message, False)
        # Open save dialog after stitching
        self.save_stitched_image(new_img)

    def save_stitched_image(self, img):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"),
                                                            ("All files", "*.*")])
        if file_path:
            img.save(file_path)
            messagebox.showinfo("Success", "Image saved successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoStitcherGUI(root)
    root.mainloop()
