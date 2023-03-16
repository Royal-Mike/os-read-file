# PHYSICALDRIVE0 = Disk
# C:, D: = Partition
# with open (r"\\.\C:", "rb") as fr:
#     count = 0
#     byte = fr.read(1)
#     while count < 512:
#         print(byte.hex(), end=' ')
#         byte = fr.read(1)
#         count += 1

from datetime import datetime, timedelta

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

with open(r"\\.\C:", "rb") as fp:
    fp.read(3)
    type = fp.read(4).decode("ascii")
    if (type == "NTFS"):
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
        i = 1
        while i < 20:
            print('File ' + str(i))

            nextMFTEntry = startMFTEntry + bytesPerMFTEntry

            fp.seek(startMFTEntry, 0)
            fp.read(1)

            fp.seek(startMFTEntry + 0x14, 0)
            offsetFirstAttribute = int.from_bytes(fp.read(2), 'little')

            fp.seek(startMFTEntry + 0x18, 0)
            sizeMFTEntryUsed = int.from_bytes(fp.read(4), 'little')
            print('Size: ' + str(sizeMFTEntryUsed) + 'B')

            startAttribute = startMFTEntry + offsetFirstAttribute

            if (sizeMFTEntryUsed > 0):
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
                    if (typeAttribute == "0x10"):
                        fp.seek(startContent, 0)
                        timeCreatedNS = int.from_bytes(fp.read(8), 'little')
                        organizedTime = datetime(1601, 1, 1, 0, 0, 0) + timedelta(seconds = timeCreatedNS/1e7)
                        dateCreated = (str(organizedTime.day) + "/" + str(organizedTime.month) + "/" + str(organizedTime.year))
                        timeCreated = (str(organizedTime.hour) + ":" + str(organizedTime.minute) + ":" + str(organizedTime.second) + "." + str(organizedTime.microsecond))
                        print('Date created: ' + str(dateCreated))
                        print('Time created: ' + str(timeCreated))

                    # $FILE_NAME
                    elif (typeAttribute == "0x30"):
                        fp.seek(startContent + 0x38, 0)
                        fileAttribute = int.from_bytes(fp.read(4), 'little')
                        fp.seek(startContent + 0x40, 0)
                        lengthFileName = int.from_bytes(fp.read(1), 'little')
                        fp.seek(startContent + 0x42, 0)
                        fileName = fp.read(lengthFileName * 2).replace(b'\x00', b'').decode('utf-8')
                        print('Name: ' + fileName)

                    fp.seek(startAttribute + 0x04, 0)
                    sizeAttribute = int.from_bytes(fp.read(4), 'little')

                    startAttribute += sizeAttribute

            print()

            startMFTEntry += bytesPerMFTEntry
            i += 1