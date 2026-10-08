#!/usr/bin/env python3
"""Finite review of Abe's center suggestion and Michiel Kosters's candidate.

No end-to-end transfer/precision theorem is certified. Kosters's source is
referenced, not vendored; --kosters-root takes the pinned problem directory.
"""
import argparse
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from certify import Parameters, constraints, margins, network, require
from compact_control_layer import layer_exponents, parameters
from search_network import log_integer_bounds, log_ratio_bounds

KOSTERS_COMMIT = '2e0aa64ca09c87fc94f8575f59493f70cf929d71'


def saving(m, W, deficit):
    eta = Q(deficit, W*m)
    require(0 < eta < 1, 'nonpositive deficit')
    lo, hi = log_ratio_bounds(1/(1-eta), terms=8)
    l, u = log_integer_bounds(m)
    return lo/u, hi/l


def assembly(p):
    exponents = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    cs = constraints(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    cs['packed_overhead'] = p.lam-exponents['internal']
    cs['reserved_axes'] = p.lamp-exponents['preprocessing']
    gs = margins(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    require(all(v > 0 for v in cs.values()), 'nonpositive assembly constraint')
    require(min(gs.values()) > p.kappa, 'insufficient assembly margin')
    return dict(kappa=str(p.kappa), parameters={k:str(v) for k,v in vars(p).items()},
                minimum_margin=str(min(gs.values())), gap=str(min(gs.values())-p.kappa),
                constraint_count=len(cs), margin_count=len(gs))


def abe():
    # Same original side roles; only replace h+1 centers by h centers.
    def counts(h):
        n = network(h)
        W = 2*n['N']+n['I']*(n['v']*n['zc']+h)
        L = n['I']*h*h
        deficit = 2*n['N']-2*L
        return dict(h=h, m=n['m'], W=W, L=L, deficit=deficit, s=W*n['m']-deficit)
    bounds = {h:saving(**{k:counts(h)[k] for k in ('m','W','deficit')}) for h in range(21,200)}
    winner = max(bounds, key=lambda h:bounds[h][0])
    require(winner == 24, 'unexpected best old-family motif')
    lo, hi = bounds[winner]
    require(all(lo > u for h, (_,u) in bounds.items() if h != winner), 'ambiguous optimum')
    tail = Q(2, 3*network(200)['zc']*200**3-2)
    require(lo > tail, 'unbounded tail not excluded')
    # Drop point 0, keep the total. Twice the scatter coefficients are
    # sum_{j in S} g_j - total (0 absent), or 2*total - sum_{j notin S} g_j.
    masks = [sum(1<<i for i in t) for t in combinations(range(24),3)]
    all_points = (1<<24)-1
    for s in masks:
        for t in masks:
            actual = 2-((all_points ^ s)&t).bit_count() if s&1 else (s&t).bit_count()-1
            require(actual == (s&t).bit_count()-1, 'dyadic center identity')
    p = parameters()
    p = Parameters(**{**vars(p), 'sigma':1-Q(5307,10**13),
                      'lam':1-Q(5300,10**13), 'lamp':1-Q(5290,10**13),
                      'kappa':Q(21,2*10**11)})
    require(1-p.sigma < lo, 'unsupported complex saving')
    n = counts(24)
    require(2 <= n['s'] < n['m']**5, 'guard size hypothesis')
    return dict(attribution='Abe / @abe_asfaw, suggestion supplied by Douglas Colkitt',
                scope='Historical-family scalar identity, counts and assembly arithmetic; no new selected witness.',
                counts=n, saving_lower=str(lo), saving_upper=str(hi),
                saving_decimal=float(lo), finite_scan=[21,199], tail_h_min=200,
                tail_saving_upper=str(tail), central_coefficients_checked=len(masks)**2,
                dyadic_factor=True, assembly=assembly(p),
                ratio_to_old_witness=str(p.kappa/Q(83,10**12)))


def kosters(source):
    source = source.resolve()
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    require(commit == KOSTERS_COMMIT, 'unexpected Kosters source commit')
    tracked = subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],
                                     cwd=source,text=True)
    require(not tracked, 'modified source checkout')
    manifest = json.loads((source/'manifest.json').read_text())['sha256']
    restored = []
    raw_hashes = {}
    with tempfile.TemporaryDirectory(prefix='kosters-replay-') as tmp:
        dst = Path(tmp)/'problem'
        shutil.copytree(source,dst,ignore=shutil.ignore_patterns('__pycache__'))
        for name, digest in manifest.items():
            p = dst/name
            data = p.read_bytes()
            raw_hashes[name] = hashlib.sha256(data).hexdigest()
            if raw_hashes[name] != digest:
                data = data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
                require(hashlib.sha256(data).hexdigest() == digest, 'not a line-ending mismatch: '+name)
                p.write_bytes(data)
                restored.append(name)
        # No source/manifest logic changes: temporary bytes now match its own hashes.
        r = subprocess.run([sys.executable,str(dst/'verify.py')],capture_output=True,text=True)
        require(r.returncode == 0, 'Kosters verifier failed: '+r.stdout+r.stderr)
        require('Ran 5 tests' in r.stderr and '\nOK\n' in r.stderr, 'missing unit test result')
        require('PASS: exact certificate reproduces' in r.stdout, 'missing certificate result')
    data = json.loads((source/'certificate.json').read_text())
    p = Parameters(**{k:Q(v) for k,v in data['parameters'].items()})
    independent = {}
    for name in ('bit','complex'):
        d = data[name]
        m, W, deficit = d['h']**3, d['wires'], d['saving']
        lo, hi = saving(m,W,deficit)
        proposed = 1-(p.tau if name == 'bit' else p.sigma)
        require(0 < proposed < lo, 'Kosters unsupported '+name+' saving')
        independent[name] = dict(m=m,W=W,deficit=deficit,saving_lower=str(lo),saving_upper=str(hi))
    return dict(repository='https://github.com/michielkosters/mathematics_ai',commit=commit,
                source_directory='problems/integer-multiplication-109',source_sha256=raw_hashes,
                unmodified_verifier='fails on LF checkout: manifest expects CRLF for listed files',
                crlf_restored_in_temporary_copy=restored, temporary_verifier='passed', unit_tests=5,
                regenerated_certificate_matches=True, independent_savings=independent,
                assembly=assembly(p),scope='Finite candidate only; complete transfer/precision integration remains open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kosters-root',type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = {'abe':abe()}
    if args.kosters_root:
        result['kosters'] = kosters(args.kosters_root)
    text = json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text,end='')


if __name__ == '__main__':
    main()
