import tkinter as tk


class ComparisonGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.configure(width=400, height=200)
        self.pack_propagate(False)
        self.colors = {"active_bg": "white", "inactive_bg": "light grey",
                       "active_fg": "black", "inactive_fg": "grey"}

        """BASE GUI FRAMES"""

        self.stages_frame = tk.Frame(self, height=30)
        self.stages_frame.pack(fill="both")
        self.stages_frame.pack_propagate(False)

        self.animation_frame = tk.Frame(self, bg=self.colors["active_bg"])
        self.animation_frame.pack(fill="both", expand=True)

        self.loader_frame = tk.Frame(self, bg="blue")
        self.loader_frame.pack(fill="x")

        """STAGES OVERVIEW"""

        self.stage_1_frame = tk.Frame(self.stages_frame, bg=self.colors["active_bg"])
        self.stage_1_frame.pack(side="left", fill="both", expand=True)
        self.stage_1_frame.pack_propagate(False)

        self.stage_2_frame = tk.Frame(self.stages_frame, bg=self.colors["inactive_bg"])
        self.stage_2_frame.pack(side="left", fill="both", expand=True)
        self.stage_2_frame.pack_propagate(False)

        self.stage_3_frame = tk.Frame(self.stages_frame, bg=self.colors["inactive_bg"])
        self.stage_3_frame.pack(side="left", fill="both", expand=True)
        self.stage_3_frame.pack_propagate(False)

        self.stage_1_label = tk.Label(self.stage_1_frame, text="Extraction", bg=self.stage_1_frame.cget("bg"))
        self.stage_1_label.pack(fill="both", expand=True)

        self.stage_2_label = tk.Label(self.stage_2_frame, text="Comparison", bg=self.stage_2_frame.cget("bg"),
                                      fg=self.colors["inactive_fg"])
        self.stage_2_label.pack(fill="both", expand=True)

        self.stage_3_label = tk.Label(self.stage_3_frame, text="Results", bg=self.stage_3_frame.cget("bg"),
                                      fg=self.colors["inactive_fg"])
        self.stage_3_label.pack(fill="both", expand=True)

        self.add_stage_arrow(self.stage_1_frame)

    def add_stage_arrow(self, stage_frame):
        self.wait_visibility(stage_frame)
        width, height = int(stage_frame.winfo_height()/2), stage_frame.winfo_height()
        print(stage_frame.winfo_height())
        canvas = tk.Canvas(stage_frame, width=width, height=height, bg=self.colors["inactive_bg"], bd=0,
                           relief='ridge', highlightthickness=0)
        triangle_coords = (0, 0, width, height // 2, 0, height)
        canvas.create_polygon(triangle_coords, fill=self.colors["active_bg"], outline=self.colors["active_bg"])

        canvas.place(x=stage_frame.winfo_width()-width, y=0)

if __name__ == '__main__':
    cgui = ComparisonGUI()
    cgui.mainloop()
