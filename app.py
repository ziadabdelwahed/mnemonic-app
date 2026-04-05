from http.server import BaseHTTPRequestHandler, HTTPServer
from main import MnemonicEngine

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = MnemonicEngine.generate(128)
        words = result.mnemonic.split()

        html = "<h2>Mnemonic Generator</h2>"
        html += "<a href='/'>Generate New</a><br><br>"

        for i, word in enumerate(words, 1):
            html += f"{i}- {word}<br>"

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

server = HTTPServer(("0.0.0.0", 8000), MyHandler)
print("Server running on http://localhost:8000")
server.serve_forever()