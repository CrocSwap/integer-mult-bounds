"""Independent PR890 owner audit, with exact T37/480-helper parameter edits."""
import argparse
from pathlib import Path
from common import P,ROOT,read,dump,load,sha

def check(base,local,owners_path,out):
    source=ROOT/'research/complex-t21-owners/independent_check.py'
    text=source.read_text()
    edits=[('2 * 512','2 * 1024'),('prefix < 512','prefix < 1024'),
      ('charged_prefix_bits=512','charged_prefix_bits=1024'),
      ('{4: 80, 5: 32, 7: 54, 8: 122, 9: 216}','{4: 56, 5: 32, 7: 32, 8: 120, 9: 240}')]
    for before,after in edits:
        assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after)
    adapter=out.parent/'independent_owner_adapter.py';assert not adapter.exists();adapter.write_text(text)
    ck=load(adapter,'independent_seven_slot_owner_checker');ck.T=37;ck.R=480;ck.EXPECTED_IDLE={1:5424,48:11320}
    refs=[base/'split-centres/GLOBAL-TEMPLATE.json.gz',base/'work/complex-nine-native/DATA-PHASES.json',
          base/'split-centres/CANONICAL-WORD.json.gz',local/'CANONICAL-WORD.json.gz',
          local/'INDEPENDENT-LOCAL-REPLAY.json',owners_path]
    parent,phases,canonical,word,receipt,owners=map(read,refs)
    assert receipt['canonical_word_sha256']==sha(refs[3])
    assert receipt['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
    assert word['ports']==canonical['ports']
    assert [ck.basis(word['frames'][f])for f in word['center_frames']]==[ck.basis(canonical['frames'][f])for f in canonical['center_frames']]
    context=ck.make_context(parent,phases,word['ports'],word,receipt,owners)
    result=ck.check_roles(context,owners);result['controls_rejected']=ck.controls(context,owners)
    result.update(edits=edits,source_sha256=sha(source),adapter_sha256=sha(adapter),inputs={str(p):sha(p)for p in refs})
    claim=read(P/'CLAIM.json')
    for field in ('roles','calls','live','physical','rank_mass','deficit','prefix_bits','physical_row_coefficient'):
        assert result[field]==claim[field],field
    assert {str(r):n for r,n in result['profile'].items()}==claim['complex_profile']
    dump(out,result);return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('base','local','owners','out'):ap.add_argument('--'+k,type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve();assert not out.exists() and not out.is_relative_to(ROOT)
    out.parent.mkdir(parents=True,exist_ok=True)
    r=check(a.base,a.local,a.owners,out);print(r['status'],r['roles'],flush=True)
if __name__=='__main__':main()
