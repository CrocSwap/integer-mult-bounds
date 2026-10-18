#!/usr/bin/env python3
"""Apply the literal57-gate joint prefix to either complete eight-cold provider.

Derived from Dominik Scholz's PR571 compose_prefix.py, commit
b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3. Exact source hashes are in
data/JOINT-PREFIX.json. The plain variant keeps each retained event's own frame,
instead of copying width-seven-only frame expansions. OpenAI Codex assistance;
Apache-2.0. No optimization, external replay directory or network is required.
"""
import argparse,copy,gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path

def main():
    if not __debug__:raise RuntimeError('Assertions required')
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('input','recipe','gk-dir','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--variant',choices=('eightcold','width7'),required=True)
    args=parser.parse_args();assert not args.out.exists()
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    recipe=json.loads(args.recipe.read_bytes());pin=recipe['variants'][args.variant]
    raw=gzip.decompress(args.input.read_bytes());assert hashlib.sha256(raw).hexdigest()==pin['input_content_sha256']
    original=json.loads(raw);word=copy.deepcopy(original)
    sys.path.insert(0,str(args.gk_dir.resolve()));import gk_word as g,gk_common as co
    g.V=co.V=112;g.DATA=co.DATA=7168
    oldn,newn=recipe['old_prefix_length'],recipe['new_prefix_length'];assert(oldn,newn)==(69,57)
    assert [event[:-1]for event in word['A'][:oldn]]==recipe['old_scalar_prefix']
    events={tuple(e[:-1]):e for e in word['A'][:oldn]};assert len(events)==oldn
    prefix=[copy.deepcopy(events[tuple(e)])for e in recipe['new_scalar_prefix']]
    assert len(prefix)==len({tuple(e[:-1])for e in prefix})==newn
    word['A']=prefix+word['A'][oldn:]
    for key,frame in recipe['removed_start_frames'].items():
        assert word['start_extra'][key]==frame
        del word['start_extra'][key]
    assert set(recipe['removed_start_frames'])=={'523','525','599','601'}
    assert word['B']==original['B'] and word['A'][newn:]==original['A'][oldn:]
    word['cleanup']=[g.inverse(e,g.FULL)for e in reversed(word['A']+word['B'])if not 112<=e[1]<224]
    before,after=g.profile(original),g.profile(word);widths=co.widths_of(word);oldwidths=co.widths_of(original)
    delta={r:after[r]-before[r]for r in set(after)|set(before)if after[r]!=before[r]}
    assert delta=={1:-12,2:-16,3:16}
    assert dict(before)=={int(r):n for r,n in pin['profile_before'].items()}
    assert dict(after)=={int(r):n for r,n in pin['profile_after'].items()}
    changes={str(h):[x,y]for h,(x,y)in enumerate(zip(oldwidths,widths))if x!=y}
    assert changes==pin['changed_helper_widths']=={str(h):[8,9]for h in(299,301,375,377)}
    assert Counter(widths)==Counter({int(r):n for r,n in pin['width_inventory'].items()})
    responses=g.responses(word);assert all(not responses[int(r)-224]for r in word['start_extra'])
    word['report'].update(local_profile=dict(after),local_rank_mass=sum(r*n for r,n in after.items()),
        entrance_rank=sum(9-w for w in widths),entering_helpers=sum(w<9 for w in widths),width_inventory=dict(Counter(widths)))
    encoded=g.dump(word);encoded=encoded[:9]+b'\xff'+encoded[10:]
    assert hashlib.sha256(gzip.decompress(encoded)).hexdigest()==pin['output_content_sha256']
    args.out.mkdir(parents=True);target=args.out/'FULL-WORD.json.gz';target.write_bytes(encoded)
    result=dict(status='PASS_LITERAL_JOINT_PREFIX_EXACT_RESPONSE_AND_FRAME_PROFILE',variant=args.variant,
        source_content_sha256=pin['input_content_sha256'],word_content_sha256=pin['output_content_sha256'],
        word_sha256=sha(target),recipe_sha256=sha(args.recipe),constructor_sha256=sha(Path(__file__)),
        old_prefix=oldn,new_prefix=newn,retained_event_frames_unchanged=True,A_tail_unchanged=True,B_unchanged=True,
        removed_start_frames=recipe['removed_start_frames'],all_entering_response_columns_zero=True,
        profile_before=dict(before),profile_after=dict(after),profile_delta=delta,
        width_inventory=dict(Counter(widths)),changed_helper_widths=changes,
        scope='Exact construction and frame-chain profile only. Full scalar/native/wrapper/phase, '
              'omission, physical owner and invoice/moment checks remain separate.')
    (args.out/'CONSTRUCTION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],args.variant)

if __name__=='__main__':main()
