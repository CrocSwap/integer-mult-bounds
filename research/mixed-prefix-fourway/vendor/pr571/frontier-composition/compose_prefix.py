#!/usr/bin/env python3
"""Compose a verified literal replacement A prefix with multicold B gates."""
import argparse,copy,gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('base','prefix','combined','gk-dir','out'):ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args()
    if not __debug__:raise ValueError('Assertions required')
    sys.path.insert(0,str(a.gk_dir.resolve()))
    import gk_word as g,gk_common as co
    g.V=co.V=112;g.DATA=co.DATA=7168
    read=lambda p:json.loads(gzip.decompress(p.read_bytes()))
    b,p,w=map(read,[a.base,a.prefix,a.combined]);before=g.profile(w)
    assert b['cut']==p['cut']==w['cut'] and b['A']==w['A']
    assert b['A'][69:]==p['A'][57:]
    assert all(w[k]==b[k]for k in b if k not in ('B','A','cleanup','start_extra','report'))
    changed=sorted(k for k in b['start_extra'].keys()|p['start_extra'].keys() if b['start_extra'].get(k)!=p['start_extra'].get(k))
    for k in changed:
        assert w['start_extra'].get(k)==b['start_extra'].get(k)
        if k in p['start_extra']:w['start_extra'][k]=copy.deepcopy(p['start_extra'][k])
        else:w['start_extra'].pop(k,None)
    w['A']=copy.deepcopy(p['A'])
    w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
    after=g.profile(w);widths=g.widths_of(w)
    a.out.mkdir(exist_ok=True)
    w['report'].update(local_profile={str(k):v for k,v in after.items()},entrance_rank=sum(9-x for x in widths),entering_helpers=sum(x<9 for x in widths),width_inventory=dict(Counter(widths)))
    encoded=g.dump(w);encoded=encoded[:9]+b'\xff'+encoded[10:]
    target=a.out/'FULL-WORD.json.gz'
    if target.exists():assert target.read_bytes()==encoded
    else:target.write_bytes(encoded)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    r=dict(status='PASS_LITERAL_PREFIX_MULTICOLD_COMPOSITION_FRAME_CHAINS',sources={str(x):sha(x)for x in[a.base,a.prefix,a.combined]},source_prefix_length=69,new_prefix_length=57,exact_unchanged_A_tail=True,exact_unchanged_cut=True,changed_start_keys=changed,profile_before=before,profile_after=after,widths=dict(Counter(widths)),widths_after=dict(Counter(widths)),word_sha256=sha(a.out/'FULL-WORD.json.gz'),scope='Literal A-prefix composition with only the upstream joint-basis entrance changes; all new multicold B gates retained and cleanup regenerated. Complete frame chains checked; native/phase/global admission pending.')
    (a.out/'CONSTRUCTION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in('profile_before','profile_after','widths')},indent=2))

if __name__=='__main__':main()
