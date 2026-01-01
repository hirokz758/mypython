import tkinter as tk

root = tk.Tk()
root.geometry("400x200")

lbl = tk.Label(text="label")
btn = tk.Button(text="push"*5)

lbl.pack()
btn.pack()
tk.mainloop()
