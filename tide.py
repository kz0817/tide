#!/usr/bin/env python3
import argparse
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class TideHandler(BaseHTTPRequestHandler):

    args = None

    def _dispatch(self, handler_map, path, default_handler):
        for re_path, handler in handler_map:
            if re_path.match(path):
                handler(self, path)
                break
        else:
            default_handler(path)

    def _response(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode())

    def _get_top_page(self, path):
        with open('ui/main.html', 'rb') as file:
            self._response(file.read())

    def _get_api_filelist(self, path):
        parsed_path = urlparse(path)
        query_params = parse_qs(parsed_path.query)
        location = query_params.get('location', '/')[0]
        # TODO: validate param_dir if it contains either '..'
        local_dir = os.path.join(self.args.root_dir, location.lstrip('/'))

        entries = []
        body = {'location': location, 'entries': entries}

        local_path = Path(local_dir)
        items = local_path.iterdir()
        for item in items:
            entries.append({
                'name': item.name,
                'isDir': item.is_dir(),
                'size':  item.stat().st_size,
                'modifiedTime': item.stat().st_mtime,
            })

        self._response(json.dumps(body))

    def do_GET(self):
        self._dispatch(self._handlers_get, self.path, self._get_top_page)

    _handlers_get = [
        (re.compile(r'/api/filelist'), _get_api_filelist)
    ]


def run(args):
    server_address = ('', args.port)
    TideHandler.args = args
    httpd = HTTPServer(server_address, TideHandler)
    print(f'Starting httpd server on port {args.port}...')
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="This is a sample script.")

    parser.add_argument('-p', '--port', default=3423)
    parser.add_argument('-r', '--root-dir', default='')

    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
