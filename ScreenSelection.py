import tkinter as tk
import pyautogui
from PIL import Image, ImageTk
import json


class ScreenCapture:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)

        # Capture the screen using pyautogui
        self.screen = pyautogui.screenshot()
        self.screen_width, self.screen_height = self.screen.size
        self.screen_image = ImageTk.PhotoImage(self.screen)

        self.canvas = tk.Canvas(root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Set the captured screen image as the background
        self.canvas.create_image(0, 0, image=self.screen_image, anchor=tk.NW)
        self.canvas.config(width=self.screen_width, height=self.screen_height)

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = event.x, event.y
        print(f"Start coordinates: ({self.start_x}, {self.start_y})")
        print(f"End coordinates: ({end_x}, {end_y})")
        self.root.destroy()
        self.top_left = (self.start_x, self.start_y)
        self.bottom_right = (end_x, end_y)


def capture_screen():
    root = tk.Tk()
    app = ScreenCapture(root)
    root.mainloop()

    # Return the start and end coordinates after the capture is done
    start_coords = app.top_left
    end_coords = app.bottom_right

    # Save the coordinates to a JSON file
    config_data = {
        "screen_config": {
            "top_left": {"x": start_coords[0], "y": start_coords[1]},
            "bottom_right": {"x": end_coords[0], "y": end_coords[1]}
        }
    }
    with open("screen_config.json", "w") as json_file:
        json.dump(config_data, json_file, indent=4)

    return start_coords, end_coords


if __name__ == "__main__":
    start_coords, end_coords = capture_screen()
    print(start_coords[0],start_coords[1])
    print(f"Top-left: {start_coords}")
    print(f"Bottom-right: {end_coords}")