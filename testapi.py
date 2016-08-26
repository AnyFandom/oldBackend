#!/usr/bin/python3

import requests
import argparse, sys
from termcolor import colored
import json
from pprint import pprint

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-t', '--type', default='POST')
    parser.add_argument ('-d', '--data', default='{}')
    parser.add_argument ('-u', '--url', default='/token')
    parser.add_argument ('--http_host', default='http://localhost:5000')

    return parser


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])

    data = json.loads(namespace.data)

    r = requests.request(namespace.type, namespace.http_host+namespace.url, data=data)

    color = 'white'
    colors = {'success': 'green', 'fail': 'red', 'error': 'yellow'}

    try:
        raw = r.json()
        if 'status' in raw.keys():
            color = colors[raw['status']]
    except Exception as exc:
        print(exc)

    print(colored('Status code: {0}'.format(r.status_code), 'blue'))

    for key, value in r.headers.items():
        print(colored("{0}: {1}".format(key,value), 'blue'))

    print()
    
    print(colored(str(r.content, 'utf-8'), color))
