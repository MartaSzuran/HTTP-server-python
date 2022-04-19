from server import HTTPServer
import socket

import sys
import os

# take first argument and if there is none given give an error and exit
try:
    path_to_html_files = sys.argv[1]
    print(path_to_html_files)
except IndexError:
    print("Path to html files is required!")
    sys.exit()

# check if the path exists and if it is change "\" to "/"
if os.path.exists(path_to_html_files):
    print("html path exists.")
    html_path = path_to_html_files.replace("\\", "/")
    print(html_path)
else:
    print("Path to html files is invalid!")
    sys.exit()


host_name = socket.gethostname()
server = HTTPServer(host_name, html_path)

server.start_server()
