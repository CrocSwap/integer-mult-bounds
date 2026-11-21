"""Measure the same full stream across a forward route, mutation and return."""

import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
from tempfile import TemporaryFile

from stripe_route import striped_in_place


def check(predecessor, evidence, count):
    sys.path[:0] = [str(predecessor), str(evidence)]
    from measure_stock import BACK, BODY, BYTES, FORWARD, TapeCount, row_action, token_block
    from streaming_routes import erase, regular, right_route

    lows = [g for g in product(range(3), repeat=4) if regular(g, 2)]
    labels = 81
    extent = labels * BODY * BYTES
    size = len(lows) * extent
    masks = [bytes(x ^ (i + 1) for x in range(256)) for i in range(len(lows))]

    def route(bank, word):
        def run(source, target, stripe_width):
            right_route(source, target, 2, 1, 1, stripe_width, word)

        with TemporaryFile() as empty:
            tally = TapeCount(bank, empty, size)
            sys.setprofile(tally.observe)
            try:
                striped_in_place(bank, len(lows), extent, count, run)
            finally:
                sys.setprofile(None)
        assert not tally.pending and tally.live == size and bank.tell() == 0
        return {
            "bytes": dict(tally.bytes),
            "peak_live_file_bytes": tally.peak,
            "peak_auxiliary_file_bytes": tally.peak - size,
        }

    with TemporaryFile() as bank:
        for row in range(len(lows) * labels):
            bank.write(token_block(row))
        bank.seek(0)
        forward = route(bank, FORWARD)
        for i, low in enumerate(lows):
            source = lows.index(row_action(low, 3, True))
            for label in range(labels):
                buf = bank.read(BODY * BYTES)
                assert buf == token_block(source * labels + label)
                bank.seek(-len(buf), 1)
                bank.write(buf.translate(masks[i]))
        bank.seek(0)
        inverse = route(bank, BACK)
        digest = sha256()
        for i, low in enumerate(lows):
            mask = masks[lows.index(row_action(low, 3, False))]
            for label in range(labels):
                buf = bank.read(BODY * BYTES)
                assert buf == token_block(i * labels + label).translate(mask)
                digest.update(buf)
        assert not bank.read(1)
        erase(bank)
    assert digest.hexdigest() == "eec8c3f6683ccc78c8b41b661a476ffc16c3f627f28ec058b08344ee5436e287"
    return {
        "stripes": count,
        "input_bytes": size,
        "records": len(lows) * labels * BODY,
        "forward": forward,
        "inverse": inverse,
        "modified_output_sha256": digest.hexdigest(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("product_evidence", type=Path)
    parser.add_argument("stripes", type=int, choices=(1, 2, 9, 81))
    args = parser.parse_args()
    print(
        json.dumps(
            check(args.predecessor.resolve(), args.product_evidence.resolve(), args.stripes),
            sort_keys=True,
        )
    )
