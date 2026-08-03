import http.server
import socketserver
import urllib.request
import urllib.error
import urllib.parse

PORT = 8000

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/unpkg/'):
            url_path = self.path[len('/unpkg/'):]
            url_path = urllib.parse.unquote(url_path)
            
            full_url = f"https://cdn.jsdelivr.net/npm/{url_path}"
            print(f"Proxying to jsDelivr: {full_url}")
            
            try:
                req = urllib.request.Request(
                    full_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req) as response:
                    self.send_response(200)
                    content_type = response.headers.get('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Type', content_type)
                    self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                    self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
                    self.end_headers()
                    self.wfile.write(response.read())
            except urllib.error.HTTPError as e:
                self.send_error(e.code, f"Proxy error: {e.reason}")
            except Exception as e:
                self.send_error(500, f"Proxy internal error: {str(e)}")
            return
            
        super().do_GET()

    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
    print(f"Сервер PEWA успешно запущен на http://localhost:{PORT}")
    httpd.serve_forever()
