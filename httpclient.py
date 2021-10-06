#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data = data.split('\r\n')
        code = data[0].split(' ')
        return int(code[1])

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        if len(data.split('\r\n\r\n')) == 2:
            return data.split('\r\n\r\n')[1]
        return ''

    def get_datas(self, data):
        header = self.get_headers(data)
        return self.get_body(data), self.get_code(header)
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        r = urllib.parse.urlparse(url)
        path = r.path
        # connect
        if ':' in r.netloc:
            self.connect(r.netloc.split(':')[0], int(r.netloc.split(':')[1]))
        else:
            self.connect(r.netloc, 80)
        # send request
        host = "Host: " + r.netloc + '\r\n'
        header = 'GET ' + path + ' HTTP/1.1\r\n' + host + 'Connection: close\r\n\r\n'
        self.sendall(header)
        # get response
        data = self.recvall(self.socket)
        body, code = self.get_datas(data)
        # close connection
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        r = urllib.parse.urlparse(url)
        path = r.path
        # connect
        if ':' in r.netloc:
            self.connect(r.netloc.split(':')[0], int(r.netloc.split(':')[1]))
        else:
            self.connect(r.netloc, 80)
        # send request
        host = "Host: " + r.netloc + '\r\n'
        header = 'POST ' + path + ' HTTP/1.1\r\n' + host
        # get content
        if args != None:
            content = '&'.join([i+'='+args[i] for i in args])
            content_length = "Content-Length: " + str(len(content.encode('utf-8'))) + '\r\n'
            content_type = "Content-Type: application/x-ww-form-urlencoded\r\n"
            header += content_length + content_type + '\r\n' + content + '\r\n'
        else:
            header += "Content-Length: 0\r\nContent-Type: application/x-ww-form-urlencoded\r\n\r\n"
        self.sendall(header)
        # get response
        data = self.recvall(self.socket)
        body, code = self.get_datas(data)
        # close connection
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
