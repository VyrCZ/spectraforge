import socket
import json

def handle_client(client_socket):
    try:
        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        data = client_socket.makefile().readline().strip()
        print(f"Received: {data}")

        # Parse JSON request
        request = json.loads(data)
        print(f"Request JSON: {request}")

        # Prepare a JSON response
        response = {
            "status": "success",
            "message": f"Hello, {request.get('name', 'Client')}!"
        }
        response_data = json.dumps(response)
        client_socket.send(response_data.encode('utf-8'))

    except json.JSONDecodeError:
        error_response = {"status": "error", "message": "Invalid JSON format"}
        client_socket.send(json.dumps(error_response).encode('utf-8'))
    except Exception as e:
        print("Error: ", e)
    finally:
        client_socket.close()

def start_server(host='0.0.0.0', port=4875):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
   