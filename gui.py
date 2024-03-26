import os.path
import tkinter as tk
from main import ImageCompare


class GUI(tk.Tk):
    def __init__(self, root_path):
        super().__init__()
        self.img_comp = ImageCompare(root_path)

        self.body = tk.Frame(self)
        self.body.pack(fill="both", expand=True)

        self.status_message_var = tk.StringVar()
        self.status_message_label = tk.Label(self.body, textvariable=self.status_message_var)
        self.status_message_label.pack()

        self.new_changes_var = tk.StringVar()
        self.new_changes_label = tk.Label(self.body, textvariable=self.new_changes_var)
        self.new_changes_label.pack()

        self.listen_for_changes()

        self.matches_frame = tk.Frame(self.body, bg="yellow")
        self.matches_frame.pack(fill="x", expand=True)

    def listen_for_changes(self):
        self.status_message_var.set("Listening for changes...")

        additions = self.img_comp.save_file_handler.update_save_file(write_to_file=False)["additions"]
        self.update_new_changes(additions)

        if len(additions) != 0:
            self.img_comp.update_features(write_to_file=False)

            for widgets in self.matches_frame.winfo_children():
                widgets.destroy()

            for addition in additions:
                matches = self.img_comp.compare_new_image(addition)
                self.add_matches_panel(addition, matches)

        self.after(3000, self.listen_for_changes)

    def update_new_changes(self, changes):
        self.new_changes_var.set(f"Added {len(changes)} image"
                                 f"{'s' if len(changes) != 1 else ''}")

    def add_matches_panel(self, new_image, matches):
        new_panel = tk.Frame(self.matches_frame, bg="red")

        new_img_frame = tk.Frame(new_panel)
        new_img_frame.pack(side="left", padx=3, pady=3)

        new_img_name_label = tk.Label(new_img_frame, text="NEW " + os.path.basename(new_image),
                                      bg=new_img_frame.cget("bg"))
        new_img_name_label.pack()

        new_img_label = tk.Label(new_img_frame, text="PLACEHOLDER\nIMAGE", bg="blue")
        new_img_label.pack()

        matches_frame = tk.Frame(new_panel, bg="grey")
        matches_frame.pack(side="right", fill="both", expand=True, padx=(0, 3), pady=3)

        tk.Label(matches_frame, text=str(matches), bg=new_panel.cget("bg")).pack()

        new_panel.pack(padx=3, pady=3, fill="x", expand=True)


if __name__ == '__main__':
    gui = GUI(root_path="./data/raw-img/cat")
    gui.mainloop()
