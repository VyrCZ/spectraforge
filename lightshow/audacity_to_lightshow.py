# open labels.txt
path = "lightshow/labels"
song = "overkill"
with open(path+"/"+song+".txt", 'r') as f:
    labels = f.readlines()

points = []
for label in labels:
    start, end, name = label.split("\t")
    points.append((float(start), name.strip()))
    print(f"schedule_event({float(start):.3f}, {name.strip()})")
    