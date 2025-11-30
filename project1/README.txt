================================================================================
SIMPLIFIED FTP SERVER AND CLIENT
================================================================================

TEAM MEMBERS
--------------------------------------------------------------------------------
1. Amir Valiulla (amir.valiulla@csu.fullerton.edu)
2. Joshua Yee (joshuayee@csu.fullerton.edu)
3. Randolph Brummett (rbrummett@csu.fullerton.edu)
4. Ric Escalante (rescalante12@csu.fullerton.edu)
5. Kush Bajaria (bajariakush@csu.fullerton.edu)

PROGRAMMING LANGUAGE
--------------------------------------------------------------------------------
Python 3


HOW TO EXECUTE
--------------------------------------------------------------------------------

1. Start the server:
   python3 server.py

2. Start the client (in separate terminal):
   python3 client.py

3. Available commands in client:
   > ls                 (list files on server)
   > get <filename>     (download file from server)
   > put <filename>     (upload file to server)
   > quit               (exit)


PROTOCOL DESIGN - TWO CONNECTION ARCHITECTURE
--------------------------------------------------------------------------------

This FTP implementation uses TWO separate TCP connections:

1. CONTROL CONNECTION (Port 11123)
   - Persistent connection for entire session
   - Used for sending commands and receiving status codes
   - Remains open throughout client session

2. DATA CONNECTION (Dynamic Port)
   - Temporary connection created for each file/data transfer
   - Server assigns available port dynamically
   - Opens for ls/get/put operations, closes after transfer
   - Port number sent to client via "150" status code

How it works:
  1. Client sends command (ls/get/put) on CONTROL connection
  2. Server responds "150 Opening data connection on port XXXXX"
  3. Client connects to that port for DATA connection
  4. File/data transferred over DATA connection
  5. DATA connection closes
  6. Server sends "226 Transfer complete" on CONTROL connection
  7. CONTROL connection stays open for next command


COMMANDS IMPLEMENTATION
--------------------------------------------------------------------------------

LS Command:
  - Client sends "ls" on control connection
  - Server opens data connection
  - Server sends directory listing over data connection
  - Data connection closes
  - Works correctly 

GET Command:
  - Client sends "get filename" on control connection
  - Server checks if file exists
  - If exists: server opens data connection and sends file (4096 byte chunks)
  - If not: server returns "550 File not found"
  - Data connection closes after transfer
  - Works correctly 

PUT Command:
  - Client sends "put filename" on control connection
  - Server opens data connection
  - Client sends file over data connection (4096 byte chunks)
  - Data connection closes after transfer
  - Works correctly 


STATUS CODES
--------------------------------------------------------------------------------
220 - Welcome to FTP Server
150 - Opening data connection on port <PORT>
226 - Transfer complete
221 - Goodbye
550 - File not found
501 - Syntax error
500 - Unknown command


SPECIAL NOTES
--------------------------------------------------------------------------------
- Server uses multi-threading to handle multiple clients simultaneously
- Dynamic port allocation prevents conflicts between concurrent clients
- Binary file transfer mode (supports all file types)
- Server must be running before starting client
- Both programs connect on localhost (127.0.0.1) by default
- File integrity preserved through binary transfer mode


TESTING
--------------------------------------------------------------------------------
All commands tested and working:
-ls - displays directory listing
 - get - downloads files successfully
-put - uploads files successfully
 -Two connections verified using netstat
- Multiple clients can connect simultaneously
- File integrity maintained (tested with md5 checksums)


================================================================================
