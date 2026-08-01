"""FLAGSHIP - CSV to working API in one file.

The customer hands you an export at 4pm; the VP demo is tomorrow at 9am.
No infra, no approvals for new packages. Stdlib only: parse the CSV, serve
a queryable JSON API with a summary endpoint. Self-testing: spins up the
server on a random port, hits it with urllib, asserts the responses.
"""

import csv
import io
import json
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

RAW_EXPORT = """order_id,customer,region,status,amount
1001,Acme Corp,NORTH,shipped,1250.50
1002,Globex,south,PENDING,340.00
1003,Initech,North,shipped,99.99
1004,Umbrella,EAST,cancelled,780.25
1005,Acme Corp,north,pending,410.10
1006,Stark Industries,East,SHIPPED,2200.00
"""


def load_records(raw: str) -> list[dict]:
    records = []
    for row in csv.DictReader(io.StringIO(raw)):
        records.append({
            "order_id": int(row["order_id"]),
            "customer": row["customer"].strip(),
            "region": row["region"].strip().lower(),      # normalize the chaos
            "status": row["status"].strip().lower(),
            "amount": float(row["amount"]),
        })
    return records


def summarize(records: list[dict]) -> dict:
    by_status: dict[str, float] = {}
    for r in records:
        by_status[r["status"]] = round(by_status.get(r["status"], 0) + r["amount"], 2)
    return {
        "total_orders": len(records),
        "total_amount": round(sum(r["amount"] for r in records), 2),
        "by_status": by_status,
    }


class Api(BaseHTTPRequestHandler):
    records: list[dict] = []

    def do_GET(self):
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        if url.path == "/records":
            data = self.records
            if "status" in qs:
                data = [r for r in data if r["status"] == qs["status"][0]]
            if "region" in qs:
                data = [r for r in data if r["region"] == qs["region"][0]]
            self._json(200, data)
        elif url.path == "/summary":
            self._json(200, summarize(self.records))
        else:
            self._json(404, {"error": "not found"})

    def _json(self, code: int, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def get(base: str, path: str):
    with urllib.request.urlopen(base + path) as resp:
        return resp.status, json.loads(resp.read())


def main():
    Api.records = load_records(RAW_EXPORT)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Api)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    status, body = get(base, "/records")
    assert status == 200 and len(body) == 6

    status, body = get(base, "/records?status=shipped")
    assert len(body) == 3, "case-normalization must merge SHIPPED/shipped"
    assert {r["order_id"] for r in body} == {1001, 1003, 1006}

    status, body = get(base, "/records?region=north&status=pending")
    assert [r["order_id"] for r in body] == [1005]

    status, body = get(base, "/summary")
    assert body["total_orders"] == 6
    assert body["total_amount"] == 5080.84
    assert body["by_status"]["shipped"] == 3550.49

    try:
        get(base, "/nope")
        raise AssertionError("expected 404")
    except urllib.error.HTTPError as e:
        assert e.code == 404

    server.shutdown()
    print("csv-to-api: all assertions passed (5 endpoints checked)")


if __name__ == "__main__":
    main()
