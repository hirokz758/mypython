import tkinter as tk

root = tk.Tk()
root.geometry("400x400")

lbl = tk.Label(text="label")
btn = tk.Button(text="push")

lbl.pack()
btn.pack()
tk.mainloop()
