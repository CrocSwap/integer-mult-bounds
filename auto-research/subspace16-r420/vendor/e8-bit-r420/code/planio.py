# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Plan loader for gen_l3.py (load_plan of discovery/planL3.py, without the CP-SAT import)."""
import json


def load_plan(path):
    d = json.load(open(path))
    return dict(ext={(q, tuple(H)): e for q, H, e in d["ext"]}, partner={t: x for t, x in d["partner"]},
                kline={t: l for t, l in d["kline"]}, rcv={tuple(c): t for c, t in d["rcv"]},
                qhost={t: x for t, x in d["qhost"]})
