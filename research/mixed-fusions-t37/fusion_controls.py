"""PR1195's ten structural fusion mutations, applied to both new providers.

Adapted from Marius-Paul Dumitrean / Claude's PR1195 controls.py. The scalar
site coordinates are unchanged by the four-entrance frame refit. Each honest
word is independently admitted before its mutations are tested.
"""
import argparse,copy,gzip,hashlib,contextlib,io,tempfile
from pathlib import Path
from common import P,ROOT,read,dump,load,sha

def check(out):
    ck=load(ROOT/'research/gauge44-slots/independent/audit_local.py','fusion_independent_raw_audit')
    source=P/'vendor/pr1195/FULL-WORD.json.gz';spec=read(P/'vendor/pr1195/CONTROL-SITES.json')
    assert hashlib.sha256(gzip.decompress(source.read_bytes())).hexdigest()==spec['word_content_sha256']
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='mixed-fusion-controls-')as temporary:
        d=Path(temporary)
        def audit(word):
            dump(d/'WORD.json.gz',word)
            with contextlib.redirect_stdout(io.StringIO()):ck.run(d/'WORD.json.gz',d/'AUDIT.json',ROOT)
        def drop_cleanup(word,index):
            word['cleanup'].pop(index)
            word['early_cleanup']=[[i-1 if i>index else i,frame]for i,frame in word['early_cleanup']]
        for pid,path in [('demote3',source),('demote4',P/'data/FOUR-WORD.json.gz')]:
            word=read(path);audit(word)
            for site in spec['sites']:
                di,ci=site['donation_B_index'],site['restore_cleanup_index']
                assert word['B'][di][:5]==site['donation'] and word['cleanup'][ci][:5]==site['restore']
                for name in ('drop_restore','drop_donation','flip_donation_sign','keep_fused_read','drop_donation_and_restore'):
                    bad=copy.deepcopy(word)
                    if name in ('drop_restore','drop_donation_and_restore'):drop_cleanup(bad,ci)
                    if name in ('drop_donation','drop_donation_and_restore'):bad['B'].pop(di)
                    if name=='flip_donation_sign':bad['B'][di][3]*=-1
                    if name=='keep_fused_read':bad['B'].insert(site['fused_read_B_position'],site['fused_read'].copy())
                    try:audit(bad)
                    except RuntimeError as error:
                        rejected.append(dict(provider=pid,site=site['t'],control=name,reason=str(error)))
                    else:raise AssertionError('Accepted fusion mutation: '+pid+' '+name)
    assert len(rejected)==20
    result=dict(status='PASS_BOTH_PROVIDERS_FUSION_SEMANTIC_CONTROLS',rejected=rejected,
      source_controls_sha256=sha(P/'vendor/pr1195/controls.py'),source_sites_sha256=sha(P/'vendor/pr1195/CONTROL-SITES.json'))
    dump(out,result);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists();print(check(a.out)['status'])
