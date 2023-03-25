# Thư viện cho GUI
import tkinter as tk
from tkinter import ttk

# Thư viện tính thời gian
from datetime import datetime, timedelta

# Tính bù 2 của byte
def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

# Class chứa thông tin của file
class File:
    def __init__(self, ID, ID_parent, name, attributes, date_created, time_created, size):
        self.ID = ID
        self.ID_parent = ID_parent
        self.name = name
        self.attributes = attributes
        self.date_created = date_created
        self.time_created = time_created
        self.size = size

# Mảng chứa tất cả file FAT32
filesFAT = []

with open(r"\\.\E:", "rb") as fp:
    fp.read(3)
    type = fp.read(4).decode("ascii")
    if type == "NTFS":
        fp.seek(0x0B, 0)
        bytesPerSector = int.from_bytes(fp.read(2), 'little')
        fp.seek(0x0D, 0)
        sectorsPerCluster = int.from_bytes(fp.read(1), 'little')
        fp.seek(0x18, 0)
        sectorsPerTrack = int.from_bytes(fp.read(2), 'little')
        fp.seek(0x1A, 0)
        heads = int.from_bytes(fp.read(2), 'little')
        fp.seek(0x28, 0)
        sectorsInDisk = int.from_bytes(fp.read(8), 'little')
        fp.seek(0x30, 0)
        MFTstartCluster = int.from_bytes(fp.read(8), 'little')
        fp.seek(0x38, 0)
        MFTBstartCluster = int.from_bytes(fp.read(8), 'little')
        fp.seek(0x40, 0)
        bytesPerMFTEntryNC = int.from_bytes(fp.read(1), 'little')
        bytesPerMFTEntry = 2 ** abs(twos_comp(bytesPerMFTEntryNC, len(bin(bytesPerMFTEntryNC)[2:])))

        print('Bytes per Sector: ' + str(bytesPerSector))
        print('Sectors per Cluster: ' + str(sectorsPerCluster))
        print('Sectors per Track: ' + str(sectorsPerTrack))
        print('Heads: ' + str(heads))
        print('Sectors in Disk: ' + str(sectorsInDisk))
        print('First MFT Cluster: ' + str(MFTstartCluster))
        print('First MFT Backup Cluster: ' + str(MFTBstartCluster))
        print('Bytes per MFT Entry: ' + str(bytesPerMFTEntry))

        print()

        MFTstartByte = MFTstartCluster * sectorsPerCluster * bytesPerSector
        fp.seek(MFTstartByte, 0)
        fp.read(1)

        startMFTEntry = MFTstartByte
        emptyCheck = 0
        i = 0
        while True:
            nextMFTEntry = startMFTEntry + bytesPerMFTEntry

            fp.seek(startMFTEntry, 0)
            fp.read(1)

            fp.seek(startMFTEntry + 0x14, 0)
            offsetFirstAttribute = int.from_bytes(fp.read(2), 'little')

            fp.seek(startMFTEntry + 0x18, 0)
            sizeMFTEntryUsed = int.from_bytes(fp.read(4), 'little')

            fp.seek(startMFTEntry + 0x2C, 0)
            fileID = int.from_bytes(fp.read(4), 'little')

            startAttribute = startMFTEntry + offsetFirstAttribute

            fileName = ''
            fileIDParent = ''
            fileAttributes = []
            fileDateCreated = ''
            fileTimeCreated = ''
            fileSize = 0

            if sizeMFTEntryUsed > 0:
                while True:
                    fp.seek(startAttribute, 0)
                    typeAttribute = hex(int.from_bytes(fp.read(4), 'little'))

                    if typeAttribute == "0xffffffff": break

                    fp.seek(startAttribute + 0x10, 0)
                    sizeContent = int.from_bytes(fp.read(4), 'little')

                    fp.seek(startAttribute + 0x14, 0)
                    offsetContent = int.from_bytes(fp.read(2), 'little')

                    startContent = startAttribute + offsetContent

                    # $STANDARD_INFORMATION
                    if typeAttribute == "0x10":
                        fp.seek(startContent, 0)
                        timeCreatedNS = int.from_bytes(fp.read(8), 'little')
                        organizedTime = datetime(1601, 1, 1, 0, 0, 0) + timedelta(seconds = timeCreatedNS / 1e7) + timedelta(hours = 7)
                        fileDateCreated = (str(organizedTime.day) + "/" + str(organizedTime.month) + "/" + str(organizedTime.year))
                        fileTimeCreated = (str(organizedTime.hour) + ":" + str(organizedTime.minute) + ":" + str(organizedTime.second) + "." + str(organizedTime.microsecond))

                    # $FILE_NAME
                    elif typeAttribute == "0x30":
                        fp.seek(startContent + 0x00, 0)
                        fileIDParent = int.from_bytes(fp.read(6), 'little')

                        fp.seek(startContent + 0x38, 0)
                        stringAttribute = bin(int.from_bytes(fp.read(4), 'little'))[2:]

                        bitPosition = 0
                        for bit in reversed(stringAttribute):
                            if (bit == '1'):
                                if (bitPosition == 0): fileAttributes.append('Read-Only')
                                elif (bitPosition == 1): fileAttributes.append('Hidden')
                                elif (bitPosition == 2): fileAttributes.append('System')
                                elif (bitPosition == 5): fileAttributes.append('Archive')
                                elif (bitPosition == 28): fileAttributes.append('Directory')
                            bitPosition += 1

                        fp.seek(startContent + 0x40, 0)
                        lengthFileName = int.from_bytes(fp.read(1), 'little')
                        fp.seek(startContent + 0x42, 0)
                        fileName = fp.read(lengthFileName * 2).replace(b'\x00', b'').decode('utf-8')

                    # $DATA
                    elif typeAttribute == "0x80":
                        fileSize = sizeContent

                    fp.seek(startAttribute + 0x04, 0)
                    sizeAttribute = int.from_bytes(fp.read(4), 'little')

                    startAttribute += sizeAttribute

            startMFTEntry += bytesPerMFTEntry
            i += 1

            if i < 37: continue

            if fileDateCreated == '': break

            fileAttributesString = ''
            if not fileAttributes: fileAttributesString = 'None'
            else:
                setAttributes = [*set(fileAttributes)]
                fileAttributesString = ', '.join(setAttributes)

            fileData = File(fileID, fileIDParent, fileName, fileAttributesString, fileDateCreated, fileTimeCreated, fileSize)
            filesFAT.append(fileData)

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
        for file in filesFAT:
            if any(obj.ID == file.ID_parent for obj in filesFAT):
                tree.insert(file.ID_parent, 'end', file.ID, text=file.name)
            else:
                tree.insert('', 'end', file.ID, text=file.name)
    elif partition == 'NTFS':
        tree.insert('', 'end', 'testN', text='testNTFS')

def display_info(self):
    # Get the selected item
    item = tree.selection()[0]

    for file in filesFAT:
        print(file.ID)
        print(item)
        if file.ID == int(item):
            # Display the information
            name_entry['text'] = file.name
            attribute_entry['text'] = file.attributes
            date_entry['text'] = file.date_created
            time_entry['text'] = file.time_created
            size_entry['text'] = str(file.size) + ' bytes'

# Add commands to the menu
partition_menu.add_command(label='FAT32', command=lambda:open_partition('FAT32'))
partition_menu.add_command(label='NTFS', command=lambda:open_partition('NTFS'))

# Bind the treeview to the display_info function
tree.bind('<<TreeviewSelect>>', display_info)

window.mainloop()