"""Optional exact committed-object custody; reads no archive code into execution."""
from pathlib import Path
from hashlib import sha1, sha256
from io import BytesIO
import argparse
import importlib.util
import json
import subprocess
import sys
import tarfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('custody_comparison',HERE/'compare_maps.py')
B=importlib.util.module_from_spec(spec);sys.modules[spec.name]=B;spec.loader.exec_module(B)
HEAD='17c08db090004c1fb54220a6d8463a5095789fa9'
PACKAGE='research/p104-common-idle-double-retirement'
ARCHIVE_SHA='be2180627c3a9ffc0176434b578659c5769c8546e3ee67dcee55c632646ebe93'
ARCHIVE_BLOB='80fd2423e2d2e52dda3b250173068ab9c981c08e'


def blob(raw):
    return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def member(raw,name):
    with tarfile.open(fileobj=BytesIO(raw),mode='r:') as t:
        f=t.extractfile(name);B.need(f is not None,'regular exact archive member')
        return f.read()


def run(repo):
    pins=B.read('SOURCES.json')['files'];B.authenticate()
    def git(head,path):
        return subprocess.run(['git','-C',str(repo),'show',head+':'+path],check=True,stdout=subprocess.PIPE).stdout
    direct=[]
    for p in pins:
        if 'head' not in p:continue
        raw=git(p['head'],p['path'])
        B.need(raw==(HERE/p['copy']).read_bytes(),'direct committed source '+p['copy'])
        direct.append({'head':p['head'],'path':p['path'],'copy':p['copy'],'git_blob':blob(raw),'sha256':sha256(raw).hexdigest()})
    archive=git(HEAD,PACKAGE+'/source6702/source.tar')
    B.need(sha256(archive).hexdigest()==ARCHIVE_SHA and blob(archive)==ARCHIVE_BLOB,
           'exact current owning outer source archive')
    retained=member(archive,'research/gaussian-root-retirement/RETAINED.json')
    manifest=json.loads(retained);engine=manifest['engines']
    engines=member(archive,'research/gaussian-root-retirement/'+engine['archive'])
    B.need(sha256(engines).hexdigest()==engine['archive_sha256'],'engines nested archive SHA')
    nested=[]
    for p in pins:
        if not p['copy'].startswith('vendor/current/'):continue
        name=p['container'].split('!/')[2]
        raw=member(engines,name)
        pin=next(x for x in engine['files'] if x['path']==name)
        B.need(raw==(HERE/p['copy']).read_bytes() and sha256(raw).hexdigest()==pin['sha256'] and blob(raw)==pin['git_blob'],
               'exact current compiler nested member '+name)
        nested.append({'member':name,'copy':p['copy'],'sha256':sha256(raw).hexdigest(),'git_blob':blob(raw)})
    native=manifest['native']
    native_archive=member(archive,'research/gaussian-root-retirement/'+native['archive'])
    B.need(sha256(native_archive).hexdigest()==native['archive_sha256'],'nested original native archive')
    raw=member(native_archive,'research/p104-scaled-transport-fusion/WORD.json.gz')
    B.need(raw==(HERE/'inputs/CURRENT-WORD.json.gz').read_bytes(),'reachable17c copy equals original nested actual native')
    return {'schema':'native-admission-current-committed-container-custody/1',
            'status':'PASS_DIRECT_GIT_OBJECTS_AND_NESTED_COMPILER_MEMBERS',
            'direct_sources':direct,'outer_source':{'head':HEAD,'path':PACKAGE+'/source6702/source.tar','sha256':ARCHIVE_SHA,'git_blob':ARCHIVE_BLOB},
            'retained_manifest_sha256':sha256(retained).hexdigest(),
            'engines_archive_sha256':sha256(engines).hexdigest(),'compiler_members':nested,
            'native_archive_sha256':sha256(native_archive).hexdigest(),
            'current_native_word_sha256':sha256(raw).hexdigest(),
            'source_code_executed':False,
            'scope':'Only exact scoped Git blobs and named archive members. Earlier nested source_head labels are lineage, not a claim that edited archive members belong to those old trees. No full repository archive or mathematical replay.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--write',action='store_true');a=p.parse_args()
    r=run(a.repo);raw=json.dumps(r,sort_keys=True,indent=2)+'\n';path=HERE/'SOURCE-CUSTODY.json'
    if a.write:path.write_text(raw)
    else:B.need(path.read_text()==raw,'read-only exact committed-source custody receipt')
    print(r['status'])
