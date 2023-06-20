import tkinter as tk
from tkinter import filedialog
import sys
import io

from controller.analyzer import projects_analysis


def disable_key_press(event):
    return "break"

class TextboxRedirect(io.StringIO):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def write(self, text):
        self.textbox.config(state="normal")
        self.textbox.insert(tk.END, text)
        self.textbox.config(state="disabled")


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("AI-Specific Code Smells Detector")
        master.geometry("500x300")

        # Riga 1: input path e button
        self.input_label = tk.Label(master, text="Input Path:")
        self.input_label.grid(row=1, column=0)

        self.input_path = tk.Label(master, text="No path selected")
        self.input_path.grid(row=1, column=1)

        self.input_button = tk.Button(master, text="Choose Input Folder", bg="lightblue", command=self.choose_input_path)
        self.input_button.grid(row=1, column=2)

        # Riga 2: output path e button
        self.output_label = tk.Label(master, text="Output Path:")
        self.output_label.grid(row=2, column=0)

        self.output_path = tk.Label(master, text="No path selected")
        self.output_path.grid(row=2, column=1)

        self.output_button = tk.Button(master, text="Choose Output Folder", bg="lightblue", command=self.choose_output_path)
        self.output_button.grid(row=2, column=2)

        # Riga 3: select number of walker
        self.walker_label = tk.Label(master, text="Select number of walkers:")
        self.walker_label.grid(row=3, column=0)

        self.walker_picker = tk.Spinbox(master, from_=1, to=10)
        self.walker_picker.grid(row=3, column=1)

        # Riga 4: parallel checkbox e textbox output
        self.parallel_check = tk.Checkbutton(master, text="Parallel")
        self.parallel_check.grid(row=4, column=0)

        self.refactoring_check = tk.Checkbutton(master, text="Refactoring")
        self.refactoring_check.grid(row=4, column=1)

        self.output_textbox = tk.Text(master, height=5, width=50)
        self.output_textbox.grid(row=5, column=0, columnspan=3, sticky="nsew")
        self.output_textbox.bind("<Key>", disable_key_press)
        # Riga 5: run e exit buttons
        self.run_button = tk.Button(master, text="Run", bg="lightgreen", command=self.run_program)
        self.run_button.grid(row=6, column=0)

        self.exit_button = tk.Button(master, text="Exit", bg="pink", command=master.quit)
        self.exit_button.grid(row=6, column=2)
        output_redirect = TextboxRedirect(self.output_textbox)

        # sovrascrivi sys.stdout con l'oggetto TextboxRedirect
        sys.stdout = output_redirect

        # Imposta il ridimensionamento dei widget
        master.grid_rowconfigure(4, weight=1)
        master.grid_columnconfigure(1, weight=1)

    def choose_input_path(self):
        path = filedialog.askdirectory()
        self.input_path.configure(text=path)

    def choose_output_path(self):
        path = filedialog.askdirectory()
        self.output_path.configure(text=path)

    def run_program(self):
        input_path = self.input_path.cget("text")
        output_path = self.output_path.cget("text")
        num_walkers = self.walker_picker.get()
        is_parallel = self.parallel_check
        self.output_textbox.insert(tk.END, f"Input path: {input_path}\nOutput path: {output_path}\nNumber of walkers: {num_walkers}\nParallel: {is_parallel}\n")
        projects_analysis(input_path,output_path)
def main():
    root = tk.Tk()
    my_gui = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
