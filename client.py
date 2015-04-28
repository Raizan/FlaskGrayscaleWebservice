# Client
# Sends batch of tasks to workers via webservice
__author__ = 'ITS_Student'

import random
import time
import os
import threading
import json
import sys
from requests import post
import base64

class Client:
    def __init__(self, workers):
        # List of address
        self.workers = workers

class Main(object):
    def __init__(self, workers_list, path_to_input, path_to_output, pack_quantity):
        self.workers_list = workers_list
        self.path_to_input = path_to_input
        
        output_length = len(path_to_output)
        if path_to_output[output_length - 1] == '/':
            self.path_to_output = path_to_output
        else:
            self.path_to_output = path_to_output + '/'

        self.pack_quantity = int(pack_quantity)
        self.file_list = os.listdir(self.path_to_input)
        self.node_list = []
        self.threads = []
        self.elapsed_time = 0
    
    def worker(self, node, file_list):
        for filename in file_list:
            print node.workers + ": Processing " + filename
            file_format = filename[-4:]
            open_file = open(self.path_to_input + filename, 'rb')
            read_file = open_file.read()
            open_file.close()
            encoded = base64.b64encode(read_file)
            
            #Change
            data = {
                    "data": encoded,
                    "format": file_format
                   }
            retval = post('http://'+ node.workers + '/api/imageconverter/v0.1/', data=data).json()
            result = base64.b64decode(retval['result'])

            file_open = open(self.path_to_output + filename, 'wb')
            file_open.write(result)
            file_open.close()
            #Change

    def run(self):
        if self.path_to_input[-1] != '/':
            self.path_to_input += '/'
        
        # Connect to server
        for workers in self.workers_list:
                self.node_list.append(Client(workers))

        i = 0
        j = self.pack_quantity
        server_selector = 0
        
        start_time = time.time()
        while True:
            if len(self.file_list) == 0:
                break
            
            if i == len(self.file_list):
                break
            
            if j > len(self.file_list):
                j = len(self.file_list)
            
            if server_selector == len(self.node_list):
                server_selector = 0
            
            t = threading.Thread(target=self.worker, args=(self.node_list[server_selector], self.file_list[i:j]))
            self.threads.append(t)
            t.start()
            for files in range(i, j):
                del self.file_list[0]
            
            server_selector += 1
        
        for thread in self.threads:
            thread.join()

        self.elapsed_time = time.time() - start_time

# Main Program
if __name__ == "__main__":
    path_to_input = None
    path_to_output = None
    
    print "How many servers do you want to use?"
    qty = raw_input()
    address_list = []
    for node in range(int(qty)):
        if node == 0:
            print "Usage: [ip_address:port]"
            print "Example: Localhost:9000"
        
        address_list.append(raw_input())
    
    print "Enter input folder"
    print "Usage: /path/to/input"
    print "Example: /home/input"
    while True:
        path_to_input = raw_input()
        if not os.path.isdir(path_to_input):
            print "Invalid argument: Input path is incorrect. Make sure it is a directory, not a file."
        
        else:
            break

    print "Enter output folder"
    print "Usage: /path/to/output"
    print "Example: /home/output"
    while True:
        path_to_output = raw_input()
        if not os.path.isdir(path_to_output):
            print "Invalid argument: Input path is incorrect. Make sure it is a directory, not a file."
        
        else:
            break

    print "How many files to distribute ?"
    pack_quantity = raw_input()
    
    main = Main(address_list, path_to_input, path_to_output, pack_quantity)
    main.run()
    
    print "Sending time " + str(main.elapsed_time)

