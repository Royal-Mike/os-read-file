# PHYSICALDRIVE0 = Disk
# C:, D: = Partition
# with open (r"\\.\C:", "rb") as fr:
#     count = 0
#     byte = fr.read(1)
#     while count < 512:
#         print(byte.hex(), end=' ')
#         byte = fr.read(1)
#         count += 1

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

with open (r"\\.\D:", "rb") as fp:
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