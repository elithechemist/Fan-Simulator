import tkinter as tk
import math
import tkinter.messagebox as messagebox

class FanSimulator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fan Simulator with Camera Framerate")
        self.geometry("900x500")  # Increase the initial size

        self.show_startup_message()

        self.canvas = tk.Canvas(self, bg="black", bd=2, relief=tk.RIDGE)
        self.canvas.pack(pady=20, padx=20, expand=True, fill=tk.BOTH)

        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=10)

        self.blade_label = tk.Label(self.control_frame, text="Number of Blades:")
        self.blade_label.pack(side=tk.LEFT, padx=5)
        self.blade_entry = tk.Entry(self.control_frame, width=10)
        self.blade_entry.pack(side=tk.LEFT, padx=5)

        self.freq_label = tk.Label(self.control_frame, text="Frequency (RPS):")
        self.freq_label.pack(side=tk.LEFT, padx=5)
        self.freq_entry = tk.Entry(self.control_frame, width=10)
        self.freq_entry.pack(side=tk.LEFT, padx=5)

        self.camera_label = tk.Label(self.control_frame, text="Camera Framerate (FPS):")
        self.camera_label.pack(side=tk.LEFT, padx=5)
        self.camera_entry = tk.Entry(self.control_frame, width=10)
        self.camera_entry.pack(side=tk.LEFT, padx=5)

        self.toggle_color_btn = tk.Button(self.control_frame, text="Blade Color: White", bg="white", fg="black", command=self.toggle_blade_color)
        self.toggle_color_btn.pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(self.control_frame, text="Start", command=self.start_simulation, bg="green")
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(self.control_frame, text="Stop", command=self.stop_simulation, bg="red")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Create the status label on the canvas
        self.status_text = self.canvas.create_text(10, 10, text="", anchor=tk.NW, fill="green", font=("Arial", 12, "bold"))

        self.blades = 0
        self.freq = 0
        self.camera_interval = 0
        self.special_blade_red = False
        self.precomputed_angles = []
        self.current_index = 0

    def calculate_angles(self, fps, rps):
        num_frames = int(60 * fps)
        times = [i / fps for i in range(num_frames)]
        return [2 * math.pi * rps * t for t in times]

    def draw_fan(self):
        self.canvas.delete("fan")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx, cy = canvas_width // 2, canvas_height // 2
        radius = min(canvas_width, canvas_height) * 0.4

        current_angle = self.precomputed_angles[self.current_index]

        for i in range(self.blades):
            color = "red" if self.special_blade_red and i == 0 else "white"
            x = cx + radius * math.cos(2 * math.pi * i / self.blades + current_angle)
            y = cy + radius * math.sin(2 * math.pi * i / self.blades + current_angle)
            self.canvas.create_line(cx, cy, x, y, tags="fan", fill=color)

        if self.is_simulating and self.current_index < len(self.precomputed_angles) - 1:
            self.current_index += 1
            self.after(self.camera_interval, self.draw_fan)

    def toggle_blade_color(self):
        self.special_blade_red = not self.special_blade_red
        if self.special_blade_red:
            self.toggle_color_btn.config(text="Blades Marked", bg="red", fg="white")
        else:
            self.toggle_color_btn.config(text="Blades Unmarked", bg="white", fg="black")
        self.draw_fan()

    def start_simulation(self):
        try:
            self.blades = int(self.blade_entry.get())
            self.freq = float(self.freq_entry.get())
            camera_fps = float(self.camera_entry.get())
            self.camera_interval = int(1000 / camera_fps)
            self.precomputed_angles = self.calculate_angles(camera_fps, self.freq)
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid Input!")
            return

        if self.blades <= 0 or self.freq <= 0 or camera_fps <= 0:
            tk.messagebox.showerror("Error", "Blades, frequency, and framerate must be positive values!")
            return

        self.is_simulating = True
        self.current_index = 0
        self.draw_fan()
        self.after(60000, self.stop_simulation)  # Auto-stop the simulation after 60 seconds
        # Update the status text on the canvas
        self.canvas.itemconfig(self.status_text, text="Simulation Running...", fill="green")

    def stop_simulation(self):
        self.is_simulating = False
        self.canvas.delete("fan")
        # Update the status text on the canvas
        self.canvas.itemconfig(self.status_text, text="Simulation Stopped.", fill="red")

    def show_startup_message(self):
        # Create a new top-level window for the message
        message_window = tk.Toplevel(self)
        message_window.title("Welcome to Fan Simulator")

        # Ensuring the popup is on top and grabs all events
        message_window.grab_set()
        message_window.transient(self)

        # Format the message with labels, using font properties for bold and italics
        header_label = tk.Label(message_window, text="Welcome to Fan Simulator", font=("Arial", 14, "bold"), fg="blue")
        header_label.pack(pady=10)

        warning_label = tk.Label(message_window, text=("WARNING:\n"
                "Frequencies and frame rates under 10 are ideal for visualization.\n"
                "The stroboscopic effect is best visualized when the difference between frequencies is very small "
                "(less than one frame per second)."), font=("Arial", 12, "italic"), fg="red")
        warning_label.pack(pady=10)

        ip_label = tk.Label(message_window, text="Intellectual Property:", font=("Arial", 12, "bold"))
        ip_label.pack()

        ip_content_label = tk.Label(message_window, text="This program is the intellectual property of Eli Jones.", font=("Arial", 12, "bold"), fg="green")
        ip_content_label.pack(pady=2)

        permissions_label = tk.Label(message_window, text="Permission is granted to use this software for non-commercial purposes only. Please credit the author when sharing or referencing.", font=("Arial", 12))
        permissions_label.pack(pady=5)

        instruction_label = tk.Label(message_window, text="How to use:\nInput the desired parameters and press Start to begin the simulation.\nToggle the blade color if needed and stop the simulation when done.", font=("Arial", 12))
        instruction_label.pack(pady=10)

        ok_button = tk.Button(message_window, text="OK", command=message_window.destroy)
        ok_button.pack(pady=10)

if __name__ == "__main__":
    app = FanSimulator()
    app.mainloop()
