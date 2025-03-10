#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def is_file(path):
    print(path)
    file_path = Path(path)
    return file_path.exists() and file_path.is_file()


def guess_media_type(path):
    mime_type, _ = mimetypes.guess_type(path)
    return mime_type


def get_query_parameter(path, param_name, default=None):
    parsed_path = urlparse(path)
    query_params = parse_qs(parsed_path.query)
    return query_params.get(param_name, default)[0]


def get_content_path(base_path, location):
    # TODO: validate location if it contains either '..'
    return os.path.join(base_path, location.lstrip('/'))

class TideHandler(BaseHTTPRequestHandler):

    args = None
    prog_dir = None

    def _dispatch(self, handler_map, path, default_handler=None):
        for re_path, handler in handler_map:
            if re_path.match(path):
                handler(self, path)
                break
        else:
            if default_handler is not None:
                default_handler(path)
            else:
                self.send_error(404)

    def _response(self, content, content_type=None):
        self.send_response(200)
        if content_type is None:
            content_type = 'text/plain'
        self.send_header('Content-type', content_type)
        self.end_headers()

        if isinstance(content, str):
            content = content.encode()
        self.wfile.write(content)

    def _response_file(self, local_path, mode='rb', default_mime='application/octet-stream'):
        if not is_file(local_path):
            self.send_error(404)
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

        local_path = get_content_path(self.prog_dir, path);
        self._response_file(local_path, 'r')

    def _get_api_filelist(self, path):
        location = get_query_parameter(path, 'location')
        local_dir = get_content_path(self.args.root_dir, location)

        entries = []
        body = {'location': location, 'entries': entries}

        local_path = Path(local_dir)
        items = local_path.iterdir()
        for item in items:
            try:
                item_stat = item.stat()
            except:
                continue

            entries.append({
                'name': item.name,
                'isDir': item.is_dir(),
                'size':  item_stat.st_size,
                'modifiedTime': item_stat.st_mtime,
            })

        self._response(json.dumps(body), 'applicationi/json')


    def _get_file(self, path):
        location = re.sub(r'^/file', '', path)
        if location is None:
            self.send_error(400)
            return

        local_path = get_content_path(self.args.root_dir, location)
        self._response_file(local_path)

    def _save_file(self, filename, content_length):
        CHUNK_SIZE = 8192
        with open(filename, 'bx') as output_file:
            bytes_received = 0
            while bytes_received < content_length:
                chunk = self.rfile.read(min(CHUNK_SIZE, content_length - bytes_received))
                if not chunk:
                    break
                output_file.write(chunk)
                bytes_received += len(chunk)

        if bytes_received != content_length:
            print(f'Error: expected: {content_length}, actual: {bytes_received}')
            self.send_error(400, 'Invalid content length')
            os.remove(filename)
            return False

        return True

    def _create_dir(self, dir_name):
        dir_path = get_content_path(self.args.root_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def _post_file(self, path):
        content_length = int(self.headers['Content-Length'])

        # setup filename
        filename = self.headers.get('X-File-Name')
        if filename is None:
            print('Missing parameter: X-File-Name')
            self.send_error(400)
            return

        # setup directory
        dir_name = self.headers.get('X-File-Dir')
        dir_path = self.args.root_dir
        if dir_name is not None:
            dir_path = self._create_dir(dir_name)
        file_path = get_content_path(dir_path, filename)

        try:
            succeeded = self._save_file(file_path, content_length)
            if not succeeded:
                return
        except FileExistsError:
            print(f'Error: {filename}: already exists.')
            self.send_error(409)
            return

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self._dispatch(self._handlers_get, self.path, self._get_web_files)

    def do_POST(self):
        self._dispatch(self._handlers_post, self.path)

    _handlers_get = [
        (re.compile(r'/api/filelist'), _get_api_filelist),
        (re.compile(r'/file'), _get_file)
    ]

    _handlers_post = [
        (re.compile(r'/api/upload'), _post_file),
    ]


def run(args):
    server_address = (args.bind, args.port)
    TideHandler.args = args
    TideHandler.prog_dir = os.path.dirname(os.path.abspath(__file__))
    httpd = ThreadingHTTPServer(server_address, TideHandler)
    print(f'Starting httpd server on port {args.port}...')
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="This is a sample script.")

    parser.add_argument('-p', '--port', default=3423)
    parser.add_argument('-r', '--root-dir', default='')
    parser.add_argument('-b', '--bind', default='', help='Ex: 127.0.0.1')

    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
