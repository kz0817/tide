#!/usr/bin/env python3
import argparse
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def is_file(path):
    print(path)
    file_path = Path(path)
    return file_path.exists() and file_path.is_file()


EXT_MIME_MAP = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',
    'json': 'application/json',
    'png': 'image/png',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
}

def guess_media_type(path):
    ext = path.split('.')[-1]
    return EXT_MIME_MAP.get(ext)


def get_query_parameter(path, param_name, default=None):
    parsed_path = urlparse(path)
    query_params = parse_qs(parsed_path.query)
    return query_params.get(param_name, default)[0]


class TideHandler(BaseHTTPRequestHandler):

    args = None

    def _dispatch(self, handler_map, path, default_handler):
        for re_path, handler in handler_map:
            if re_path.match(path):
                handler(self, path)
                break
        else:
            default_handler(path)

    def _response(self, content, content_type=None):
        self.send_response(200)
        if content_type is None:
            content_type = 'text/plain'
        self.send_header('Content-type', content_type)
        self.end_headers()

        if isinstance(content, str):
            content = content.encode()
        self.wfile.write(content)

    def _response_error(self, code):
        self.send_response(code)
        self.end_headers()

    def _response_file(self, local_path, mode='rb', default_mime='application/octet-stream'):
        if not is_file(local_path):
            self._response_error(404)
            self.end_headers()
            return

        mimetype = guess_media_type(local_path)
        if mimetype is None:
            mimetype = 'application/octet-stream'

        with open(local_path, mode) as file:
            self._response(file.read(), mimetype)

    def _get_web_files(self, path):
        if path == '/':
            self.send_response(301)
            self.send_header('Location', 'ui/main.html')
            self.end_headers()
            return

        # TODO: Use response_file
        # TODO: validate param_dir if it contains either '..'

        local_path = './' + path
        if not is_file(local_path):
            self.send_response(404)
            self.end_headers()
            return

        with open(local_path, 'r') as file:
            self._response(file.read(), guess_media_type(local_path))

    def _get_api_filelist(self, path):
        # TODO: use get query parameter
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

        self._response(json.dumps(body), 'applicationi/json')


    def _get_file(self, path):
        location = get_query_parameter(path, 'location')
        if location is None:
            self._response_error(400)
            return

        local_path = os.path.join(self.args.root_dir, location.lstrip('/'))
        self._response_file(local_path)

    def do_GET(self):
        self._dispatch(self._handlers_get, self.path, self._get_web_files)

    _handlers_get = [
        (re.compile(r'/api/filelist'), _get_api_filelist),
        (re.compile(r'/api/file'), _get_file)
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
