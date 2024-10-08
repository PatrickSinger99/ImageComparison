import tkinter as tk
from main import ImageCompare
from tkinter.font import Font
import threading
import os
from PIL import Image, ImageTk


class App(tk.Tk):

    colors = {
        "header": "white",
        "overview": "light grey",
        "match_details": "grey",
        "analysis_button_base": "medium sea green",
        "analysis_button_hover": "light sea green",
        "info_type": "sea green",
        "comparison_score": "sea green",
        "match_list_base_bg": "light grey",
        "match_list_hover_bg": "white",
        "match_list_active_bg": "sea green"
    }

    def __init__(self, save_file_path="savefile.json"):
        super().__init__()

        """INITIALIZE COMPARE"""
        self.save_file_path = save_file_path
        self.comparer = ImageCompare(savefile_path=save_file_path)

        """SESSION VARIABLES"""
        self.running_analysis = False
        self.matches = {}
        self.session_next_match_id = 0
        self.selected_match_id = None

        """METADATA"""
        self.title("Image Comparison")
        self.geometry("720x480")

        """HEADER"""

        self.header_frame = tk.Frame(self, bg=App.colors["header"])
        self.header_frame.pack(side="top", fill="x")

        """INFO FRAME"""

        self.info_frame = tk.Frame(self.header_frame, bg=self.header_frame.cget("bg"), relief="groove", bd=1)
        self.info_frame.pack(side="left", fill="both", expand=True)

        # Root Path Label
        tk.Label(self.info_frame, text="Root Path", bg=self.info_frame.cget("bg"), font=Font(weight="bold", size=9),
                 fg=App.colors["info_type"]).grid(row=0, column=0, sticky="e")
        self.root_directory_label = tk.Label(self.info_frame, text="", bg=self.info_frame.cget("bg"))
        self.root_directory_label.grid(row=0, column=1, sticky="w")

        # Num of Files Label
        tk.Label(self.info_frame, text="Loaded Files", bg=self.info_frame.cget("bg"), font=Font(weight="bold", size=9),
                 fg=App.colors["info_type"]).grid(row=1, column=0, sticky="e")
        self.num_files_label = tk.Label(self.info_frame, text="0", bg=self.info_frame.cget("bg"))
        self.num_files_label.grid(row=1, column=1, sticky="w")

        self.update_info()

        """ANALYSE USER OPTIONS"""

        self.analyze_frame = tk.Frame(self.header_frame, bg=self.header_frame.cget("bg"))
        self.analyze_frame.pack(side="right")

        # Include compared images
        self.include_compared_var = tk.BooleanVar(value=True)
        self.include_compared_checkbox = tk.Checkbutton(self.analyze_frame, text="Complete comparison", relief="groove",
                                                        variable=self.include_compared_var, cursor="hand2",
                                                        bg=self.analyze_frame.cget("bg"), font=Font(size=8))
        self.include_compared_checkbox.pack(side="bottom")

        # Start Analysis Button
        self.analyze_button = tk.Button(self.analyze_frame, text="Start Analysis", command=self.on_start_analysis,
                                        height=2, cursor="hand2", bg=App.colors["analysis_button_base"],
                                        relief="groove")
        self.analyze_button.bind("<Enter>", self._on_analyse_button_enter)
        self.analyze_button.bind("<Leave>", self._on_analyse_button_leave)
        self.analyze_button.pack(side="top", fill="x")

        """BODY"""

        self.body_frame = tk.Frame(self)
        self.body_frame.pack(side="bottom", fill="both", expand=True)

        # Matches Overview
        self.overview_frame = tk.Frame(self.body_frame, width=200, bg=App.colors["overview"])
        self.overview_frame.pack(side="left", fill="y")
        self.overview_frame.pack_propagate(False)

        self.matches_frame = ScrollableFrame(self.overview_frame)
        self.matches_frame.pack(fill="both", expand=True)

        # Match Detail
        self.detail_frame = tk.Frame(self.body_frame, bg=App.colors["match_details"])
        self.detail_frame.pack(side="right", fill="both", expand=True)

    def update_info(self):
        self.root_directory_label.configure(text=self.data["meta"]["root"])
        self.num_files_label.configure(text=self.data_handler.get_number_of_files())

    @property
    def data(self):
        return self.comparer.save_file_handler.data_dict

    @property
    def data_handler(self):
        return self.comparer.save_file_handler

    def on_start_analysis(self):
        self.running_analysis = True

        self.analyze_button.configure(text="Analysing", state="disabled", cursor="", bg="light grey")
        self.analyze_button.unbind("<Enter>")
        self.analyze_button.unbind("<Leave>")
        self.include_compared_checkbox.configure(state="disabled", cursor="")

        # Create a new thread to run the compare_all_images method
        thread = threading.Thread(target=self.run_analysis_thread)
        thread.start()

    def run_analysis_thread(self):
        # Run the compare_all_images method in a separate thread
        results = self.comparer.compare_all_images(skip_compared=not self.include_compared_var.get())
        self.populate_matches(results)

        # Use the after method to update the GUI from the main thread
        self.after(0, self.on_analysis_complete, results)

    def on_analysis_complete(self, e):
        self.analyze_button.configure(text="Start Analysis", state="normal", cursor="hand2",
                                      bg=App.colors["analysis_button_base"])
        self.analyze_button.bind("<Enter>", self._on_analyse_button_enter)
        self.analyze_button.bind("<Leave>", self._on_analyse_button_leave)
        self.include_compared_checkbox.configure(state="normal", cursor="hand2")

    def populate_matches(self, results):

        for match in results:
            match_frame = MatchFrame(master=self.matches_frame.scrollable_frame, match=match,
                                     match_id=self.session_next_match_id)
            match_frame.pack(fill="x")

            self.matches[self.session_next_match_id] = match_frame
            self.session_next_match_id += 1

    def _on_analyse_button_enter(self, e):
        self.analyze_button.configure(bg=App.colors["analysis_button_hover"])

    def _on_analyse_button_leave(self, e):
        self.analyze_button.configure(bg=App.colors["analysis_button_base"])

    def on_select_match(self, match_id):

        if self.selected_match_id is not None and self.selected_match_id != match_id:
            self.matches[self.selected_match_id].on_deselect()

        self.selected_match_id = match_id

        self.display_match_detail(images=(self.matches[self.selected_match_id].img_1_path,
                                          self.matches[self.selected_match_id].img_2_path),
                                  score=self.matches[self.selected_match_id].score)

    def display_match_detail(self, images, score):

        for child in self.detail_frame.winfo_children():
            child.destroy()

        score_label = tk.Label(self.detail_frame, text=score)
        score_label.pack()

        for image in images:
            new_img_frame = ImageDetailFrame(master=self.detail_frame, img_path=image)
            new_img_frame.pack(side="left")




class MatchFrame(tk.Frame):
    def __init__(self, match, match_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(relief="groove", bd=1, cursor="hand2", bg=App.colors["match_list_base_bg"])
        self.base_tk = self._get_base_tk()
        self.selected = False

        self.img_1_path = match[0]
        self.img_2_path = match[1]
        self.score = match[2]
        self.id = match_id

        self.img_names_frame = tk.Frame(self)
        self.img_names_frame.pack(side="left")

        self.img_1_label = tk.Label(self.img_names_frame, text=os.path.basename(self.img_1_path), width=18, anchor="w",
                                    bg=App.colors["match_list_base_bg"])
        self.img_1_label.grid(row=0, column=0, sticky="w")

        self.img_2_label = tk.Label(self.img_names_frame, text=os.path.basename(self.img_2_path), width=18, anchor="w",
                                    bg=App.colors["match_list_base_bg"])
        self.img_2_label.grid(row=1, column=0, sticky="w")

        self.score_label = tk.Label(self, text=str(int(self.score*100)) + "%", fg=App.colors["comparison_score"],
                                    font=Font(size=11, weight="bold"), anchor="e", bg=App.colors["match_list_base_bg"])
        self.score_label.pack(side="right")

        self.bg_widgets = (self, self.img_1_label, self.img_2_label, self.score_label)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for widget in self.bg_widgets:
            widget.bind("<Button-1>", self._on_click)

    def _on_enter(self, e):
        if not self.selected:
            for widget in self.bg_widgets:
                widget.configure(bg=App.colors["match_list_hover_bg"])

    def _on_leave(self, e):
        if not self.selected:
            for widget in self.bg_widgets:
                widget.configure(bg=App.colors["match_list_base_bg"])

    def _on_click(self, e):
        self.selected = True
        for widget in self.bg_widgets:
            widget.configure(bg=App.colors["match_list_active_bg"])

        self.score_label.configure(fg=App.colors["match_list_hover_bg"])

        self.base_tk.on_select_match(match_id=self.id)

    def on_deselect(self):
        self.selected = False
        for widget in self.bg_widgets:
            widget.configure(bg=App.colors["match_list_base_bg"])

        self.score_label.configure(fg=App.colors["comparison_score"])

    def _get_base_tk(self):
        master = self.master
        while not isinstance(master, tk.Tk):
            master = master.master
        return master


class ImageDetailFrame(tk.Frame):
    def __init__(self, img_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.img_path = img_path
        self.pil_img = Image.open(img_path).resize((300, 300))
        self.img_dims = self.pil_img.size
        self.img_size = os.path.getsize(img_path)

        self.tk_img = ImageTk.PhotoImage(self.pil_img)

        self.image_display = tk.Label(self, image=self.tk_img)
        self.image_display.pack()




class ScrollableFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize_timer = None  # Prevents lagging by only rezizing content once mouse is let go after rezizing

        self.scrollable_canvas = tk.Canvas(self, bg=self.cget("bg"), highlightthickness=0, relief='ridge')

        # Frame inside canvas
        self.scrollable_frame = tk.Frame(self.scrollable_canvas, bg=self.scrollable_canvas.cget("bg"))
        self.scrollable_frame.pack(side="left")
        self.scrollable_frame.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion=self.scrollable_canvas.bbox("all")))

        # Scrollbar for canvas
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.scrollable_canvas.yview, troughcolor=self.scrollable_canvas.cget("bg"))
        self.scrollbar.pack(side="right", fill="y")

        # Add a window with inner frame inside canvas. Link scrollbar to canvas
        self.scrollable_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_canvas.pack(side="bottom", fill="both", expand=True)

        # Bind scrollwheel to canvas to enable scrolling with mouse
        self.scrollable_frame.bind("<Enter>", lambda x: self.bind_canvas_to_mousewheel(self.scrollable_canvas))
        self.scrollable_frame.bind("<Leave>", lambda x: self.unbind_canvas_from_mousewheel(self.scrollable_canvas))

        # Bind canvas resize event to update the scrollable frame width
        self.scrollable_canvas.bind("<Configure>", self.on_canvas_configure)

    def bind_canvas_to_mousewheel(self, canvas):
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def unbind_canvas_from_mousewheel(self, canvas):
        canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_configure(self, event):
        if self.resize_timer is not None:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(200, self.update_scrollable_frame_width, event.width)

    def update_scrollable_frame_width(self, width):
        self.scrollable_canvas.itemconfig(self.scrollable_canvas.create_window((0, 0), window=self.scrollable_frame,
                                                                               anchor="nw"), width=width)


if __name__ == '__main__':
    app = App()
    app.mainloop()
