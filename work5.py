import tkinter as tk


def dispLadel():
    lbl["text"] = "pushed"
btn = tk.Button(text="push", command = dispLadel)

root = tk.Tk()
root.geometry("100x100")

lbl = tk.Label(text="label")

#btn = tk.Button(text="push")
btn = tk.Button(text="push", command = dispLadel)

lbl.pack()
btn.pack()

def displabel():
    lbl.configure(text="pushed")

import tkinter as tk
import random

def displabel():
   kuji = ["大吉","中吉","小吉","吉","末吉","凶"]
    lbl.configure(text=random.choice(kuji))

root = tk.Tk() 



tk.mainloop()


