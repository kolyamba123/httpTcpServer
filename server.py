from lxml import etree, objectify
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import socket
import time

HOST_NAME = 'localhost'
PORT_NUMBER = 9000

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # print(self.headers)
        tcp_host_header = str(self.headers['X-TCP-Host'])
        tcp_port_header = str(self.headers['X-TCP-Port'])
        tcp_path_header = str(self.headers['X-TCP-Path'])
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        response = BytesIO()

        mess = prepareXml(body)
        resp = tcp_msg(tcp_host_header, tcp_port_header, mess)
        #Check if recieved xml or not
        content_type = 'text'
        try:
            textString = str(resp).encode()
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.fromstring(textString, parser)
            content_type = 'application/xml'
        except Exception:
            content_type = 'text'

        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(str(resp).encode())

def prepareXml(textString):
    parser = etree.XMLParser(remove_blank_text=True)
    textString2 = textString.decode("utf-8")
    tree = etree.fromstring(textString2, parser)
    result = etree.tostring(tree, pretty_print=True, method="xml", encoding='unicode', xml_declaration = False)
    return result

def tcp_msg(host, port, msg):

    ss = msg.encode('utf8')
    MESSAGE = ss

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Try connect to " + str(host) + ":" + str(port))
    s.connect((host, int(port)))
    print("Send message...")
    print("request: ", MESSAGE)
    s.send(MESSAGE)
    print ("Receive data...")
    data = recv_timeout(s)
    s.close
    print ("response: ", data)

    return data.decode("utf-8")

def recv_timeout(the_socket, timeout=2):
    BUFFER_SIZE = 2048
    # make socket non blocking
    the_socket.setblocking(0)

    # total data partwise in an array
    total_data = []
    data = ''
    # beginning time
    begin = time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break

        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break

        # recv something
        try:
            data = the_socket.recv(BUFFER_SIZE)
            if data:
                total_data.append(data)
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass

    # join all parts to make final string
    return b''.join(total_data)

if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))