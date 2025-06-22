image_height = 2304
poses = [
    [(2602, 928), (1472, 952)],
    [(2296, 456), (2402, 346)],
    [(1810, 912), (1658, 920)],
    [(3296, 1338), (1996, 1538)],
    [(930, 1340), (1996, 1538)],
    [(2116, 1872), (2986, 1788)],
    [(2112, 1040), (790, 1004)],
    [(2768, 566), (2038, 468)],
    [(1868, 604), (2372, 600)]
]

for pos in poses:
    # gets X Z from first image, gets Y from the second
    # converts Z from image coordinates to world
    pos3d = (pos[0][0], pos[1][0], image_height - pos[0][1])
    print(pos3d)