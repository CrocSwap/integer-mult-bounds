#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the candidate with authenticated predecessor engines in private directories."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sources import need, parent_archive

STAGES = {"early": "verify_early.py", "native": "verify_native.py", "caller": "verify.py"}
REPLAY = ("verify_early.py", "verify_native.py", "verify.py", "price.py", "adapt.py",
          "derive_grid.py", "support.py")
INPUTS = ("INPUTS.json", "REFERENCE.json", "WITNESS.json", "WORD.json.gz",
          "EARLY-RESULT.json", "NATIVE-RESULT.json", "RESULT.json")


def adapt(work):
    def patch(file, old, new, count=1):
        path = work / file
        raw = path.read_text()
        need(raw.count(old) == count, "Exact adapter anchor in " + file + ": " + old)
        path.write_text(raw.replace(old, new))

    native = STAGES["native"]
    patch(native, "(64, 47, 61)", "(70, 49, 67)", 2)
    patch(native, "+1\n        base=G.module", "+2\n        base=G.module")
    patch(native, "oldN['lifetimes']+2==64 and N['owned_peak']==47", "oldN['lifetimes']+4==70 and N['owned_peak']==49")
    patch(native, "old['owned_fields']+2==61", "old['owned_fields']+4==67")
    patch(native, "['lifetimes']==64,'Fresh exact owned census", "['lifetimes']==70,'Fresh exact owned census")
    patch(native, "=={4:1,5:1,9:-1} and delta(N['paid'],oldN['paid'])=={3:1,5:1,8:-1}",
          "=={1:1,4:1,5:1,8:-1} and delta(N['paid'],oldN['paid'])=={1:2}")
    patch(native, "len(old['program'])+40 and new['public']==old['public']+1==1498",
          "len(old['program'])+95 and new['public']==old['public']+2==1501")
    patch(native, "hit=read(HERE/'WITNESS.json');f=hit['frame'];u=source['initial'][hit['pivot']];v=source['final'][hit['pivot']];a=hit['path']['old'];b=hit['path']['new']\n"
                  "    needed=changed|{(u,f),(f,v),(a,f),(f,b),(a,b),(u,v)}",
          "needed=changed|{(3,1091),(1091,127),(3,245),(245,127),(3,127)}")
    patch(native, "hit=read(HERE/'WITNESS.json');paths=read(HERE/'PATHS.json');new=construct(old,hit,paths)",
          "hit=read(HERE/'WITNESS.json');new=construct(old,hit)")
    patch(native, "from certificate import controls as temporal_controls, observe, check\n"
                  "        snapshots=observe(old,hit);timed_certificate=check(hit,snapshots)\n"
                  "        controls=temporal_controls(old,hit,paths,snapshots)",
          "from certificate import controls as temporal_controls, vectors, check\n"
          "        snapshots=vectors(old,hit);timed_certificate=check(old,hit,snapshots)\n"
          "        controls=temporal_controls(old,hit,snapshots)")
    patch(native, "hit['pivot']", "hit['pivots'][0]", 3)
    patch(native, "hit['frame']", "hit['frames'][0]", 2)
    patch(native, "PASS_TEMPORAL_CHART306_NATIVE", "PASS_TWO_CUT_FUNDED_NATIVE")
    patch(native, "source_head=read(HERE/'INPUTS.json')", "source_head=read(HERE/'REFERENCE.json')")
    patch("verify.py", "PASS_TEMPORAL_CHART306_CONTINUATION", "PASS_TWO_CUT_FUNDED_CALLER")
    patch("adapt.py", "(64, 47, 61)", "(70, 49, 67)")
    patch("price.py", "Entire reconstructed current #7155 invoice", "Entire reconstructed #7161 invoice")
    patch("adapt.py", 'crossing_probe_rejected,"scope":"Reuse exact same native word all-column adjoint;',
          'crossing_probe_rejected,"scope":"Fresh complete changed-native arbitrary-input adjoint;')

    early = STAGES["early"]
    patch(early, "from construct import construct", "from construct import construct\nfrom packing_reference import packing\nfrom fractions import Fraction as Q")
    patch(early, "construct(old,read(HERE/'WITNESS.json'),read(HERE/'PATHS.json'))", "construct(old,read(HERE/'WITNESS.json'))")
    patch(early, "before['lifetimes']+2 and new['owned_fields']==old['owned_fields']+2",
          "before['lifetimes']+4 and new['owned_fields']==old['owned_fields']+4")
    patch(early, "        return normalized(dict(status=",
          "        ceiling=packing(invoice,after,G.module('two_cut_packing',vendor/'interval_gate.py'),Q(gate['claim']))\n"
          "        return normalized(dict(packing=ceiling,status=")
    patch(early, "    r=run();need(r==read(HERE/'EARLY-RESULT.json'),'Every frozen early receipt field');print(r['status'],r['price']['claim_decimal'],flush=True)",
          "    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args()\n"
          "    r=run()\n"
          "    if args.out:\n"
          "        with args.out.open('x') as out:json.dump(r,out,sort_keys=True,indent=2);out.write('\\n')\n"
          "    else:need(r==read(HERE/'EARLY-RESULT.json'),'Every frozen early receipt field')\n"
          "    print(r['status'],r['price']['claim_decimal'],flush=True)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=STAGES)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    need(__debug__, "Assertions are proof obligations")
    output = args.out.resolve() if args.out else None
    need(output is None or not output.exists(), "Keep prior receipts immutable")
    with parent_archive() as parent, TemporaryDirectory(prefix="p104-two-cut-stage-") as root:
        work = Path(root)
        for name in REPLAY:
            shutil.copyfile(parent / name, work / name)
        for name in INPUTS:
            if (HERE / name).is_file():
                shutil.copyfile(HERE / name, work / name)
        for name in ("construct.py", "certificate.py", "packing_reference.py"):
            shutil.copyfile(HERE / name, work / name)
        shutil.copyfile(HERE / "sources.py", work / "source.py")
        shutil.copytree(HERE / "reference", work / "reference")
        (work / "PARENT-DIRECTORY.txt").write_text(str(parent) + "\n")
        adapt(work)
        argv = [sys.executable, "-I", "-B", str(work / STAGES[args.stage])]
        if output is not None:
            argv.extend(("--out", str(output)))
        subprocess.run(argv, cwd=work, check=True)


if __name__ == "__main__":
    main()
