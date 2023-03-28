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

# Lấy thuộc tính của file FAT32
def getAttributes(atributes):
    temp = ""
    for i in range(len(atributes)):
        if (atributes[i] == "0"):
            temp += "Read-Only"
        elif (atributes[i] == "1"):
            temp += "Hidden"
        elif (atributes[i] == "2"):
            temp += "System"
        elif (atributes[i] == "3"):
            temp += "Volume label"
        elif (atributes[i] == "4"):
            temp += "Directory"
        elif (atributes[i] == "5"):
            temp += "Archive"

        if (i < len(atributes) - 2):
            temp += ", "
    return temp

# Class chứa thông tin của file FAT32
class FileFAT32:
    name = ""
    extension = "."
    attributes = ""
    
    created_time = ""
    created_date = ""

    location = 0
    beginning_cluster = 0
    size = 0
    father = -1
    #Check directory
    sentinal = False
    #Constructor
    def __init__(self, name):
        self.name = name

# Mảng chứa tất cả file FAT32
filesFAT32 = []

# Class chứa thông tin của file NTFS
class FileNTFS:
    def __init__(self, ID, ID_parent, name, attributes, date_created, time_created, size):
        self.ID = ID
        self.ID_parent = ID_parent
        self.name = name
        self.attributes = attributes
        self.date_created = date_created
        self.time_created = time_created
        self.size = size

# Mảng chứa tất cả file NTFS
filesNTFS = []

# Mở partition
with open(r"\\.\E:", "rb") as fp:
    # Đọc format
    fp.read(3)
    type = fp.read(5).decode("ascii")
    # Kiểu NTFS
    if type == "NTFS ":
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
        startMFTEntry = MFTstartByte

        fp.seek(startMFTEntry, 0)
        fp.read(1)
        fp.seek(-1, 1)

        i = 0
        while True:
            fp.seek(0x14, 1)
            offsetFirstAttribute = int.from_bytes(fp.read(2), 'little')
            fp.seek(-2 - 0x14, 1)

            fp.seek(0x18, 1)
            sizeMFTEntryUsed = int.from_bytes(fp.read(4), 'little')
            fp.seek(-4 - 0x18, 1)

            fp.seek(0x2C, 1)
            fileID = int.from_bytes(fp.read(4), 'little')
            fp.seek(-4 - 0x2C, 1)

            fileName = ''
            fileIDParent = ''
            fileAttributes = []
            fileDateCreated = ''
            fileTimeCreated = ''
            fileSize = 0

            fp.seek(offsetFirstAttribute, 1)

            if sizeMFTEntryUsed > 0:
                totalAttributes = offsetFirstAttribute
                while True:
                    typeAttribute = hex(int.from_bytes(fp.read(4), 'little'))
                    fp.seek(-4, 1)

                    if typeAttribute == "0xffffffff":
                        fp.seek(-totalAttributes, 1)
                        break

                    fp.seek(0x10, 1)
                    sizeContent = int.from_bytes(fp.read(4), 'little')
                    fp.seek(-4 - 0x10, 1)

                    fp.seek(0x14, 1)
                    offsetContent = int.from_bytes(fp.read(2), 'little')
                    fp.seek(-2 - 0x14, 1)

                    # $STANDARD_INFORMATION
                    if typeAttribute == "0x10":
                        fp.seek(offsetContent, 1)
                        timeCreatedNS = int.from_bytes(fp.read(8), 'little')
                        fp.seek(-8 - offsetContent, 1)
                        organizedTime = datetime(1601, 1, 1, 0, 0, 0) + timedelta(seconds = timeCreatedNS / 1e7) + timedelta(hours = 7)
                        fileDateCreated = (str(organizedTime.day) + "/" + str(organizedTime.month) + "/" + str(organizedTime.year))
                        fileTimeCreated = (str(organizedTime.hour) + ":" + str(organizedTime.minute) + ":" + str(organizedTime.second) + "." + str(organizedTime.microsecond))

                    # $FILE_NAME
                    elif typeAttribute == "0x30":
                        fp.seek(offsetContent, 1)
                        fileIDParent = int.from_bytes(fp.read(6), 'little')
                        fp.seek(-6, 1)

                        fp.seek(0x38, 1)
                        stringAttribute = bin(int.from_bytes(fp.read(4), 'little'))[2:]
                        fp.seek(-4 - 0x38, 1)

                        bitPosition = 0
                        for bit in reversed(stringAttribute):
                            if (bit == '1'):
                                if (bitPosition == 0): fileAttributes.append('Read-Only')
                                elif (bitPosition == 1): fileAttributes.append('Hidden')
                                elif (bitPosition == 2): fileAttributes.append('System')
                                elif (bitPosition == 5): fileAttributes.append('Archive')
                                elif (bitPosition == 28): fileAttributes.append('Directory')
                            bitPosition += 1

                        fp.seek(0x40, 1)
                        lengthFileName = int.from_bytes(fp.read(1), 'little')
                        fp.seek(-1 - 0x40, 1)

                        fp.seek(0x42, 1)
                        fileName = fp.read(lengthFileName * 2).replace(b'\x00', b'').decode('utf-8')
                        fp.seek(-(lengthFileName * 2) - 0x42, 1)

                        fp.seek(-offsetContent, 1)

                    # $DATA
                    elif typeAttribute == "0x80":
                        fileSize = sizeContent

                    fp.seek(0x04, 1)
                    sizeAttribute = int.from_bytes(fp.read(4), 'little')
                    fp.seek(-4 - 0x04, 1)

                    totalAttributes += sizeAttribute
                    fp.seek(sizeAttribute, 1)

            i += 1

            if i < 37:
                fp.seek(bytesPerMFTEntry, 1)
                fp.read(1)
                fp.seek(-1, 1)
                continue

            if fileDateCreated == '': break

            fileAttributesString = ''
            if not fileAttributes: fileAttributesString = 'None'
            else:
                setAttributes = [*set(fileAttributes)]
                fileAttributesString = ', '.join(setAttributes)

            fileData = FileNTFS(fileID, fileIDParent, fileName, fileAttributesString, fileDateCreated, fileTimeCreated, fileSize)
            filesNTFS.append(fileData)

            fp.seek(bytesPerMFTEntry, 1)
            fp.read(1)
            fp.seek(-1, 1)

    # Kiểu FAT32
    elif (type == "MSDOS"):
        fp.seek(0x0B, 0)
        bytesPerSector = int.from_bytes(fp.read(2), 'little')
        fp.seek(0x0D, 0)
        sectorsPerCluster = int.from_bytes(fp.read(1), 'little')
        fp.seek(0x0E, 0)
        sectorsBeforeFAT = int.from_bytes(fp.read(2), 'little')
        fp.seek(0x10, 0)
        numberOfFATs = int.from_bytes(fp.read(1), 'little')

        fp.seek(0x52, 0)

        numberOfEntriesofRDET = 0 
        volumeSize = 0 
        sectorsPerFAT = 0

        FATtype = fp.read(5).decode("ascii")

        if (FATtype != "FAT32"):
            print("ERROR: Partition là FAT nhưng không phải FAT32")
            
        else:
            fp.seek(0x20, 0)
            volumeSize = int.from_bytes(fp.read(4), 'little')

            fp.seek(0x24, 0)
            sectorsPerFAT = int.from_bytes(fp.read(4), 'little')

            fp.seek(0x2C, 0)
            RDETIndex = int.from_bytes(fp.read(4), 'little')

            RDETLocation = (sectorsBeforeFAT + numberOfFATs*sectorsPerFAT)*bytesPerSector
            
            file_list = FileFAT32("")
            file_list = []
            
            list_length = 0
            fp.seek(RDETLocation, 0)
            fp.read(1)
            temp_name = ""
            index = RDETLocation
            #Check if there are no more files to read by counting the file
            cou = 0
            sentinal = 0
            father = [-1]
            while True:
                fp.seek(index, 0)
                isDeleted = fp.read(1)
                #If the file is deleted
                if (int.from_bytes(isDeleted,'little') == 229):
                    index += 32
                    continue
                #If the entry is NULL
                elif (int.from_bytes(isDeleted,'little') == 0):
                    if (cou >= list_length):
                        break

                    if (file_list[cou].sentinal):
                        child_location = (file_list[cou].beginning_cluster - RDETIndex) * sectorsPerCluster * bytesPerSector + RDETLocation
                        #If the children files havenot been read
                        if (index - child_location < 0):
                            index = child_location
                            father.append(cou)
                            sentinal += 1
                        #If the children files have been read
                        else:
                            for j in range(cou, list_length):
                                if (file_list[j].father == -1 and file_list.location > child_location):
                                    file_list[j].father = cou
                        
                    cou += 1
                else:
                    fp.seek(index + 0x0B, 0)
                    check = fp.read(1)

                    if (int.from_bytes(check, 'little') == 15):
                        name = ""

                        fp.seek(index + 0x01, 0)
                        tmp = fp.read(2)
                        check = tmp[1:]
                        
                        i = 0

                        while (int.from_bytes(check,'little') != 255 and i < 5):
                            name = name + tmp.decode("utf-16")
                            tmp = fp.read(2)
                            check = tmp[1:]
                            i += 1

                        fp.seek(index + 0x0E, 0)
                        tmp = fp.read(2)
                        check = tmp[1:]
                        i = 0
                        while (int.from_bytes(check, 'little') != 255 and i < 6):
                            name = name + tmp.decode("utf-16")
                            tmp = fp.read(2)
                            check = tmp[1:]
                            i += 1
                        fp.seek(index + 0x1C, 0)
                        tmp = fp.read(2)
                        check = tmp[1:]
                        i = 0
                        while (int.from_bytes(check, 'little') != 255 and i < 2):
                            name = name + tmp.decode("utf-16")
                            tmp = fp.read(2)
                            check = tmp[1:]
                            i += 1
                        #Reverse the file name
                        temp_name = name + temp_name
                    else:
                        #Check if there is any extra entries before this main entry
                        guard = False
                        if (temp_name == ""):
                            fp.seek(index, 0)
                            temp_name = fp.read(8).decode("utf-8")
                            guard = True

                        temp_name = temp_name[::-1]

                        while (temp_name[0] == " "):
                            temp_name = temp_name[1:]

                        if (guard == False): temp_name = temp_name[1:]

                        temp_name = temp_name[::-1]
                        
                        if (temp_name != "." and temp_name != ".."):
                            temp_extension = ""

                            fp.seek(index + 0x08, 0)
                            temp_extension =  fp.read(3).decode("utf-8").lower()

                            if (guard and temp_extension != "   "):
                                temp_name = temp_name + "." + temp_extension

                            file_list.append(FileFAT32(temp_name))
                            list_length += 1

                            file_list[list_length - 1].location = index
                            
                            file_list[list_length - 1].father = father[sentinal]

                            file_list[list_length - 1].extension = temp_extension

                            fp.seek(index + 0x0B, 0)

                            temp_attribute = bin(int.from_bytes(fp.read(1), 'little'))[2:]
                            position = 0
                            
                            for bit in temp_attribute[::-1]:
                                if (bit == "1"):
                                    if (position == 0 or position == 1 or position == 2 or position == 3 or position == 4 or position == 5): 
                                        if (position == 4): file_list[list_length - 1].sentinal = True
                                        file_list[list_length - 1].attributes += str(position) + " "
                                position += 1
                            
                            t_attribute = getAttributes(file_list[list_length - 1].attributes)

                            file_list[list_length - 1].attributes = t_attribute


                            fp.seek(index + 0x0D, 0)

                            t_time = '{0:b}'.format(int.from_bytes(fp.read(3), 'little'))
                            #print(t_time)

                            for i in range(24 - len(t_time)):
                                t_time = "0" + t_time
                            #Extract hours, minutes, seconds... from binary string
                            tmp_time = ""
                            for i in range(5):
                                tmp_time += t_time[i]

                            file_list[list_length - 1].created_time = file_list[list_length - 1].created_time + str(int(tmp_time, 2)) + ":"
                            tmp_time =""
                            for i in range(5, 11):
                                tmp_time += t_time[i]
                            file_list[list_length - 1].created_time = file_list[list_length - 1].created_time + str(int(tmp_time, 2)) + ":"

                            tmp_time =""
                            for i in range(11, 17):
                                tmp_time += t_time[i]
                            file_list[list_length - 1].created_time = file_list[list_length - 1].created_time + str(int(tmp_time, 2)) + "."

                            tmp_time =""
                            for i in range(17, 24):
                                tmp_time += t_time[i]
                            file_list[list_length - 1].created_time += str(int(tmp_time, 2))

                            #Date
                            tmp_time = ""
                            fp.seek(index + 0x10, 0)

                            t_time = '{0:b}'.format(int.from_bytes(fp.read(2), 'little'))

                            for i in range(16 - len(t_time)):
                                t_time = "0" + t_time
                            
                            for i in range(7):
                                tmp_time += t_time[i]

                            file_list[list_length - 1].created_date = str(int(tmp_time, 2) + 1980) + file_list[list_length - 1].created_date

                            tmp_time =""
                            for i in range(7, 11):
                                tmp_time += t_time[i]
                            if (int(tmp_time, 2) == 0):
                                file_list[list_length - 1].created_date = "1/" + file_list[list_length - 1].created_date
                            else:
                                file_list[list_length - 1].created_date = str(int(tmp_time, 2)) + "/" + file_list[list_length - 1].created_date

                            tmp_time =""
                            for i in range(11, 16):
                                tmp_time += t_time[i]
                            if (int(tmp_time, 2) == 0):
                                file_list[list_length - 1].created_date = "1/" + file_list[list_length - 1].created_date
                            else:
                                file_list[list_length - 1].created_date = str(int(tmp_time, 2)) + "/" + file_list[list_length - 1].created_date


                            fp.seek(index + 0x1A, 0)

                            file_list[list_length - 1].beginning_cluster = int.from_bytes(fp.read(2), 'little')

                            fp.seek(index + 0x1C, 0)
                            file_list[list_length - 1].size = int.from_bytes(fp.read(4), 'little')

                        temp_name = ""
                    
                    index += 32

    # Không phải cả 2
    else: print('ERROR: Partition không phải là FAT32 hay NTFS')

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
    if partition == 'NTFS':
        for file in filesNTFS:
            if any(obj.ID == file.ID_parent for obj in filesNTFS):
                tree.insert(file.ID_parent, 'end', file.ID, text=file.name)
            else:
                tree.insert('', 'end', file.ID, text=file.name)
    elif partition == 'FAT32':
        tree.insert('', 'end', 'testF', text='testFAT32')

def display_info(self):
    # Get the selected item
    item = tree.selection()[0]

    for file in filesNTFS:
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