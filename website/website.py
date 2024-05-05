import socketserver
import os
import logging

import http.server

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler for logging
log_file = 'logfile.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the file handler to the root logger
logging.getLogger().addHandler(file_handler)

class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Get the file name from the requested URL
        file_name = self.path.strip('/')
        if os.path.exists(file_name):
            # Check if it's a directory, then serve index.html
            if os.path.isdir(file_name):
                file_name = os.path.join(file_name, 'landingpage.html')
            
            # Serve the requested file
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            # File not found, return 404
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
            logging.error(f'File not found: {file_name}')

# Set the port number you want to use
PORT = 8000

# Create the server with the custom request handler
httpd = socketserver.TCPServer(("", PORT), CustomRequestHandler)

logging.info("Serving at port %s", PORT)

# Start the HTTP server
httpd.serve_forever()