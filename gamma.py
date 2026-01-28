gamma = 2.8

for i in range(256):
    value = int((i / 255) ** gamma * 255)
    bigger_value = int((i / 255) ** (gamma * 2) * 255 + 0.5)
    print(f"{i}: {value} | {bigger_value}")
