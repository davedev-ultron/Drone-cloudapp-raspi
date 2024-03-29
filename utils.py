import base64

class Utils:    

# this method takes drone id and msg body and encodes into the byte
# the id will be 1 byte only
# encodes data into base64
    def create_datagram_message(drone_id, msg_body):
        return drone_id.encode() + base64.b64encode(msg_body)   

    def readNetworkMessage(socket):
        
        # read first 4 bytes that describe size
        body_size = int.from_bytes(socket.recv(4), byteorder='big')
        body = socket.recv(body_size)
        
        # this will contain proto object array
        return body
        
        
    def createNetworkMessage(msg_body_bytes):
        # serialized data from proto object that is byte array
        length = len(msg_body_bytes)
        # add the header with size, 4 bytes should be huge 
        length_encoded_to_4_bytes = (length).to_bytes(4, byteorder='big')
        
        return length_encoded_to_4_bytes + msg_body_bytes 