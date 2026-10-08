#!/usr/bin/env python3
"""Run the full upstream frame audit on a new locally generated schedule.

Only the final equality to the original *headline numbers* is replaced: those
numbers describe the pinned input, and a new histogram should differ. Every
frame containment, rank, generic pivot, ledger, certificate and negative
control remains the same upstream check.
"""
import gzip
import json
from pathlib import Path
import sys
import audit_evidence

HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE/'vendor/independent/deferred-readout')]
import check_frames as cf
import deferred as dr


def main(path):
    before = audit_evidence.snapshot('frames', path)
    with gzip.open(path,'rt') as f:candidate=json.load(f)
    W,_=dr.load();origreport=cf.report
    dr.load=lambda h=23,*args,**kwargs:(W,candidate)
    def report(name,ok):
        if name.startswith('F. claims:'):
            origreport('F. candidate: original headline equality inapplicable; candidate ledgers and exact certificates checked above',True)
        else:origreport(name,ok)
    cf.report=report
    ok = cf.main(candidate['h'])
    if ok:
        audit_evidence.record('frames', path, before, dict(cf.OK))
    return ok


if __name__=='__main__':sys.exit(0 if main(Path(sys.argv[1])) else 1)
