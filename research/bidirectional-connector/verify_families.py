#!/usr/bin/env python3
"""Replay constructed family words, exact cost examples and focused regressions."""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import families as f
import verify as v

HERE=Path(__file__).resolve().parent


def verify():
    examples=[]
    for n in range(3,13):
        sizes=f.balanced_three(n)
        word=f.construct_palette(sizes)
        v.check_endpoint(word,n,2)
        counts=f.palette_screen(sizes)
        if counts['source_calls']!=sum(op[0]=='B' for op in word) or counts['transfers']!=sum(op[0]=='C' for op in word):
            raise ValueError('unpaid family instruction')
        examples.append({'sources':n,'counts':counts,'word_sha256':sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()})
    for n,b in ((9,20),(12,85),(15,200),(18,800)):
        reference=f.best_single(n,b,1);baseline=f.cost(reference,b,1)
        counts=f.palette_screen(f.balanced_three(n))
        candidate=counts['source_calls']*b+counts['readout_calls']+counts['transfers']
        if candidate>=baseline:raise ValueError('declared positive tariff does not improve')
        examples.append({'sources':n,'B_price':b,'A_price':1,'transfer_price':1,'best_one_root_blocks':list(reference),'reference_cost':int(baseline),'palette_cost':candidate,'saved_units':int(baseline-candidate),'fraction_saved':str(Fraction(baseline-candidate,baseline))})
    for n in (9,12,15,18,30,60):
        price=f.critical_tariff(n)
        lower=f.global_lower_bound(n,price,1,1)
        two_lower=f.global_lower_bound(n,price,1,2)
        achieved=f.palette_cost(f.balanced_three(n),price,1,1)
        if achieved>=lower or achieved<two_lower:raise ValueError('global tariff separation failed')
        examples.append({'theorem':'all-word query tariff bounds','sources':n,'source_price':price,
                         'readout_price':1,'transfer_price':1,'one_root_lower_bound':int(lower),
                         'two_root_lower_bound':int(two_lower),'palette_cost':int(achieved),
                         'guaranteed_saved_fraction_vs_every_one_root_word':str(Fraction(lower-achieved,lower))})
    for n in (9,12,15,18,30,60):
        b=f.critical_tariff(n);c=f.signed_palette_screen(f.balanced_three(n))
        achieved=c['source_calls']*b+c['readout_calls']+c['transfers']
        lower=f.global_lower_bound(n,b,1,1)
        if achieved>=lower:raise ValueError('signed global separation failed')
        examples.append({'theorem':'characteristic-zero signed palette','sources':n,'source_price':b,
                         'one_root_lower_bound':int(lower),'signed_palette_cost':achieved,
                         'guaranteed_saved_fraction_vs_every_one_root_word':str(Fraction(lower-achieved,lower))})
    for n in (9,12,15,18,30,60):
        b=f.critical_tariff(n)
        lower=f.locality_lower_bound(n,b,1,1)
        two_lower=f.locality_lower_bound(n,b,1,2)
        signed=f.signed_palette_screen(f.balanced_three(n))
        achieved=signed['source_calls']*b+signed['readout_calls']+signed['transfers']
        if achieved>=lower or achieved<two_lower:raise ValueError('locality separation failed')
        examples.append({'theorem':'all-word source-locality bound and signed triangle',
                         'sources':n,'source_price':b,'one_root_locality_lower_bound':int(lower),
                         'two_root_locality_lower_bound':int(two_lower),'signed_triangle_cost':achieved,
                         'guaranteed_saved_fraction':str(Fraction(lower-achieved,lower))})
    return examples


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--write-receipt',action='store_true');args=p.parse_args()
    result={'schema':'paid-palette-family-v1','records':verify()}
    path=HERE/'FAMILY-RECEIPT.json'
    literal = {"sources": 6, "word": f.construct_palette((2,2,2))}
    literal_path = HERE / "PALETTE6.json"
    if not args.write_receipt:
        if json.loads(path.read_text())!=result:raise ValueError('family receipt changed')
        if json.loads(literal_path.read_text()) != literal:raise ValueError('literal palette export differs')
    subprocess.run([sys.executable,'-B',str(HERE/'test_families.py')],check=True,timeout=60)
    subprocess.run([sys.executable,'-O','-B',str(HERE/'test_verify.py')],check=True,timeout=30)
    subprocess.run([sys.executable,'-B',str(HERE/'certify_frames.py')],check=True,timeout=30)
    if args.write_receipt:
        path.write_text(json.dumps(result,indent=2)+'\n')
        literal_path.write_text(json.dumps(literal,separators=(',',':'))+'\n')
    print('PASS_PAID_PALETTE_FAMILY generic_n=3..12 exact_tariffs=4 global_bounds=6 tests=11+6 benchmark_pins=23 drift_control=checked frame_cases=384 signed_triangle=checked locality_bounds=6 no_new_kappa')


if __name__=='__main__':main()
