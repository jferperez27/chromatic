import socket

class URL:
    def __init__(self, url):
        
        # Separate url and scheme
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        # Separate host
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):

        # Instantiate socket for communication
        s = socket.socket(
            family=socket.AF_INET, # Address Family
            type=socket.SOCK_STREAM, # Send arbitrary amt of data
            proto=socket.IPPROTO_TCP # Protocol
        )

        s.connect((self.host, 80))

        req = "GET {} HTTP/1.0\r\n".format(self.path)
        req += "Host: {}\r\n".format(self.host)
        req += "\r\n"
        
        s.send(req.encode("utf8"))

        # Parses server response from bytes into string via utf8 encoding
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        # Parse headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        # Checks for unusual data
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content


def show(body):
    in_tag = False
    for char in body:
        if char == "<":
            in_tag = True
        elif char == ">":
            in_tag = False
        elif not in_tag:
            print(char, end="")

def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))