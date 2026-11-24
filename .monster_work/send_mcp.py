import argparse
import json
import socket
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--type', default='execute_code')
parser.add_argument('--file', type=Path)
parser.add_argument('--code')
parser.add_argument('--path')
parser.add_argument('--timeout', type=int, default=50)
options = parser.parse_args()

params = {}
if options.file:
    file = str(options.file.resolve())
    params['code'] = f'exec(compile(open({file!r}, encoding="utf-8").read(), {file!r}, "exec"), {{"__name__": "__main__"}})'
if options.code:
    params['code'] = options.code
if options.path:
    params.update(filepath=options.path, max_size=1200)
with socket.create_connection(('127.0.0.1', 9876), timeout=options.timeout) as client:
    client.sendall(json.dumps({'type': options.type, 'params': params}).encode())
    chunks = bytearray()
    while block := client.recv(16384):
        chunks.extend(block)
        try:
            response = json.loads(chunks)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        print(json.dumps(response, indent=2, ensure_ascii=True))
        raise SystemExit(0 if response.get('status') == 'success' else 1)
raise RuntimeError('No JSON response')
