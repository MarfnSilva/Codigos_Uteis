import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 5506)
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    
    # Send data
    ReaderModule = 101
    ReaderHWID = 1
    CardNumber = 5610737
    FC = 0
    EventPictureID = 0
    message = f'{ReaderModule}.{ReaderHWID}|{CardNumber}|{FC}|{EventPictureID}\n'
    print ('sending "%s"' % message)
    sock.sendall(message.encode('utf-8'))

    # Look for the response
    amount_received = 0
    amount_expected = len(message)
    
    while amount_received < amount_expected:
        data = sock.recv(900)
        if not data:
            break
        amount_received += len(data)
        print ('received "%s"' % data)
        break

finally:
    print ('closing socket')
    sock.close()
    
    