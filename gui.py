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
partition_menu = tk.Menu(menu_bar, tearoff='off')
menu_bar.add_cascade(label='Partition', menu=partition_menu)

# Create treeview
tree = ttk.Treeview(window, height=20)
tree.pack()
tree.place(x=0)

# Create labels
name_label = tk.Label(window, text='Name:')
name_label.place(x=220, y=0)

attribute_label = tk.Label(window, text='Attribute:')
attribute_label.place(x=220, y=30)

date_label = tk.Label(window, text='Date Created:')
date_label.place(x=220, y=60)

time_label = tk.Label(window, text='Time Created:')
time_label.place(x=220, y=90)

size_label = tk.Label(window, text='Size:')
size_label.place(x=220, y=120)

# Create entry boxes
name_entry = tk.Label(window)
name_entry.place(x=300, y=0)

attribute_entry = tk.Label(window)
attribute_entry.place(x=300, y=30)

date_entry = tk.Label(window)
date_entry.place(x=300, y=60)

time_entry = tk.Label(window)
time_entry.place(x=300, y=90)

size_entry = tk.Label(window)
size_entry.place(x=300, y=120)

def open_partition(partition):
    tree.delete(*tree.get_children())
    if partition == 'FAT32':
        tree.insert('', 'end', 'testF', text='testFAT')
    elif partition == 'NTFS':
        tree.insert('', 'end', 'testN', text='testNTFS')

def display_info(self):
    # Get the selected item
    item = tree.selection()[0]
    print(item)
    # Display the information
    name_entry['text'] = "A"
    attribute_entry['text'] = "B"
    date_entry['text'] = "C"
    time_entry['text'] = "D"
    size_entry['text'] = "E"

# Add commands to the menu
partition_menu.add_command(label='FAT32', command=lambda:open_partition('FAT32'))
partition_menu.add_command(label='NTFS', command=lambda:open_partition('NTFS'))

# Bind the treeview to the display_info function
tree.bind('<<TreeviewSelect>>', display_info)

window.mainloop()