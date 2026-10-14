"""Independent call-indexed local recount and PR890 literal owner geometry audit.

The owner constructor and emitted controller are never imported. Both native
words are independently recounted, then selected by the frozen call dispatch.
Every modification to the retained geometric checker is explicit and hashed.
"""
import argparse, copy
from collections import Counter
from pathlib import Path
from common import P,ROOT,read,dump,load,sha

INVENTORIES={'demote3':{4:44,5:44,7:38,8:114,9:240},'demote4':{4:40,5:48,7:38,8:114,9:240}}

def check(base,providers,owners_path,out):
    source=ROOT/'research/complex-t21-owners/independent_check.py'
    text=source.read_text()
    edits=[('2 * 512','2 * 1024'),('prefix < 512','prefix < 1024'),
      ('charged_prefix_bits=512','charged_prefix_bits=1024'),
      ('Counter(widths) == {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}',
       'Counter(widths) in ({4:44,5:44,7:38,8:114,9:240},{4:40,5:48,7:38,8:114,9:240})'),
      ("width == c['widths'][helper]", "width == c['widths_by_call'][call][helper]"),
      ("Counter({rank: 9 * T * count for rank, count in c['paid'].items()})", "Counter(c['paid_total'])"),
      ("max(x['prefix_bits_upper'] for x in c['replay']['local'].values())", "c['localbits']"),
      ("local_profile=dict(sorted(c['paid'].items())), width_inventory=dict(sorted(Counter(c['widths']).items())),", "local_profiles=c['local_profiles'], width_inventories=c['inventories'], provider_call_counts=c['call_counts'],"),
      ("if context['callpos'][key] >= hi", "if context['callpos'][key] >= hi and context['widths_by_call'][key][z['helper']] == z['width']")]
    for before,after in edits:
        assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after)
    adapter=out.parent/'mixed_independent_owner_adapter.py';assert not adapter.exists();adapter.write_text(text)
    ck=load(adapter,'independent_mixed_owner_checker');ck.T=37;ck.R=480;ck.EXPECTED_IDLE={1:2,48:11374}
    refs=[base/'split-centres/GLOBAL-TEMPLATE.json.gz',base/'work/complex-nine-native/DATA-PHASES.json',
          base/'split-centres/CANONICAL-WORD.json.gz',owners_path,P/'data/MIX.json',P/'data/ORDER.json']
    parent,phases,canonical,owners,mix,order=map(read,refs)
    assert [[s,r]for pid,s,r in mix]==order
    assert len({(s,r)for pid,s,r in mix})==333
    counts=Counter(pid for pid,s,r in mix);assert counts=={'demote3':125,'demote4':208}
    assert set(providers)==set(counts)
    widths={};paid={};words={};receipts={};bits=[]
    for pid,directory in sorted(providers.items()):
        paths=[directory/'CANONICAL-WORD.json.gz',directory/'INDEPENDENT-LOCAL-REPLAY.json'];refs+=paths
        word,receipt=map(read,paths);words[pid]=word;receipts[pid]=receipt
        assert receipt['canonical_word_sha256']==sha(paths[0])
        assert receipt['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
        assert word['ports']==canonical['ports']
        assert [ck.basis(word['frames'][f])for f in word['center_frames']]==[ck.basis(canonical['frames'][f])for f in canonical['center_frames']]
        widths[pid],paid[pid]=ck.local_inventory(word,receipt)
        assert Counter(widths[pid])==INVENTORIES[pid]
        bits.extend(v['prefix_bits_upper']for v in receipt['local'].values())
    context=ck.make_context(parent,phases,words['demote3']['ports'],words['demote3'],receipts['demote3'],owners)
    assert [list(k)for k in context['order']]==order
    total=Counter()
    for pid,s,r in mix:total.update(paid[pid])
    context.update(widths_by_call={(s,r):widths[pid]for pid,s,r in mix},paid_total=total,localbits=max(bits),
      local_profiles={pid:dict(v)for pid,v in paid.items()},inventories=INVENTORIES,call_counts=dict(counts))
    result=ck.check_roles(context,owners);result['controls_rejected']=ck.controls(context,owners)
    # Substituting the other admitted word changes four specific whole-helper
    # widths. Keep the geometry fixed and require rejection at that predicate.
    for pid in sorted(providers):
        call=next((s,r)for p,s,r in mix if p==pid);bad=copy.copy(context)
        bad['widths_by_call']=dict(context['widths_by_call'])
        bad['widths_by_call'][call]=widths['demote4'if pid=='demote3'else'demote3']
        try:ck.check_roles(bad,owners)
        except ValueError as e:
            assert str(e)=='whole-helper residual width'
            result['controls_rejected'].append(dict(name='wrong_provider_'+pid,reason=str(e)))
        else:raise AssertionError('wrong provider accepted')
    result.update(edits=edits,source_sha256=sha(source),adapter_sha256=sha(adapter),inputs={str(p):sha(p)for p in refs})
    claim=read(P/'CLAIM.json')
    for field in ('roles','calls','live','physical','rank_mass','deficit','prefix_bits','physical_row_coefficient'):
        assert result[field]==claim[field],field
    assert {str(r):n for r,n in result['profile'].items()}==claim['complex_profile']
    dump(out,result);return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('base','local3','local4','owners','out'):ap.add_argument('--'+k,type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve();assert not out.exists() and not out.is_relative_to(ROOT)
    out.parent.mkdir(parents=True,exist_ok=True)
    r=check(a.base,{'demote3':a.local3,'demote4':a.local4},a.owners,out);print(r['status'],r['roles'],flush=True)
if __name__=='__main__':main()
