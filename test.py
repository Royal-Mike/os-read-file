with open (r"\\.\PHYSICALDRIVE0","rb") as fr:
    data = fr.read(512)
    print(data)