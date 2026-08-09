#!/usr/bin/env python3
#server file for my streamlink server
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import subprocess

CHANNELS = {
    "@ishowspeed": "https://twitch.tv/ishowspeed",
    "@kaicenat": "https://twitch.tv/kaicenat"
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        channel = self.path.removeprefix("/stream/").split("?")[0]

        if channel not in CHANNELS:
            self.send_error(404, "Unknown channel")
            return

        self.send_response(200)
        self.send_header("Content-Type", "video/mp2t")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        process = subprocess.Popen(
            [
                "/usr/bin/streamlink",
                "--stdout",
                "--quiet",
                CHANNELS[channel],
                "best",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        try:
            while True:
                data = process.stdout.read(64 * 1024)

                if not data:
                    break

                self.wfile.write(data)
                self.wfile.flush()

        except (BrokenPipeError, ConnectionResetError):
            pass

        finally:
            process.terminate()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
server.serve_forever()
