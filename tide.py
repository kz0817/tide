#!/usr/bin/env python3
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer

class TideHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hello")


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
