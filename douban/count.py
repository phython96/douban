import os

root = 'Json_2006_2009'
namelist = os.listdir(root)
count = 0
for name in namelist:
    if "movielist" in name:
        continue
    path = os.path.join(root, name)
    f = open(path, "r")
    count += len(f.readlines())

print(count)
