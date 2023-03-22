import tkinter as tk
from tkinter import ttk
import os
import shutil
import datetime

# Create window
window = tk.Tk()
window.title('Partition Manager')
window.geometry('500x500')

# Create menu bar
menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

# Create submenu
partition_menu = tk.Menu(menu_bar)
menu_bar.add_cascade(label='Partition', menu=partition_menu)

# Create treeview
tree = ttk.Treeview(window, height=20)
tree.pack()

# Create labels
name_label = tk.Label(window, text='Name:')
name_label.place(x=20, y=320)

attribute_label = tk.Label(window, text='Attribute:')
attribute_label.place(x=20, y=350)

date_label = tk.Label(window, text='Date Created:')
date_label.place(x=20, y=380)

time_label = tk.Label(window, text='Time Created:')
time_label.place(x=20, y=410)

size_label = tk.Label(window, text='Size:')
size_label.place(x=20, y=440)

# Create entry boxes
name_entry = tk.Entry(window)
name_entry.place(x=100, y=320)

attribute_entry = tk.Entry(window)
attribute_entry.place(x=100, y=350)

date_entry = tk.Entry(window)
date_entry.place(x=100, y=380)

time_entry = tk.Entry(window)
time_entry.place(x=100, y=410)

size_entry = tk.Entry(window)
size_entry.place(x=100, y=440)

window.mainloop()