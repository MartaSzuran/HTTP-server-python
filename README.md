# Http-server-python
Web server based on partial implementation of HTTP 1.1 protocol 

Technology:
- python
- html5

Features:
- server created with python sockets library 
- using port 80
- user need to provide file path to directory
- heandling with methods "GET" and "POST"
- searching requested web page - return valid response - if not exist returns page_not_found.html
- HTML files has hyperlinks to other pages

Example directory:
  static:
    favicon.ico
    see.jpg
  templates:
    about.html
    page_not_found.html
  index.html
  main.py
  server.py
