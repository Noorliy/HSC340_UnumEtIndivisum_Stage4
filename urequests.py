import usocket
import ujson

def request(method, url, data=None, json=None, headers={}, stream=None):
    try:
        proto, dummy, host, path = url.split('/', 3)
    except ValueError:
        proto, dummy, host = url.split('/', 2)
        path = ''
    if proto == 'http:':
        port = 80
    elif proto == 'https:':
        import ussl
        port = 443
    else:
        raise ValueError('Unsupported protocol: ' + proto)

    if ':' in host:
        host, port = host.split(':', 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][4]
    s = usocket.socket()
    s.connect(addr)
    if proto == 'https:':
        import ussl
        s = ussl.wrap_socket(s, server_hostname=host)

    s.write(b'%s /%s HTTP/1.0\r\n' % (method.encode(), path.encode()))
    s.write(b'Host: %s\r\n' % host.encode())

    for k in headers:
        s.write(k.encode())
        s.write(b': ')
        s.write(headers[k].encode())
        s.write(b'\r\n')

    if json is not None:
        assert data is None
        data = ujson.dumps(json)
        s.write(b'Content-Type: application/json\r\n')

    if data:
        s.write(b'Content-Length: %d\r\n' % len(data))
    s.write(b'\r\n')

    if data:
        s.write(data.encode())

    l = s.readline()
    protover, status, msg = l.split(None, 2)
    status = int(status)
    reason = msg.strip()

    while True:
        l = s.readline()
        if not l or l == b'\r\n':
            break

    class Response:
        def __init__(self, s):
            self.raw = s
            self.encoding = 'utf-8'
            self._cached = None

        def close(self):
            if self.raw:
                self.raw.close()
                self.raw = None

        @property
        def content(self):
            if self._cached is None:
                self._cached = self.raw.read()
                self.raw.close()
                self.raw = None
            return self._cached

        def text(self):
            return str(self.content, self.encoding)

        def json(self):
            import ujson
            return ujson.loads(self.content)

    resp = Response(s)
    resp.status_code = status
    resp.reason = reason
    return resp

def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)
