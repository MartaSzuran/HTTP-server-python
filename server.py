# creating http server using sockets

import socket
import sys
import os
import mimetypes


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
    """Object takes request from the browser and returns response."""
    # dictionary with status codes {code : reason}
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
        """Function for reading the browser request and return the response."""
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
        # print(request)

        # recognise the request method
        if request.method not in self.http_methods:
            response_line = self.resp_line(status_code=501)
        elif request.method == "GET":
            response_line = self.resp_line(status_code=200)
        elif request.method == "POST":
            response_line = self.resp_line(status_code=404)
        else:
            print("Unknown request method.")
            sys.exit()

        # response body
        if request.method == "GET":
            response_body = self.get_method(request.uri)

        # create headers
        header_lines = self.header_lines(request.uri)

        # blank line
        blank_line = self.blank_l()

        return b"".join([response_line, header_lines, blank_line, response_body])

    # response line
    def resp_line(self, status_code):
        response = ""
        if status_code in self.status_codes:
            reason = self.status_codes[status_code]
            # example : HTTP / 1.1 200 OK
            response = "HTTP/1.1 %s %s\r\n" % (status_code, reason)
        return response.encode()

    def header_lines(self, file_extension_from_uri):
        """Return response headers, check content type, if argument is not Null,
        change content type and return requested one."""

        # create local copy of headers for adding any additional once
        headers_copy = self.headers.copy()

        # find our requested content type
        # using mimetypes.guess_type - it returns tuple - tuple[0] = content type / tuple[1] = encoding
        current_content_type = mimetypes.guess_type(file_extension_from_uri)[0] or "text/html"
        print(current_content_type)

        # set proper content type
        headers_copy["Content-Type"] = current_content_type

        # create an empty string for adding headers
        headers = ""

        for header in headers_copy:
            headers += "%s: %s\r\n" % (header, headers_copy[header])

        # call encode to convert string to bytes
        return headers.encode()

    def blank_l(self):
        """Returns binary black line \r\n"""
        blank = b"\r\n"
        return blank

    def get_method(self, uri):
        """Check if requested URI exists, returns html file in binary."""
        # add uri to the file path
        if uri == "/":
            # if bare slash and index.html to the file path
            uri_req = "/index.html"
            path_to_get_req = self.html_path + uri_req
        else:
            path_to_get_req = self.html_path + uri

        # check if requested path exists
        if os.path.exists(path_to_get_req):
            # if it does open and read in binary
            with open(path_to_get_req, "rb") as f:
                uri_response = f.read()
        else:
            # else open not_found.html
            uri_req = "/templates/not_found.html"
            path_to_get_req = self.html_path + uri_req
            with open(path_to_get_req, "rb") as f:
                uri_response = f.read()
        return uri_response


class HTTPRequest:
    """Class for grabbing HTTP request."""
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
        # set method, uri and http_ver to None then with function reading_request set their values
        self.method = None
        self.uri = None
        self.http_ver = None

        # read the first line from the browser request and set the method, uri and http_ver values
        self.reading_request(data)

    def __str__(self):
        return str(self.method) + " " + str(self.uri) + " " + str(self.http_ver)

    def reading_request(self, data):
        """Read the first line from the request and it as a string list."""
        # create local variable to store browser request
        request = data

        # take first line from the browser request
        req_first_line = self.first_line(request)
        # print(req_first_line)

        # list of strings from the first line of the browser request
        words_list = self.separate(req_first_line)
        self.method = words_list[0]
        self.uri = words_list[1]
        self.http_ver = words_list[2]
        return words_list

    def first_line(self, req):
        """Take first line from the request."""
        # create empty string for first line from the request
        first_l = ""
        for letter in req:
            # every line from Http request ends with "\r\n"
            if letter == "\r":
                break
            else:
                first_l += letter
        return first_l

    def separate(self, r_f_l):
        """Create the list with separate words from request first line."""
        # separate first line content using split function
        words = r_f_l.split()
        return words
