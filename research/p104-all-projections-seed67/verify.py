#!/usr/bin/env python3
"""Standalone, standard-library proof checker for the P104 finite width certificate.

No imports from generate.py, no integer-program solver and no trust in stored widths.
Each antichain and chain partition is checked directly against the *entire*
projected poset, then the 48 cube isometries transport the proof to 255 cases.
"""
import copy
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

PINNED_SUPPORT_SHA256 = 'adc1b55add8d480dbe1a6baf2c8322495a7176eca698bb6899cb698fce1de087'
PINNED_BASE = 'ba82555c64e1879e4b7decce28186f208fcb8262'
PINNED_HEAD = '9f7c0679d64bab954b7161d8586dc626a59b92ee'
PINNED_BLOB = '9a2cd574df48361579167e39aa6198f39059f70c'


def check(condition, label):
    if not condition:
        raise ValueError(label)


def automorphisms():
    # Independent permutation construction: x -> coordinate shuffle(x) XOR t.
    out = []
    for coords in itertools.permutations(range(3)):
        for t in range(8):
            out.append(tuple((sum(((v >> j) & 1) << coords[j] for j in range(3)) ^ t) for v in range(8)))
    check(len(set(out)) == 48, 'automorphism count')
    return out


def permute(mask, mapping):
    return sum(1 << mapping[j] for j in range(8) if mask & (1 << j))


def is_strict_subset(a, b):
    return a != b and (a & b) == a


def verify(data):
    check(data['schema'] == 'p104-projection-widths-v1', 'schema')
    check(data['upstream_base_commit'] == PINNED_BASE, 'base pin')
    check(data['audited_pr'] == 1125 and data['audited_head_commit'] == PINNED_HEAD, 'PR head pin')
    check(data['audited_blob'] == PINNED_BLOB and data['assignment_seed'] == 67, 'source pin / seed')
    supports = data['support_masks']
    digest = hashlib.sha256(json.dumps(supports, separators=(',', ':')).encode('ascii')).hexdigest()
    check(digest == PINNED_SUPPORT_SHA256, 'source data digest')
    check(len(supports) == len(set(supports)) == 104, 'source size')
    check(all(isinstance(s, int) and 0 < s < 256 for s in supports), 'mask range')
    check(Counter(s.bit_count() for s in supports) == {2:12,3:24,4:32,5:24,6:12},'source histogram')
    autos = automorphisms()
    family = set(supports)
    for p in autos:
        check({permute(s,p) for s in family} == family, 'source isometry closure')
    by_representative = {}
    all_orbit_members = set()
    for entry in data['orbits']:
        rep = entry['representative']
        members = entry['members']
        check(isinstance(rep,int) and 1 <= rep <= 255,'representative bounds')
        check(rep not in by_representative,'duplicate representative')
        check(members == sorted(set(members)),'members sorted unique')
        orbit = {permute(rep,p) for p in autos}
        check(orbit == set(members) and rep == min(orbit),'wrong orbit')
        check(not(all_orbit_members & orbit), 'overlapping orbits')
        all_orbit_members.update(orbit)
        poset = {s & rep for s in family if s & rep}
        check(bool(poset),'nonempty projection')
        chains = entry['chains']
        antichain = entry['antichain']
        check(isinstance(entry['width'],int) and entry['width'] >= 1,'width integer')
        check(len(chains) == len(antichain) == entry['width'],'witness widths')
        check(len(antichain) == len(set(antichain)) and set(antichain) <= poset,'antichain membership')
        for a,b in itertools.combinations(antichain,2):
            check(not is_strict_subset(a,b) and not is_strict_subset(b,a),'comparable antichain pair')
        seen=[]
        for chain in chains:
            check(isinstance(chain,list) and len(chain)>=1,'empty chain')
            check(all(x in poset for x in chain),'chain membership')
            check(all(is_strict_subset(a,b) for a,b in zip(chain,chain[1:])),'chain order')
            seen.extend(chain)
        check(len(seen)==len(set(seen)) and set(seen)==poset,'chain exact cover')
        by_representative[rep] = entry['width']
    check(all_orbit_members == set(range(1,256)), 'orbit coverage')
    check(len(by_representative)==21,'orbit count')
    # Transport exact antichain and chain-cover witnesses to every K by cube symmetry.
    histograms = {q:Counter() for q in range(8)}
    for K in range(1,256):
        rep = min(permute(K,p) for p in autos)
        width = by_representative[rep]
        histograms[8-K.bit_count()][width] += 1
    expected={
        0:{32:1},1:{26:8},2:{18:24,20:4},3:{10:56},
        4:{6:70},5:{3:56},6:{2:28},7:{1:8}
    }
    check({q:dict(h) for q,h in histograms.items()}==expected,'unexpected distribution')
    return {'orbits':len(by_representative),'subsets':len(all_orbit_members),
            'distribution': {str(q):dict(sorted(h.items())) for q,h in histograms.items()}}


def negative_controls(data):
    mutations = [
        ('support-bit',lambda x: x['support_masks'].__setitem__(0, x['support_masks'][0]^4)),
        ('false-width',lambda x: x['orbits'][0].__setitem__('width', 33)),
        ('delete-chain',lambda x: x['orbits'][0]['chains'].pop()),
        ('duplicate-chain-node',lambda x: x['orbits'][0]['chains'][0].append(x['orbits'][0]['chains'][0][-1])),
        ('duplicate-antichain',lambda x: x['orbits'][0]['antichain'].__setitem__(0,x['orbits'][0]['antichain'][1])),
        ('comparable-antichain',lambda x: x['orbits'][0]['antichain'].__setitem__(0,3)),
        ('reverse-chain',lambda x: x['orbits'][0]['chains'][0].reverse()),
        ('wrong-representative',lambda x:x['orbits'][0].__setitem__('representative',254)),
        ('delete-orbit',lambda x:x['orbits'].pop()),
        ('tampered-head',lambda x:x.__setitem__('audited_head_commit','0'*40)),
    ]
    for label, mutate in mutations:
        copy_of_data=copy.deepcopy(data)
        mutate(copy_of_data)
        try:
            verify(copy_of_data)
        except (ValueError, KeyError, TypeError, IndexError):
            pass
        else:
            raise AssertionError('negative control incorrectly accepted: '+label)
    return len(mutations)


if __name__=='__main__':
    data=json.loads(Path(__file__).with_name('CERTIFICATE.json').read_text(encoding='utf-8'))
    report=verify(data)
    count=negative_controls(data)
    print('PASS_P104_ALL_PROJECTIONS orbits=%d subsets=%d negative_controls=%d no_new_kappa'%(report['orbits'],report['subsets'],count))
    for q,distribution in sorted(report['distribution'].items()):
        print('q=%s widths=%s'%(q,distribution))
