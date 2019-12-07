from tkinter.scrolledtext import *
from tkinter import *


class T:

    # def __init__(self, text):  # I don't need any init attributes, so I can skip this?
    #     pass                   # Also because it's a static method, right?

    @staticmethod
    def show(text):
        textbox.insert(END, text + '\n')
        textbox.see(END)  # Scrolls down if text exceeds bottom of textbox.


# TODO: Fit both say() and textbox on the grid into this class, and then can import it everywhere?

textbox = ScrolledText(window, width=40, height=24, wrap=WORD, fg='white', bg='black')
textbox.grid(row=0, column=7, rowspan=11, padx=5, sticky=N)

