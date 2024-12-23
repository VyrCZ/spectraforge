import socket
import board
import neopixel

# LED setup
NUM_LEDS = 200
pixels = neopixel.NeoPixel(board.D18, NUM_LEDS, auto_write=False)

def set_led(index):
    pixels.fill((0, 0, 0))  # Turn off all LEDs
    if 0 <= index < NUM_LEDS:
        pixels[index] = (255, 255, 255)  # Set specific LED to full white
    pixels.show()

# Networking setup
HOST = "0.0.0.0"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = server_socket.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                index = int(data.decode())
                print(f"Received index: {index}")
                set_led(index)
            except ValueError:
                print("Invalid input received")
