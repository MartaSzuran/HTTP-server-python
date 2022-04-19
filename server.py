# creating http server using sockets

import socket
import sys
import os


class TCPServer:
    """TCP server / creating connection."""
    def __init__(self, host_name, html_path):
        self.html_path = html_path
        self.host_ip = socket.gethostbyname(host_name)
        print(self.host_ip)
        self.port = 8000

    def start_server(self):
        # create socket object
        socket_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind() assigns the address specified by local address to the socket
        # bind() argument is a tuple
        socket_stream.bind((self.host_ip, self.port))

        # listen() for connections on a socket
        socket_stream.listen(5)
        print("Listening at", socket_stream.getsockname())

        # start while loop managing the connection
        while True:
            # return the address of our port
            connection, address = socket_stream.accept()
            print("Connection establish to address:", address)

            # take request line from the browser
            data = connection.recv(1024)
            decoded_data = data.decode()

            # pass it to the function handle request
            response = self.handle_request(decoded_data)

            # use connection to send back the response to the web browser
            connection.send(response)

            # close connection
            connection.close()

    def handle_request(self, data):
        """Function for handling with http requests, rewrite in subclass."""
        return data


class HTTPServer(TCPServer):
    # dict with status codes {code : reason}
    status_codes = {200: "OK",
                    404: "Not Found",
                    403: "Forbidden",
                    418: "I'm a teapot",
                    501: "Not implemented"}

    # dict with headers for the responses
    headers = {"Server": "MarHttpServer",
               "Content-Type": "text/html"}

    # HTTP methods - GET / POST
    http_methods = ["GET", "POST"]

    def handle_request(self, data_from_browser):
        # sending response for the request
        # response example:
        # # HTTP / 1.1 200 OK             # The first line is called the response line
        # # Server: Tornado / 4.3         # Response header
        # # Date: Wed, 18Oct 2017         # Response header
        # # Content - type: text / html   # Response header
        # # Content - Length: 13          # Response header
        # # Blank line
        # # Hello, world!                 # Response body

        # read requests method
        request = HTTPRequest(data_from_browser)
        print(request)

        # recognise the request method
        if request.method not in self.http_methods:
            # response body should be the answer
            response_line = self.resp_line(status_code=501)
        elif request.method == "GET":
            response_line = self.resp_line(status_code=200)
        elif request.method == "POST":
            response_line = self.resp_line(status_code=404)
        else:
            print("Something is wrong with the request method.")
            sys.exit()

        # create headers
        header_lines = self.header_lines()

        # blank line
        blank_line = self.blank_l()

        # Response body
        if request.method == "GET":
            resp = self.get_method(request.uri)
            response_body = self.r_body(resp)

        return b"".join([response_line, header_lines, blank_line, response_body])

    # response line
    def resp_line(self, status_code):
        response = ""
        if status_code in self.status_codes:
            reason = self.status_codes[status_code]
            # example : HTTP / 1.1 200 OK
            response = "HTTP/1.1 %s %s\r\n" % (status_code, reason)

        return response.encode()

    # create headers
    def header_lines(self, extra_headers=None):
        """Create headers. For any different type of content,
        I can create extra headers for adding it to the massage."""

        # create local copy of headers for adding any additional once
        headers_copy = self.headers.copy()

        # if there are any extra add it to the dict
        if extra_headers:
            headers_copy.update(extra_headers)

        # create an empty string for adding headers
        headers = ""

        for header in headers_copy:
            headers += "%s: %s\r\n" % (header, headers_copy[header])

        # call encode to convert string to bytes
        return headers.encode()

    # blank line
    def blank_l(self):
        blank = b"\r\n"
        return blank

    # response body
    def r_body(self, resp):
        if resp:
            resp_body = b"".join([resp])
        else:
            resp_body = b"There is nothing..."
        return resp_body

    def get_method(self, uri):
        # add uri to the file path
        if uri == "/":
            uri_req = "/index.html"
            path_to_get_req = self.html_path + uri_req
        else:
            path_to_get_req = self.html_path + uri

        # check if requested path exists
        # if it does open and read
        if os.path.exists(path_to_get_req):
            with open(path_to_get_req, "rb") as f:
                uri_response = f.read()
        else:
            uri_req = "/templates/not_found.html"
            path_to_get_req = self.html_path + uri_req
            with open(path_to_get_req, "rb") as f:
                uri_response = f.read()

        return uri_response


class HTTPRequest:
    """Class for grabbing HTTP request"""
    # taking specific first line elements
    # f.e. : GET /index.html HTTP/1.1
    # GET           - method - Method tells the server what action the client wants to perform on the URI
    # /index.html   - URI    - URI stands for Uniform Resource Identifier.
    #                          This tells the server on which resource or page or anything else the client
    #                          wants to perform the request.
    # HTTP/1.1      - HTTP   - version is the version of HTTP the client supports or wants the server
    #                          to use for the response.
    #                        - The most widely used version of HTTP is 1.1.
    # \r\n          - Line break - this tells the server that the request line has ended and the request
    #                              headers follow after this line.

    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_ver = None

        self.reading_request(data)

    def __str__(self):
        return str(self.method) + " " + str(self.uri) + " " + str(self.http_ver)

    def reading_request(self, data):
        """Read the first line from the request"""
        # first need to decode request
        request = data

        req_first_line = self.first_line(request)

        words_list = self.separate(req_first_line)
        self.method = words_list[0]
        self.uri = words_list[1]
        self.http_ver = words_list[2]
        return words_list

    # taking first line
    def first_line(self, req):
        # create empty string for first line from the request
        first_l = ""
        for letter in req:
            # every line from Http request ends with "\r\n"
            if letter == "\r":
                break
            else:
                first_l += letter
        return first_l

    # separate first line content
    def separate(self, r_f_l):
        """create the list with separate words from request first line"""
        words = r_f_l.split()
        return words

