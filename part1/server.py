import socket
import os
import threading

# FTP-like server with TWO connections:
# 1. Control Connection (port 11123) - for commands
# 2. Data Connection (dynamic port) - for file/data transfers

CONTROL_PORT = 11123
# Thread lock for synchronized logging
log_lock = threading.Lock()

def handle_data_connection(client_ctrl, ctrl_addr, operation, filename=None):
    """
    Handle data connection for file transfers and directory listings.
    This creates a separate connection for data transfer.
    Each client gets a dynamically assigned port to avoid conflicts.
    """
    # Create data socket with dynamic port allocation
    data_socket = socket.socket()
    data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
    data_socket.bind(('', 0))  # Port 0 = let OS assign available port
    data_socket.listen(1)

    # Get the actual port assigned by OS
    data_port = data_socket.getsockname()[1]

    with log_lock:
        print(f"[{ctrl_addr}] Opening data connection on port {data_port}")

    # Tell client we're ready for data connection (include port number)
    client_ctrl.send(f"150 Opening data connection on port {data_port}\n".encode())

    # Accept data connection from client
    data_conn, data_addr = data_socket.accept()
    with log_lock:
        print(f"[{ctrl_addr}] Data connection established from {data_addr}")

    try:
        if operation == "ls":
            # Send directory listing over data connection
            files = os.listdir('.')
            file_list = '\n'.join(files) if files else "No files found."
            data_conn.sendall(file_list.encode())

        elif operation == "get":
            # Send file over data connection
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        data_conn.sendall(chunk)
                with log_lock:
                    print(f"[{ctrl_addr}] File '{filename}' sent successfully")
            else:
                # This shouldn't happen as we check before, but just in case
                data_conn.send(b"ERROR: File not found")

        elif operation == "put":
            # Receive file over data connection
            with open(filename, 'wb') as f:
                while True:
                    chunk = data_conn.recv(4096)
                    if not chunk:
                        break
                    f.write(chunk)
            with log_lock:
                print(f"[{ctrl_addr}] File '{filename}' received successfully")

    finally:
        # Always close data connection after transfer
        data_conn.close()
        data_socket.close()
        with log_lock:
            print(f"[{ctrl_addr}] Data connection closed")

        # Send completion message on control connection
        client_ctrl.send(b"226 Transfer complete\n")


def handle_client(ctrl_conn, ctrl_addr):
    """
    Handle control connection with client.
    Commands are sent/received here, data transfers use separate connection.
    Each client thread handles both control and data connections independently.
    """
    with log_lock:
        print(f"[{ctrl_addr}] Control connection established")
    ctrl_conn.send(b"220 Welcome to FTP Server\n")

    while True:
        try:
            # Receive command on control connection
            data = ctrl_conn.recv(1024).decode().strip()

            if not data:
                break

            with log_lock:
                print(f"[{ctrl_addr}] Received command: {data}")

            if data.lower() == "ls":
                # Use data connection for directory listing
                handle_data_connection(ctrl_conn, ctrl_addr, "ls")

            elif data.lower().startswith('get'):
                parts = data.split()
                if len(parts) == 2:
                    filename = parts[1]
                    if os.path.exists(filename):
                        # Use data connection for file transfer
                        handle_data_connection(ctrl_conn, ctrl_addr, "get", filename)
                    else:
                        ctrl_conn.send(b"550 File not found\n")
                else:
                    ctrl_conn.send(b"501 Syntax error: GET <filename>\n")

            elif data.lower().startswith('put'):
                parts = data.split()
                if len(parts) == 2:
                    filename = parts[1]
                    # Use data connection for file upload
                    handle_data_connection(ctrl_conn, ctrl_addr, "put", filename)
                else:
                    ctrl_conn.send(b"501 Syntax error: PUT <filename>\n")

            elif data.lower() == 'quit':
                ctrl_conn.send(b"221 Goodbye!\n")
                break

            else:
                ctrl_conn.send(b"500 Unknown command\n")

        except Exception as e:
            with log_lock:
                print(f"[{ctrl_addr}] Error: {e}")
            ctrl_conn.send(f"500 Error: {str(e)}\n".encode())
            break

    # Close control connection
    ctrl_conn.close()
    with log_lock:
        print(f"[{ctrl_addr}] Control connection closed")


def main():
    """
    Main server function.
    Creates control connection socket and handles multiple clients concurrently.
    Each client gets its own thread with independent control and data connections.
    """
    # Create control connection socket
    ctrl_socket = socket.socket()
    ctrl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ctrl_socket.bind(('', CONTROL_PORT))
    ctrl_socket.listen(5)

    print("="*60)
    print("FTP Server with Multi-Threaded Two-Connection Architecture")
    print("="*60)
    print(f"Control connection listening on port {CONTROL_PORT}")
    print(f"Data connections use dynamically assigned ports")
    print(f"Ready to handle multiple concurrent clients")
    print("Waiting for clients...\n")

    try:
        while True:
            # Accept control connection
            ctrl_conn, ctrl_addr = ctrl_socket.accept()

            # Handle each client in a separate daemon thread
            # Daemon threads automatically terminate when main program exits
            client_thread = threading.Thread(
                target=handle_client,
                args=(ctrl_conn, ctrl_addr),
                daemon=True  # Ensures clean shutdown
            )
            client_thread.start()

            with log_lock:
                print(f"[MAIN] New client thread started for {ctrl_addr}")

    except KeyboardInterrupt:
        print("\n[MAIN] Server shutting down...")
    finally:
        ctrl_socket.close()
        print("[MAIN] Server closed.")


if __name__ == "__main__":
    main()
