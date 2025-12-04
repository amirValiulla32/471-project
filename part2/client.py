import socket
import os

# FTP-like client with TWO connections:
# 1. Control Connection (port 11123) - for commands and responses
# 2. Data Connection (dynamic port) - for file/data transfers

CONTROL_PORT = 11123
SERVER_IP = '3.81.111.91'  # EC2 instance IP

def create_data_connection(port):
    """
    Create a data connection to the server on the specified port.
    This is opened on-demand for each data transfer.
    The port is dynamically assigned by the server.
    """
    data_socket = socket.socket()
    data_socket.connect((SERVER_IP, port))
    return data_socket

def parse_data_port(response):
    """
    Parse the data port number from server's 150 response.
    Example: "150 Opening data connection on port 54321"
    """
    try:
        # Split response and find "port" keyword
        parts = response.split()
        port_index = parts.index("port") + 1
        return int(parts[port_index])
    except (ValueError, IndexError):
        print("Error: Could not parse data port from server response")
        return None


def handle_ls(ctrl_socket):
    """
    Handle 'ls' command using two-connection architecture.
    Command sent on control connection, data received on data connection.
    """
    # Send command on control connection
    ctrl_socket.send(b"ls\n")

    # Receive response on control connection
    response = ctrl_socket.recv(1024).decode().strip()
    print(f"Server: {response}")

    if response.startswith("150"):
        # Parse the data port from server response
        data_port = parse_data_port(response)
        if data_port is None:
            return

        # Server is opening data connection, connect to it
        data_socket = create_data_connection(data_port)

        # Receive directory listing on data connection
        file_list = data_socket.recv(4096).decode()
        print("\nDirectory Listing:")
        print(file_list)

        # Close data connection
        data_socket.close()

        # Receive completion message on control connection
        completion = ctrl_socket.recv(1024).decode().strip()
        print(f"Server: {completion}")


def handle_get(ctrl_socket, filename):
    """
    Handle 'get' command using two-connection architecture.
    Command sent on control connection, file received on data connection.
    """
    # Send command on control connection
    ctrl_socket.send(f"get {filename}\n".encode())

    # Receive response on control connection
    response = ctrl_socket.recv(1024).decode().strip()
    print(f"Server: {response}")

    if response.startswith("150"):
        # Parse the data port from server response
        data_port = parse_data_port(response)
        if data_port is None:
            return

        # Server is opening data connection, connect to it
        data_socket = create_data_connection(data_port)

        # Receive file on data connection
        with open(filename, 'wb') as f:
            while True:
                chunk = data_socket.recv(4096)
                if not chunk:
                    break
                f.write(chunk)

        # Close data connection
        data_socket.close()
        print(f"File '{filename}' downloaded successfully")

        # Receive completion message on control connection
        completion = ctrl_socket.recv(1024).decode().strip()
        print(f"Server: {completion}")

    elif response.startswith("550"):
        print("File not found on server.")


def handle_put(ctrl_socket, filename):
    """
    Handle 'put' command using two-connection architecture.
    Command sent on control connection, file sent on data connection.
    """
    # Check if file exists locally
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found locally")
        return

    # Send command on control connection
    ctrl_socket.send(f"put {filename}\n".encode())

    # Receive response on control connection
    response = ctrl_socket.recv(1024).decode().strip()
    print(f"Server: {response}")

    if response.startswith("150"):
        # Parse the data port from server response
        data_port = parse_data_port(response)
        if data_port is None:
            return

        # Server is ready, create data connection
        data_socket = create_data_connection(data_port)

        # Send file on data connection
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                data_socket.sendall(chunk)

        # Close data connection to signal end of transfer
        data_socket.close()
        print(f"File '{filename}' uploaded successfully")

        # Receive completion message on control connection
        completion = ctrl_socket.recv(1024).decode().strip()
        print(f"Server: {completion}")


def main():
    """
    Main client function.
    Creates persistent control connection and handles user commands.
    """
    # Create control connection socket
    ctrl_socket = socket.socket()

    try:
        # Connect to server's control port
        ctrl_socket.connect((SERVER_IP, CONTROL_PORT))

        # Receive welcome message
        welcome = ctrl_socket.recv(1024).decode().strip()
        print(welcome)
        print("\nAvailable commands: ls, get <filename>, put <filename>, quit")
        print("="*50)

        # Command loop
        while True:
            command = input("\n> ").strip()

            if not command:
                continue

            # Parse command
            parts = command.split()
            cmd = parts[0].lower()

            if cmd == 'ls':
                handle_ls(ctrl_socket)

            elif cmd == 'get':
                if len(parts) == 2:
                    handle_get(ctrl_socket, parts[1])
                else:
                    print("Usage: get <filename>")

            elif cmd == 'put':
                if len(parts) == 2:
                    handle_put(ctrl_socket, parts[1])
                else:
                    print("Usage: put <filename>")

            elif cmd == 'quit':
                ctrl_socket.send(b"quit\n")
                response = ctrl_socket.recv(1024).decode().strip()
                print(f"Server: {response}")
                break

            else:
                print(f"Unknown command: {cmd}")
                print("Available commands: ls, get <filename>, put <filename>, quit")

    except ConnectionRefusedError:
        print("Error: Could not connect to server. Make sure server is running.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close control connection
        ctrl_socket.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()
