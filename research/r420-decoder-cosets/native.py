# Apache-2.0; cxnmai with substantial OpenAI assistance.
"""Read exported primitive records; exact copy-aware bounds in both directions."""
import hashlib
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path
from model import ROOT

EXPORTER = ROOT/'research/e8-bit-carrier-skeleton/code/bit/export_records.py'


def audit(word, out):
    subprocess.run([sys.executable, '-B', str(EXPORTER), str(word), str(out)],
                   check=True, capture_output=True)
    records = list(struct.iter_unpack('<6i', (out/'249-records.bin').read_bytes()))
    kinds = Counter(r[0] for r in records)
    assert kinds[2] == kinds[3] == 9
    bounds = []
    for reverse in (False, True):
        norm, peak, opened = [1]*661, 1, None
        for op, dst, src, coef, frame, rank in (reversed(records) if reverse else records):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5-op
            if op == 1:
                assert dst != 660 and (src != 660 or opened is not None)
                norm[dst] += abs(coef)*norm[src]
                peak = max(peak, norm[dst])
            elif op == 2:
                assert opened is None and src == 660
                norm[660], opened = norm[dst], dst
            else:
                assert op == 3 and opened == dst and src == 660
                norm[660], opened = 0, None
        assert opened is None
        bounds.append(peak)
    # The stock columns_k.cpp finite local envelope (not a global invoice).
    payload = 64*bounds[0]**3*bounds[1]**2
    assert payload < 2**104
    return dict(records=len(records), additions=kinds[1], copies=kinds[2],
                erasures=kinds[3], moves=kinds[0], bounds=bounds,
                payload_upper=str(payload), payload_bits=payload.bit_length(),
                rank_histogram=[list(item) for item in sorted(Counter(
                    r[4] if r[0] == 0 else r[5]
                    for r in records if r[0] in (0, 2)).items())],
                exporter_sha256=hashlib.sha256(EXPORTER.read_bytes()).hexdigest())
