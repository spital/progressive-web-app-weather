
import http.server
import socket
import ssl
import os
import sys


if len(sys.argv) > 1:
    os.chdir(sys.argv[1])


if len(sys.argv) > 2:
    port = int(sys.argv[2])


port = 9000
server_address = ('0.0.0.0', port)
certfile = "cert.pem"
keyfile = "key.pem"

if not os.path.isfile(certfile):
    print("Generating certificate ...")
    os.system(f"openssl req -nodes -x509 -newkey rsa:2048 -keyout {keyfile} -out {certfile} -days 365 -subj '/CN=mylocalhost'")

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    remoteip = s.getsockname()[0]

print(f"Open https://localhost:{port} or remotely https://{remoteip}:{port}")

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        '': 'application/octet-stream',
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.svg':	'image/svg+xml',
        '.css':	'text/css',
        '.js': 'application/x-javascript',
        '.wasm': 'application/wasm',
        '.json': 'application/json',
        '.xml': 'application/xml',
    }

    def end_headers(self):
        # Include additional response headers here. CORS for example:
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

class MHTTPServer(http.server.HTTPServer):
    def get_request(self):
        newsock, client = self.socket.accept()
        newsock.settimeout(self.timeout)
        newsock.do_handshake()
        return newsock, client

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.check_hostname = False
#ctx.load_cert_chain(certfile='localhost.pem')  # with key inside
ctx.load_cert_chain(keyfile=keyfile, certfile=certfile)
httpd = MHTTPServer(server_address, CORSHTTPRequestHandler)
httpd.timeout = 5
httpd.socket = ctx.wrap_socket(
    httpd.socket, server_side=True,
    do_handshake_on_connect=False
)
httpd.serve_forever()
