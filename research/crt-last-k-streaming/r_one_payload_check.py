"""Independent follow-up control: true one-bit payloads, not unit-cost tags."""
import hashlib
import json
from pathlib import Path
import sys
import types


def main():
    path = Path(sys.argv[1])
    data = path.read_bytes()
    expected = "623bde19c1b0ad08b9a0dcfb54c1cd849e5b4a3e697dd385541d578ad7bc6ec2"
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("reviewed primary source changed")
    module = types.ModuleType("_independently_reviewed_tail_payload")
    module.__file__ = str(path)
    exec(compile(data, str(path), "exec"), module.__dict__)
    cases = columns = 0
    for length in range(1, 4):
        for suffix in range(length):
            for target in range(length - suffix):
                dependencies = [k for k in range(length - suffix) if k != target]
                for table in range(1 << (1 << len(dependencies))):
                    def control(word):
                        key = 0
                        for k in dependencies:
                            key = 2 * key + ((word >> (length - 1 - k)) & 1)
                        return (table >> key) & 1

                    for pattern in range(1 << (1 << length)):
                        payload = [(pattern >> k) & 1 for k in range(1 << length)]
                        actual, invoice = module.lower_tail(
                            payload, length, suffix, 1, target, control)
                        if actual != module.direct_switch(payload, length, target, control):
                            raise ValueError("R=1 payload endpoint mismatch")
                        if invoice["payload_cell_head_steps"] != 13 * (1 << length):
                            raise ValueError("R=1 payload tariff mismatch")
                        cases += 1
                        columns += len(payload)
    print(json.dumps({"status": "PASS_R_ONE_PAYLOAD_CONTROL",
                      "case_count": cases, "record_columns": columns,
                      "lengths": [1, 2, 3], "record_bits": 1,
                      "primary_sha256": expected,
                      "scope": "every binary payload pattern and permitted Boolean control on complete small rectangles; tags are not charged as one bit"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
