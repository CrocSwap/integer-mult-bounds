#!/usr/bin/env python3
"""Replay the two-half-shear allowance alternative to the gate-minimum handoff.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Lead construction; worker A primary and source-bound integration; worker D
independent algebra and unchanged integer-dyadic replay implementation.
"""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from types import ModuleType
import argparse
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HISTORICAL_RECEIPT = '56fd699bb50d539b2e2143681839d2bb82cd1d9e9bc9450e96c2f3b5f52165fe'


def load(path, name):
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


v = load(HERE/'verify.py', '_allowance_primary')


def weighted(a, b, pivot, frame):
    """The one prescribed pair-specific two-half-shear completion, not a search."""
    v.need(pivot == 596, 'Exact alternative pivot')
    aa, bb = dict(a), dict(b)
    for destination, source in ((594, 592), (594, 593)):
        aa[source] = aa.get(source, Q(0)) - aa.get(destination, Q(0))/2
        bb[destination] = bb.get(destination, Q(0)) + bb.get(source, Q(0))/2
    v.need({k:x for k,x in aa.items() if x} == {594:Q(5,8),596:Q(3,8)}, 'Exact row cancellations')
    v.need(bb == b, 'Exact column cancellation')
    events = v.compiler.compile_basis(aa, bb, pivot, frame)
    events += [['ADD',594,593,'-1/2',frame],['ADD',594,592,'-1/2',frame]]
    v.need(all(abs(Q(e[-2]))+1 < 2**16 for e in events+v.compiler.inverse(events)), 'Both-way scalar cap')
    return events


def verify():
    sources = v.source_checks()
    historical = (HERE/'GATE-MINIMUM-RESULT.json').read_bytes()
    v.need(v.digest(historical) == HISTORICAL_RECEIPT, 'Immutable gate-minimum receipt')
    old, current = json.loads(historical), json.loads((HERE/'RESULT.json').read_bytes())
    old.pop('package_sha256'); current.pop('package_sha256')
    v.need(old == current, 'Gate-minimum mathematical receipt unchanged')
    where = ROOT/'research/p104-coupled-helper-bases'
    local = load(where/'local.py', 'local')
    construct = load(where/'construct.py', '_allowance_construct')
    engine = load(HERE/'weighted_review.py', '_allowance_independent_review')
    word = json.loads(gzip.decompress((where/'inputs/pr5580-WORD.json.gz').read_bytes()))
    step = {'kind':'coupled_handoff','cut':13762,'frame':1053,'group':[3,127],
            'pivot':596,'v':v.pairs(v.V),'u':v.pairs(v.U),
            'source_functional':v.pairs(v.V),'output_direction':v.pairs(v.B)}
    source, cut = weighted(v.V,v.B,596,3), weighted(v.V,v.U,596,1053)
    v.boundary_check(v.V,v.B,596,source); v.boundary_check(v.V,v.U,596,cut)
    v.need((len(source),len(cut),v.compiler.allowance(source),v.compiler.allowance(cut)) == (7,6,72,64), 'Alternative boundary costs')
    construct.basis = weighted
    candidate = construct.handoff(word,step)
    result = local.replay(candidate)
    v.need(len(candidate['program']) == 25166 and result['real_scalar_allowance'] == 217700, 'Alternative whole-word costs')
    v.need(result['paid'] == v.PAID and result['helpers'] == {9:423,4:84,5:6,8:15}, 'Retained paid/productive inventory')
    audit = engine.audit(word,candidate)
    indices = list(range(7))+list(range(7+13762+1,7+13762+1+12))+list(range(len(candidate['program'])-7,len(candidate['program'])))
    v.need(len(indices) == 26, 'Every inserted event identified')
    controls = 0
    for index in indices:
        mutant = deepcopy(candidate); del mutant['program'][index]
        controls += v.rejection(lambda:local.replay(mutant))
    for coefficient, frame in (('-5/8',1053),(str(2**16),3)):
        mutant = deepcopy(candidate); mutant['program'][0][-2:] = [coefficient,frame]
        controls += v.rejection(lambda:local.replay(mutant))
    v.need(controls == 28, 'Alternative omission/chart/growth controls')
    # The separate alternative wrapper first accepts this exact candidate;
    # its semantic controls reject before fixture-count checks can mask errors.
    independent_controls = engine.controls(word,candidate)
    v.need(len(independent_controls) == 10, 'Alternative independent controls')
    v.need(all('inventory' not in case['rejection'] for case in independent_controls),
           'Semantic controls must fail before fixture inventory')
    return candidate, {'source_events':source,'cut_events':cut,'inserted_events':26,'inserted_allowance':272,
           'primary':result,'independent':audit,'word_rejections':controls,
           'independent_rejections':independent_controls,'word_sha256':v.digest(v.canonical(candidate)),
           'historical_receipt_sha256':HISTORICAL_RECEIPT,'input_sha256':sources,
           'package_sha256':{name:v.digest((HERE/name).read_bytes()) for name in
             ('alternative.py','ALTERNATIVE-PROOF.md','weighted_review.py','WEIGHTED-REVIEW.md','compiler.py','verify.py','independent.py','README.md','TASK.json','VERIFY.json')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--emit-word', type=Path)
    args = parser.parse_args()
    word, result = verify()
    if args.emit_word:
        v.need(not args.emit_word.resolve().is_relative_to(ROOT), 'Emit outside checkout')
        args.emit_word.write_bytes(v.canonical(word))
    if args.write:
        (HERE/'ALTERNATIVE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        v.need(json.loads((HERE/'ALTERNATIVE.json').read_bytes()) == json.loads(v.canonical(result)), 'Exact alternative receipt')
    print('PASS_P104_ALLOWANCE_ALTERNATIVE inserted_events=26 inserted_allowance=272 word_controls=28')


if __name__ == '__main__':
    main()
