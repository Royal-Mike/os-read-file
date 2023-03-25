import array

class time:
    hours = 0
    minutes = 0
    seconds = 0
    miliseconds = 0

class date:
    days = 0
    months = 0
    years = 0

class File:
    name = ""
    extension = "."
    atributes = ""
    
    created_time = time()
    created_date = date()


    beginning_cluster = 0
    size = 0
    children = array.array("i", [])
    #Constructor
    def __init__(self, name):
        self.name = name


def getAtributes(atributes):
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
            temp += "Director"
        elif (atributes[i] == "5"):
            temp += "Archive"

        if (i < len(atributes) - 2):
            temp += ", "
    return temp

from datetime import datetime, timedelta

with open(r"\\.\F:", "rb") as fp:
    fp.read(3)
    type = fp.read(5).decode("ascii")
    if (type == "MSDOS"):
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

        if (FATtype == "FAT32"):
            fp.seek(0x20, 0)
            volumeSize = int.from_bytes(fp.read(4), 'little')

            fp.seek(0x24, 0)
            sectorsPerFAT = int.from_bytes(fp.read(4), 'little')

            fp.seek(0x2C, 0)
            RDETIndex = int.from_bytes(fp.read(4), 'little')
            
        else:
            print("Error! The disk partition is not FAT32")
        
        RDETLocation = (sectorsBeforeFAT + numberOfFATs*sectorsPerFAT)*bytesPerSector
        
        file_list = File("")
        file_list = []
        
        list_length = 0
        fp.seek(RDETLocation, 0)
        fp.read(1)
        temp_name = ""
        index = RDETLocation
        while True:
            fp.seek(index, 0)
            isDeleted = fp.read(1)
            #If the file is deleted
            if (int.from_bytes(isDeleted,'little') == 229):
                index += 32
                continue
            #If the entry is NULL
            elif (int.from_bytes(isDeleted,'little') == 0):
                break
            else:
                fp.seek(index + 0x0B, 0)
                check = fp.read(1)

                if (int.from_bytes(check, 'little') == 15):
                    name = ""

                    #Check if there is any 0x0F
                    # fp.seek(index + 0x01, 0)
                    # check = fp.read(1)

                    fp.seek(index + 0x01, 0)
                    tmp = fp.read(2)
                    check = tmp[1:]
                    
                    i = 0

                    while (int.from_bytes(check,'little') != 255 and i < 5):
                        #if (i % 2 == 0): 
                        name = name + tmp.decode("utf-16")
                        tmp = fp.read(2)
                        check = tmp[1:]
                        i += 1

                    fp.seek(index + 0x0E, 0)
                    tmp = fp.read(2)
                    check = tmp[1:]
                    i = 0
                    while (int.from_bytes(check, 'little') != 255 and i < 6):
                        #if (i % 2 == 0):
                        name = name + tmp.decode("utf-16")
                        tmp = fp.read(2)
                        check = tmp[1:]
                        i += 1
                    fp.seek(index + 0x1C, 0)
                    tmp = fp.read(2)
                    check = tmp[1:]
                    i = 0
                    while (int.from_bytes(check, 'little') != 255 and i < 2):
                        #if (i % 2 == 0): 
                        name = name + tmp.decode("utf-16")
                        tmp = fp.read(2)
                        check = tmp[1:]
                        i += 1
                    temp_name = name + temp_name
                else:
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

                        file_list.append(File(temp_name))
                        list_length += 1

                        file_list[list_length - 1].extension = temp_extension

                        fp.seek(index + 0x0B, 0)

                        temp_atribute = bin(int.from_bytes(fp.read(1), 'little'))[2:]
                        position = 0
                        
                        for bit in temp_atribute[::-1]:
                            if (bit == "1"):
                                if (position == 0 or position == 1 or position == 2 or position == 3 or position == 4 or position == 5): 
                                    file_list[list_length - 1].atributes += str(position) + " "
                            position += 1
                        
                        fp.seek(index + 0x0D, 0)

                        t_time = '{0:b}'.format(int.from_bytes(fp.read(3), 'little'))
                        #print(t_time)

                        for i in range(24 - len(t_time)):
                            t_time = "0" + t_time
                        #Extract hours, minutes, seconds... from binary string
                        tmp_time = ""
                        for i in range(5):
                            tmp_time += t_time[i]

                        file_list[list_length - 1].created_time.hours = int(tmp_time, 2)

                        tmp_time =""
                        for i in range(5, 11):
                            tmp_time += t_time[i]
                        file_list[list_length - 1].created_time.minutes = int(tmp_time, 2)

                        tmp_time =""
                        for i in range(11, 17):
                            tmp_time += t_time[i]
                        file_list[list_length - 1].created_time.seconds = int(tmp_time, 2)

                        tmp_time =""
                        for i in range(17, 24):
                            tmp_time += t_time[i]
                        file_list[list_length - 1].created_time.miliseconds = int(tmp_time, 2)

                        #Date
                        tmp_time = ""
                        fp.seek(index + 0x10, 0)

                        t_time = '{0:b}'.format(int.from_bytes(fp.read(2), 'little'))

                        for i in range(16 - len(t_time)):
                            t_time = "0" + t_time
                        
                        for i in range(7):
                            tmp_time += t_time[i]

                        file_list[list_length - 1].created_date.years = int(tmp_time, 2) + 1980

                        tmp_time =""
                        for i in range(7, 11):
                            tmp_time += t_time[i]
                        file_list[list_length - 1].created_date.months = int(tmp_time, 2)

                        tmp_time =""
                        for i in range(11, 16):
                            tmp_time += t_time[i]
                        file_list[list_length - 1].created_date.days = int(tmp_time, 2)

                        # print(file_list[list_length - 1].name, end = ', created time: ')
                        # print(file_list[list_length - 1].created_time.hours, end = ':')   
                        # print(file_list[list_length - 1].created_time.minutes, end = ':') 
                        # print(file_list[list_length - 1].created_time.seconds, end = '.') 
                        # print(file_list[list_length - 1].created_time.miliseconds, end = ', create date: ')

                        # print(file_list[list_length - 1].created_date.days, end = '/')   
                        # print(file_list[list_length - 1].created_date.months, end = '/') 
                        # print(file_list[list_length - 1].created_date.years)

                        fp.seek(index + 0x1A, 0)

                        file_list[list_length - 1].beginning_cluster = int.from_bytes(fp.read(2), 'little')

                        fp.seek(index + 0x1C, 0)
                        file_list[list_length - 1].size = int.from_bytes(fp.read(4), 'little')

                        print(file_list[list_length - 1]. name, end = ', size: ')
                        print(file_list[list_length - 1].size, end = ', starting cluster: ')
                        print(file_list[list_length - 1].beginning_cluster)
                    temp_name = ""
                    

                index += 32
        
        # for j in range(list_length):
        #     print(file_list[j].name, end = ', ')
        #     print(getAtributes(file_list[j].atributes))
        #     print()
        #     print(file_list[i].name)
        #print(file_list[0].name)
        #print(fp.read(8).decode("utf-8"))
       # fp.seek(RDETLocation + 424)
        #print(fp.read(3).decode("utf-8"))

        # fp.seek(RDETLocation + 0x0D, 0)
        # time = int.from_bytes(fp.read(3), 'little')
        # hour = time // 3600000
        # minute = (time - hour * 3600000)//60000
        # second = (time - hour*3600000 - minute*60000) // 1000
        # milisecond = time - hour*3600000 - minute*60000 - second*1000
        # print(str(hour) + ":" + str(minute) + ":" + str(second) + "." + str(milisecond))

        # fp.seek(RDETLocation + 0x10, 0)
        # print(int.from_bytes(fp.read(2),'little'))

        # print("Bytes per Sector: " + str(bytesPerSector))
        # print("Sector per Cluster: " + str(sectorsPerCluster))
        # print("Sectors before FAT: " + str(sectorsBeforeFAT))
        # print("Number of Sectors of FAT: " + str(sectorsPerFAT))
        # print("Size of Volume: " + str(volumeSize))
        # print("Number of FAT: " + str(numberOfFATs))
        # print("RDET's index cluster: " + str(RDETIndex))
        # print("RDET location: " + str(RDETLocation))
    #     fp.seek(0x18, 0)
    #     sectorsPerTrack = int.from_bytes(fp.read(2), 'little')
    #     fp.seek(0x1A, 0)
    #     heads = int.from_bytes(fp.read(2), 'little')
    #     fp.seek(0x28, 0)
    #     sectorsInDisk = int.from_bytes(fp.read(8), 'little')
    #     fp.seek(0x30, 0)
    #     MFTstartCluster = int.from_bytes(fp.read(8), 'little')
    #     fp.seek(0x38, 0)
    #     MFTBstartCluster = int.from_bytes(fp.read(8), 'little')
    #     fp.seek(0x40, 0)
    #     bytesPerMFTEntryNC = int.from_bytes(fp.read(1), 'little')
    #     bytesPerMFTEntry = 2 ** abs(twos_comp(bytesPerMFTEntryNC, len(bin(bytesPerMFTEntryNC)[2:])))

    #     print('Bytes per Sector: ' + str(bytesPerSector))
    #     print('Sectors per Cluster: ' + str(sectorsPerCluster))
    #     print('Sectors per Track: ' + str(sectorsPerTrack))
    #     print('Heads: ' + str(heads))
    #     print('Sectors in Disk: ' + str(sectorsInDisk))
    #     print('First MFT Cluster: ' + str(MFTstartCluster))
    #     print('First MFT Backup Cluster: ' + str(MFTBstartCluster))
    #     print('Bytes per MFT Entry: ' + str(bytesPerMFTEntry))

    #     print()

    #     MFTstartByte = MFTstartCluster * sectorsPerCluster * bytesPerSector
    #     fp.seek(MFTstartByte, 0)
    #     fp.read(1)

    #     startMFTEntry = MFTstartByte
    #     i = 1
    #     while i < 20:
    #         print('File ' + str(i))

    #         nextMFTEntry = startMFTEntry + bytesPerMFTEntry

    #         fp.seek(startMFTEntry, 0)
    #         fp.read(1)

    #         fp.seek(startMFTEntry + 0x14, 0)
    #         offsetFirstAttribute = int.from_bytes(fp.read(2), 'little')

    #         fp.seek(startMFTEntry + 0x18, 0)
    #         sizeMFTEntryUsed = int.from_bytes(fp.read(4), 'little')
    #         print('Size: ' + str(sizeMFTEntryUsed) + 'B')

    #         startAttribute = startMFTEntry + offsetFirstAttribute

    #         if (sizeMFTEntryUsed > 0):
    #             while True:
    #                 fp.seek(startAttribute, 0)
    #                 typeAttribute = hex(int.from_bytes(fp.read(4), 'little'))

    #                 if typeAttribute == "0xffffffff": break

    #                 fp.seek(startAttribute + 0x10, 0)
    #                 sizeContent = int.from_bytes(fp.read(4), 'little')

    #                 fp.seek(startAttribute + 0x14, 0)
    #                 offsetContent = int.from_bytes(fp.read(2), 'little')

    #                 startContent = startAttribute + offsetContent

    #                 # $STANDARD_INFORMATION
    #                 if (typeAttribute == "0x10"):
    #                     fp.seek(startContent, 0)
    #                     timeCreatedNS = int.from_bytes(fp.read(8), 'little')
    #                     organizedTime = datetime(1601, 1, 1, 0, 0, 0) + timedelta(seconds = timeCreatedNS/1e7)
    #                     dateCreated = (str(organizedTime.day) + "/" + str(organizedTime.month) + "/" + str(organizedTime.year))
    #                     timeCreated = (str(organizedTime.hour) + ":" + str(organizedTime.minute) + ":" + str(organizedTime.second) + "." + str(organizedTime.microsecond))
    #                     print('Date created: ' + str(dateCreated))
    #                     print('Time created: ' + str(timeCreated))

    #                 # $FILE_NAME
    #                 elif (typeAttribute == "0x30"):
    #                     fp.seek(startContent + 0x38, 0)
    #                     fileAttribute = int.from_bytes(fp.read(4), 'little')
    #                     fp.seek(startContent + 0x40, 0)
    #                     lengthFileName = int.from_bytes(fp.read(1), 'little')
    #                     fp.seek(startContent + 0x42, 0)
    #                     fileName = fp.read(lengthFileName * 2).replace(b'\x00', b'').decode('utf-8')
    #                     print('Name: ' + fileName)

    #                 fp.seek(startAttribute + 0x04, 0)
    #                 sizeAttribute = int.from_bytes(fp.read(4), 'little')

    #                 startAttribute += sizeAttribute

    #         print()

    #         startMFTEntry += bytesPerMFTEntry
    #         i += 1