import tkinter as tk
from tkinter import ttk

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack()

        # Dropdown menu for selecting drawing mode
        self.mode = tk.StringVar(value="brush")
        mode_menu = ttk.OptionMenu(root, self.mode, "brush", "line", "eraser", "select", command=self.update_mode)
        mode_menu.pack()

        # Scale for adjusting line thickness
        self.line_thickness = tk.IntVar(value=2)  # Default thickness set to 2
        thickness_scale = ttk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.line_thickness)
        thickness_scale.pack()
        ttk.Label(root, text="Line Thickness").pack()

        # Variables to store line start point and shapes drawn
        self.start_x = None
        self.start_y = None
        self.drawn_shapes = []  # List of shapes with their properties
        self.selected_shapes = []  # List of selected shapes

        # Initial mode setup
        self.update_mode("brush")

        # Keybindings for copying and moving shapes
        self.root.bind("<Control-c>", self.copy_selected)
        self.root.bind("<Control-v>", self.paste_copied)
        self.root.bind("<Control-x>", self.cut_selected)

        self.copied_shapes = None  # Store copied shapes

    def update_mode(self, mode):
        # Unbind existing bindings
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        
        if mode == "brush":
            # Bindings for brush drawing mode
            self.canvas.bind("<B1-Motion>", self.draw_brush)
        elif mode == "line":
            # Bindings for line drawing mode
            self.canvas.bind("<Button-1>", self.on_left_button_down)
            self.canvas.bind("<ButtonRelease-1>", self.on_left_button_up)
        elif mode == "eraser":
            # Bindings for eraser mode
            self.canvas.bind("<Button-1>", self.erase_line)
        elif mode == "select":
            # Bindings for selection mode
            self.canvas.bind("<Button-1>", self.select_shape)
            self.canvas.bind("<B1-Motion>", self.move_selected_shape)
            self.canvas.bind("<ButtonRelease-1>", self.clear_selection)

    def draw_brush(self, event):
        x, y = event.x, event.y
        # Draw an oval with thickness based on line_thickness
        thickness = self.line_thickness.get()
        oval = self.canvas.create_oval(x - thickness, y - thickness, x + thickness, y + thickness, fill="black")
        # Add to drawn_shapes list
        self.drawn_shapes.append({"type": "oval", "id": oval, "x": x, "y": y, "thickness": thickness})

    def on_left_button_down(self, event):
        # Record the starting point of the line
        self.start_x, self.start_y = event.x, event.y

    def on_left_button_up(self, event):
        # Draw a line from the starting point to the current point with line thickness
        end_x, end_y = event.x, event.y
        thickness = self.line_thickness.get()
        line = self.canvas.create_line(self.start_x, self.start_y, end_x, end_y, fill="black", width=thickness)
        # Add to drawn_shapes list
        self.drawn_shapes.append({"type": "line", "id": line, "start": (self.start_x, self.start_y), "end": (end_x, end_y), "thickness": thickness})

    def erase_line(self, event):
        # Check if the click event is near any drawn shape
        for shape in self.drawn_shapes:
            # Get the bounding box of the shape
            bbox = self.canvas.bbox(shape["id"])
            if bbox and bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
                # Delete the shape from the canvas and remove it from the list
                self.canvas.delete(shape["id"])
                self.drawn_shapes.remove(shape)
                break

    def select_shape(self, event):
        # Select shape based on click event coordinates
        x, y = event.x, event.y
        for shape in self.drawn_shapes:
            # Get the bounding box of the shape
            bbox = self.canvas.bbox(shape["id"])
            if bbox and bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                # Add shape to the selected shapes list
                if shape not in self.selected_shapes:
                    self.selected_shapes.append(shape)
                    # Optionally highlight the selected shape
                    self.canvas.itemconfigure(shape["id"], outline="blue", width=shape.get("thickness", 2) + 2)
                break

    def move_selected_shape(self, event):
        # Move the selected shapes based on mouse motion
        if self.selected_shapes:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            for shape in self.selected_shapes:
                if shape["type"] == "line":
                    # Move the line by dx, dy
                    start_x, start_y = shape["start"]
                    end_x, end_y = shape["end"]
                    new_start_x, new_start_y = start_x + dx, start_y + dy
                    new_end_x, new_end_y = end_x + dx, end_y + dy
                    self.canvas.coords(shape["id"], new_start_x, new_start_y, new_end_x, new_end_y)
                    shape["start"] = (new_start_x, new_start_y)
                    shape["end"] = (new_end_x, new_end_y)
                elif shape["type"] == "oval":
                    # Move the oval by dx, dy
                    self.canvas.move(shape["id"], dx, dy)
                    shape["x"] += dx
                    shape["y"] += dy

            # Update the start coordinates for the next motion event
            self.start_x, self.start_y = event.x, event.y

    def clear_selection(self, event):
        # Clear the selection
        for shape in self.selected_shapes:
            # Remove the highlight from the selected shape
            self.canvas.itemconfigure(shape["id"], outline="", width=shape.get("thickness", 2))
        self.selected_shapes = []

    def copy_selected(self, event):
        # Copy the selected shapes
        if self.selected_shapes:
            self.copied_shapes = []
            for shape in self.selected_shapes:
                self.copied_shapes.append(shape.copy())

    def paste_copied(self, event):
        # Paste the copied shapes
        if self.copied_shapes:
            # Calculate the offset for pasting
            offset = 20
            for shape in self.copied_shapes:
                new_shape = shape.copy()
                shape_type = new_shape["type"]

                if shape_type == "line":
                    # Adjust the coordinates of the line
                    new_start = (shape["start"][0] + offset, shape["start"][1] + offset)
                    new_end = (shape["end"][0] + offset, shape["end"][1] + offset)
                    new_line_id = self.canvas.create_line(new_start[0], new_start[1], new_end[0], new_end[1], fill="black", width=shape["thickness"])
                    # Store the new line shape
                    new_shape["id"] = new_line_id
                    new_shape["start"] = new_start
                    new_shape["end"] = new_end

                elif shape_type == "oval":
                    # Adjust the coordinates of the oval
                    new_x = shape["x"] + offset
                    new_y = shape["y"] + offset
                    thickness = shape["thickness"]
                    new_oval_id = self.canvas.create_oval(new_x - thickness, new_y - thickness, new_x + thickness, new_y + thickness, fill="black")
                    # Store the new oval shape
                    new_shape["id"] = new_oval_id
                    new_shape["x"] = new_x
                    new_shape["y"] = new_y

                # Add the new shape to drawn_shapes list
                self.drawn_shapes.append(new_shape)
            # Clear the copied shapes list after pasting
            self.copied_shapes = None
    
    def delete_selected(self, event):
        # Delete the selected shapes
        for shape in self.selected_shapes:
            self.canvas.delete(shape["id"])
            self.drawn_shapes.remove(shape)
        self.selected_shapes = []

    def cut_selected(self, event):
        # Cut the selected shapes by copying and then deleting them
        self.copy_selected(event)
        for shape in self.selected_shapes:
            self.canvas.delete(shape["id"])
            self.drawn_shapes.remove(shape)
        self.selected_shapes = []

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
