#!/usr/bin/env python3
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer

class TideHandler(BaseHTTPRequestHandler):

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

    def do_GET(self):
        self._dispatch(self._handlers_get, self.path, self._get_top_page)

    _handlers_get = [
    ]


def run(args):
    server_address = ('', args.port)
    httpd = HTTPServer(server_address, TideHandler)
    print(f'Starting httpd server on port {args.port}...')
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="This is a sample script.")

    parser.add_argument('-p', '--port', default=3423)

    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
