# from flask import Flask, send_from_directory

# app = Flask(__name__)

# @app.route('/')
# def serve_index():
#     return send_from_directory('html', 'index.html')

# if __name__ == '__main__':
#     app.run(debug=True)




import http.server
import socketserver
import os
import webbrowser

PORT = 8000
DIRECTORY = "html"

os.chdir(DIRECTORY)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}/index.html")
    httpd.serve_forever()
