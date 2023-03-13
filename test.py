# PHYSICALDRIVE0 = Disk
# C:, D: = Partition
# with open (r"\\.\C:", "rb") as fr:
#     count = 0
#     byte = fr.read(1)
#     while count < 512:
#         print(byte.hex(), end=' ')
#         byte = fr.read(1)
#         count += 1

with open (r"\\.\D:", "rb") as fr:
    fr.read(3)
    print(fr.read(5).decode("ascii"))