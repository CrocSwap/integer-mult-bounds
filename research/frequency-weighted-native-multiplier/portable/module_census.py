"""Read code-body lengths and expanded local declarations from the guest binary."""

import json
from hashlib import sha256
from pathlib import Path


class Reader:
    def __init__(self, raw):
        self.raw = raw
        self.i = 0

    def byte(self):
        self.i += 1
        return self.raw[self.i - 1]

    def uint(self):
        value = shift = 0
        while True:
            b = self.byte()
            value |= (b & 127) << shift
            if b < 128:
                return value
            shift += 7
            assert shift < 35

    def take(self, n):
        self.i += n
        assert self.i <= len(self.raw)
        return Reader(self.raw[self.i - n : self.i])


def catalogue(raw):
    rd = Reader(raw)
    assert bytes(rd.take(8).raw) == b"\x00asm\x01\x00\x00\x00"
    maximum_local = maximum_body = maximum_params = maximum_results = functions = 0
    while rd.i < len(rd.raw):
        kind = rd.byte()
        body = rd.take(rd.uint())
        if kind == 1:
            for _ in range(body.uint()):
                assert body.byte() == 0x60
                p = body.uint()
                body.take(p)
                r = body.uint()
                body.take(r)
                maximum_params = max(maximum_params, p)
                maximum_results = max(maximum_results, r)
            assert body.i == len(body.raw)
        if kind == 10:
            functions = body.uint()
            for _ in range(functions):
                size = body.uint()
                code = body.take(size)
                loc = 0
                for _ in range(code.uint()):
                    loc += code.uint()
                    typ = code.byte()
                    assert typ in {0x7F, 0x7E, 0x7D, 0x7C, 0x7B, 0x70, 0x6F}
                maximum_local = max(maximum_local, loc)
                maximum_body = max(maximum_body, size)
            assert body.i == len(body.raw)
    return {
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
        "functions": functions,
        "max_locals": maximum_local,
        "max_body_bytes": maximum_body,
        "max_params": maximum_params,
        "max_results": maximum_results,
    }


if __name__ == "__main__":
    print(
        json.dumps(
            catalogue((Path(__file__).parent / "python-3.12.0.wasm").read_bytes()),
            indent=2,
        )
    )
