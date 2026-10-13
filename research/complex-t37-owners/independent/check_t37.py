"""Independent T37 whole-role/window/chart check with explicit payload adaptation.

Preserves the PR890 independent checker except three payload constants and
the replica range admitted by the enlarged prefix reserve. Reads three named
original T8 reference inputs from the provided cold replay and fresh U8 data.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must remain enabled; do not use Python -O')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PACKAGE=HERE.parent
SOURCE=ROOT/'research/complex-t21-owners/independent_check.py'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--local-replay',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--baseline-base',type=Path,required=True,
                    help='Fresh replay base containing split-centres and work/complex-nine-native')
    args=ap.parse_args()
    args.out=args.out.resolve()
    assert not args.out.exists() and not args.out.is_relative_to(ROOT),'New output outside checkout required'
    text=SOURCE.read_text()
    changes=[('2 * 512','2 * 1024',1),('prefix < 512','prefix < 1024',1),
             ('charged_prefix_bits=512','charged_prefix_bits=1024',1),
             ('1 <= T <= 22','1 <= T <= 50',1)]
    for old,new,count in changes:
        assert text.count(old)==count,(old,text.count(old))
        text=text.replace(old,new)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    adapter=args.out.parent/'independent_check_1024.py'
    assert not adapter.exists(),'Independent adapter output must be new'
    adapter.write_text(text)
    spec=importlib.util.spec_from_file_location('independent_t37',adapter)
    ck=importlib.util.module_from_spec(spec);spec.loader.exec_module(ck)
    ck.T=37;ck.EXPECTED_IDLE={48:11086,1:6}
    # No constructor, owner emitter, or root exploratory search is imported.
    refs=[args.baseline_base/'split-centres/GLOBAL-TEMPLATE.json.gz',
          args.baseline_base/'split-centres/CANONICAL-WORD.json.gz',
          args.baseline_base/'work/complex-nine-native/DATA-PHASES.json']
    parent,canonical,phases=map(ck.read,refs)
    word,replay=ck.read(args.word),ck.read(args.local_replay)
    assert replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
    assert replay['canonical_word_sha256']==sha(args.word)
    assert set(replay['local'])=={'forward','backward'}
    assert word['ports']==canonical['ports']
    assert len(word['center_frames'])==len(canonical['center_frames'])==8
    assert [ck.basis(word['frames'][f])for f in word['center_frames']]==[ck.basis(canonical['frames'][f])for f in canonical['center_frames']]
    owner_path=PACKAGE/'OWNERS.json.gz'
    roles=ck.read(owner_path)
    context=ck.make_context(parent,phases,canonical['ports'],word,replay,roles)
    receipt=ck.check_roles(context,roles)
    receipt['controls_rejected']=ck.controls(context,roles)
    edits_path=PACKAGE/'EDITS.json'
    edits=ck.read(edits_path)['edits']
    by_role={(z['stage'],z['replica'],z['helper']):i for i,z in enumerate(roles)}
    omitted=[]
    for edit in edits:
        bad=roles.copy();index=by_role[tuple(edit['role'])]
        z=dict(roles[index]);z.update(edit['before'])
        child=z['child'];owner=z['owner_replica'];port=z['port']
        z['copy']=112*owner+port
        z['family']=owner*896+(2*context['child_pair'][child]+context['side'][child])*112+port
        bad[index]=z
        try:ck.check_roles(context,bad)
        except ValueError as exc:omitted.append(dict(role=edit['role'],reason=str(exc)))
        else:raise AssertionError('Accepted omitted edit '+str(edit['role']))
    receipt['omitted_edits_rejected']=omitted
    receipt['checker_adaptation']=dict(source_sha256=sha(SOURCE),adapted_sha256=sha(adapter),changes=changes)
    inputs=[args.word,args.local_replay,owner_path,edits_path,SOURCE]+refs
    receipt['input_sha256']={str(p.resolve()):sha(p)for p in inputs}
    receipt['scope']='Fresh independent full owner/event/chart/profile/prefix/row check with native U8 word/replay binding. Full controller emission, complete finite invoice and supplier ancestry admission remain separate.'
    receipt['baseline_mode']='provided_replay_base'
    args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k]for k in ['status','roles','calls','prefix_bits','physical_row_coefficient','idle']}))
    print('Controls:',len(receipt['controls_rejected']),'omitted edits:',len(omitted))

if __name__=='__main__':main()
