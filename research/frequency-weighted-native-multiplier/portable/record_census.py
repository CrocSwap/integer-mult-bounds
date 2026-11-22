"""Read all directory records, check backward edges and size semantic dictionary keys."""

import json
import struct
import sys
from array import array
from collections import Counter
from pathlib import Path


def inspect(path):
    # One finite key has a self-delimiting type plus one reference for each atom.
    cap = 2**31 - 1
    size = array("I")
    counts = Counter()
    keys = largest = largest_key = edges = scalar = 0
    with path.open("rb") as f:
        assert f.read(8) == b"IMBDAG1\0"
        while raw := f.read(5):
            t, n = struct.unpack("<BI", raw)
            buf = f.read(n)
            assert len(buf) == n
            counts[t] += 1
            largest = max(largest, n)
            if t < 4:
                key_size = 5 + n
                if t == 2:
                    scalar = max(
                        scalar,
                        abs(int.from_bytes(buf, "little", signed=True)).bit_length(),
                    )
            else:
                refs = array("I")
                refs.frombytes(buf)
                if sys.byteorder != "little":
                    refs.byteswap()
                assert all(j < len(size) for j in refs)
                edges += len(refs)
                if t in (4, 5):
                    key_size = min(cap, 5 + sum(size[i] for i in refs))
                else:
                    key_size = cap
                if t in (7, 8, 9):
                    items = refs if t == 9 else refs[::2]
                    for i in items:
                        largest_key = max(largest_key, size[i])
                    keys += len(items)
            size.append(key_size)
    return {
        "bytes": path.stat().st_size,
        "records": len(size),
        "largest_record": largest,
        "edges": edges,
        "dictionary_set_keys": keys,
        "largest_key_bytes": largest_key,
        "largest_integer_bits": scalar,
        "tag_counts": counts,
    }


if __name__ == "__main__":
    print(json.dumps(inspect(Path(sys.argv[1])), indent=2))
