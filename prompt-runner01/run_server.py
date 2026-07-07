import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self._send(200, {'status': 'ok', 'service': 'prompt_runner'})
        else:
            self._send(404, {'error': 'not_found'})

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b''
        try:
            data = json.loads(body.decode('utf-8')) if body else {}
        except Exception:
            data = {'raw': body.decode('utf-8', errors='replace')}
        
        prompt = data.get('prompt', 'Default prompt')
        
        # Return a valid PromptRunnerInstruction payload matching Creator Core expectations
        payload = {
            "prompt": prompt,
            "module": "creator",
            "intent": "generate",
            "topic": "design",
            "tasks": ["create_blueprint"],
            "output_format": "json",
            "product_context": "testing"
        }
        self._send(200, payload)

if __name__ == '__main__':
    port = int(os.environ.get('PROMPT_RUNNER_PORT', '8003'))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Prompt Runner stub listening on 0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down prompt runner')
        server.server_close()
