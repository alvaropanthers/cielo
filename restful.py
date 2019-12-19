#!/usr/bin/env python
import sys
import csv
import requests
import argparse
from pathlib import Path 

def Arguments():
    arg = argparse.ArgumentParser()
    arg.add_argument('METHOD', choices=['get', 'post'], help='Request method')
    arg.add_argument('ENDPOINT', help='Request endpoint URI fragment')
    arg.add_argument('-d', '--data', help='Data to send with request')
    arg.add_argument('-o', '--output', help='Output to .json or .csv file (default: dump to stdout)')

    return arg.parse_args()

class Request:
    def __init__(self, baseuri, endpoint, method, data=None):
        self.baseuri = baseuri
        self.endpoint = endpoint
        self.method = method
        self.data = data
        self.response = None

    def Send(self):
        self.Get() if self.method == 'get' else self.Post()
        if self.response.status_code < 200 or self.response.status_code  > 299:
            raise Exception("Error, request failed. Status_code not in 2xx")

    def Get(self):
        self.response = requests.get(self.baseuri + self.endpoint)
    
    def Post(self):
        self.response = requests.post(self.baseuri + self.endpoint, self.data)

class Output:
    def __init__(self, filename, response):
        self.filename = filename
        self.response = response

    def ToJson(self):
        data = self.response.text
        with open(self.filename, 'w') as OutFile:
            OutFile.write(data)

    def ToCsv(self):
        data = self.response.json()
        if isinstance(data, dict):
            fieldnames = [item for item in data]
        else:
            fieldnames = [item for item in data[0]]

        with open(self.filename, 'w', newline='') as OutFile:
            writer = csv.DictWriter(OutFile, fieldnames=fieldnames)
            writer.writeheader()

            if isinstance(data, dict):
                writer.writerow(data)
            else:
                for row in data:
                    writer.writerow(row)

    def ToConsole(self):
        print(self.response.text)

    def Write(self):
        if self.filename is None:
            self.ToConsole()
        elif Path(self.filename).suffix == '.json':
            self.ToJson()
        elif Path(self.filename).suffix == '.csv':
            self.ToCsv() 

def Main():
    args = Arguments()
    req = Request(baseuri='https://jsonplaceholder.typicode.com', endpoint=args.ENDPOINT, method=args.METHOD, data=args.data)

    try:
        req.Send()
        print("Response status code is {code}".format(code=req.response.status_code))
        tt = Output(filename=args.output, response=req.response)
        tt.Write()
    except Exception as e:
        print(e)
        sys.exit(1)

Main()