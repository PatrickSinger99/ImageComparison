import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        """METADATA"""
        self.title("Image Comparison")
        self.geometry("720x480")


        """HEADER"""

        self.header_frame = tk.Frame(self, bg="green")
        self.header_frame.pack(side="top", fill="x")

        self.root_directory_label = tk.Label(text="asd")
        self.root_directory_label.pack()


        """BODY"""

        self.body_frame = tk.Frame(self, bg="red")
        self.body_frame.pack(side="bottom", fill="both", expand=True)

        # Matches Overview
        self.overview_frame = tk.Frame(self.body_frame, width=200, bg="yellow")
        self.overview_frame.pack(side="left", fill="y")

        # Match Detail
        self.detail_frame = tk.Frame(self.body_frame, bg="blue")
        self.detail_frame.pack(side="right", fill="both", expand=True)

if __name__ == '__main__':
    app = App()
    app.mainloop()
