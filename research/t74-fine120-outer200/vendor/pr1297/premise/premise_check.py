#!/usr/bin/env python3
"""premise_check.py WORD : PR1049's independent checks on a NEW word -- literal location of all eight coded cells, the leaver
premise (no post-cell touch, no early-tail touch, FULL-cleanup restoration, not a centre/entering/low-ended register),
the exact all-column endpoint, and the frame/profile recount. verify_1049.py is PR1049's verify.py, unchanged; its two
coded-cell inputs are copied byte-for-byte (sha256-pinned inside it)."""
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_1049 as V
w = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
cells = V.read_pinned('CODED-CELLS-k8.json'); tri = V.read_pinned('TRI-LEAVER-k8.json')
cells = cells['cells'] if isinstance(cells, dict) and 'cells' in cells else cells
found, rep = V.audit_word(w, cells, V.cell_targets(cells, tri))
print(json.dumps(dict(status='PASS_LEAVER_PREMISE', cells=len(found), leavers=len(rep['leavers']),
                      paid_profile=rep['paid_profile'])))
