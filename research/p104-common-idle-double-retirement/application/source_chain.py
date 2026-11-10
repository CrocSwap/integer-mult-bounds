"""Read only the two pinned source archives; never execute their code."""
from pathlib import Path
from hashlib import sha256,sha1
from io import BytesIO
import argparse
import gzip
import json
import tarfile

HERE=Path(__file__).resolve().parent


def need(ok,why):
    if not ok:raise ValueError(why)


def checked(b,pin):
    need(sha256(b).hexdigest()==pin['sha256'],'exact source member SHA')
    need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==pin['git_blob'],'exact source member blob')


def run(package):
    pins=json.loads((HERE/'inputs/SOURCE6702.json').read_bytes())
    need(pins['source_head']=='edd6a37a9ff87b254fb7466184348d1432d0c8c0','6702 exact owning head')
    for pin in pins['files']:checked((package/pin['path']).read_bytes(),pin)
    b=(package/'source6702/source.tar').read_bytes()
    outer=json.loads((HERE/'inputs/SOURCE-RETAINED.json').read_bytes())
    need(sha256(b).hexdigest()==outer['archive_sha256'],'exact outer retained archive')
    with tarfile.open(fileobj=BytesIO(b),mode='r:')as tar:
        raw=tar.extractfile('research/gaussian-root-retirement/RETAINED.json').read()
        need(raw==(HERE/'inputs/NATIVE-RETAINED.json').read_bytes(),'exact extracted native inventory')
        record=json.loads(raw)['native']
        native_archive=tar.extractfile('research/gaussian-root-retirement/'+record['archive']).read()
    need(sha256(native_archive).hexdigest()==record['archive_sha256'],'exact nested native archive')
    with tarfile.open(fileobj=BytesIO(native_archive),mode='r:')as tar:
        raw=tar.extractfile('research/p104-scaled-transport-fusion/WORD.json.gz').read()
        base_raw=tar.extractfile('research/p104-scaled-transport-fusion/BASEWORD.json.gz').read()
    need(raw==(HERE/'inputs/NATIVE.json.gz').read_bytes(),'actual nested word is the independent checker input')
    current=json.loads(gzip.decompress(raw));base=json.loads(gzip.decompress(base_raw))
    need(current['frames']==base['frames'],'retained base/current share literal native frame alphabet')
    def tasks(w):
        main=set(w['live'])|{r+112 for r in w['live']}
        return {(e[2],e[3])for e in w['program']if e[0]=='MOVE'}|{
            (w['initial'][r],w['final'][r])for r in range(w['public'])if r not in main}
    before,after=tasks(base),tasks(current)
    added=[{'frame_ids':[a,b],'source_axes':current['frames'][a],
            'target_axes':current['frames'][b],
            'paid_rank':abs(len(current['frames'][a])-len(current['frames'][b]))}
           for a,b in sorted(after-before)]
    return {'schema':'p104-actual-outer-source-chain/1','status':'PASS_EXACT_6702_ARCHIVE_MEMBER_CUSTODY',
       'owning_head':pins['source_head'],'outer_source_files_checked':len(pins['files']),
       'outer_archive_sha256':outer['archive_sha256'],'native_archive_sha256':record['archive_sha256'],
       'native_word_sha256':sha256(raw).hexdigest(),'source_code_executed':False,
       'retained_BASEWORD_sha256':sha256(base_raw).hexdigest(),
       'literal_task_delta_vs_retained_BASEWORD':{'base_tasks':len(before),'current_tasks':len(after),
           'added':added,'removed':[list(x)for x in sorted(before-after)],
           'scope':'Combined edited current native versus its retained6529 BASEWORD, not a map equivalence test and not a delta versus6030 or6621 alone.'},
       'scope':'Exact original6702 container custody. Retained nested head labels are lineage labels; modified members are authenticated by this actual outer archive, not asserted to belong directly to those earlier Git trees.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--write',action='store_true');a=p.parse_args()
    r=run(a.package);text=json.dumps(r,sort_keys=True,indent=2)+'\n';path=HERE/'SOURCE-CHAIN.json'
    if a.write:path.write_text(text)
    else:need(path.read_text()==text,'read-only source chain receipt')
    print(r['status'])
