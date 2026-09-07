"""HTTP smoke check of real containers started by make all."""
import json
import time
from urllib.request import Request, urlopen
from urllib.error import URLError


def request(url, method="GET", data=None):
    body = None if data is None else json.dumps(data).encode()
    req = Request(url, data=body, method=method,
                  headers={"Accept": "application/json", "Content-Type": "application/json"})
    with urlopen(req, timeout=10) as response:
        raw = response.read()
        return response.status, raw


for url in ["http://127.0.0.1:8000/api/tasks/", "http://127.0.0.1:3000/"]:
    for attempt in range(90):
        try:
            status, body = request(url)
            assert status == 200
            if url.endswith("3000/"):
                assert b'<div id="root"></div>' in body
            print(f"PASS {url}: HTTP {status}", flush=True)
            break
        except (URLError, TimeoutError, ConnectionError):
            time.sleep(2)
    else:
        raise RuntimeError(f"Service not ready: {url}")

base = "http://127.0.0.1:3000/api/tasks/"
status, raw = request(base, "POST", {"title": "Make + Docker smoke check", "description": "Temporary CI task", "completed": False})
assert status == 201, status
item = json.loads(raw)
try:
    status, raw = request(base + str(item["id"]) + "/", "PATCH", {"completed": True})
    assert status == 200 and json.loads(raw)["completed"] is True
    status, raw = request(base)
    assert any(task["id"] == item["id"] for task in json.loads(raw))
    print("PASS frontend proxy: create, update and list tasks", flush=True)
finally:
    status, _ = request(base + str(item["id"]) + "/", "DELETE")
    assert status == 204, status
    print("PASS temporary task removed", flush=True)
