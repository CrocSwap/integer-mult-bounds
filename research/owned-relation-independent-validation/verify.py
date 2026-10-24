#!/usr/bin/env python3
"""Independent PR5377 packet replay, standard-library Python, no Git/network.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
The two frozen review engines retain their attribution and exact source bytes.
"""
from pathlib import Path, PurePosixPath
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, tempfile, time

HERE = Path(__file__).resolve().parent
CAPSULE_SHA256 = '3351f3826dff8c1b39aa63f15a1f8d2764111ae61ffb4d49a2ebd3ed658471e6'
HEAD = 'c448d13c71908647f968b06cddb795ce7d288139'
MAIN = '1ec1119972c9aefe42525172d07b332fcff81cb4'
BASE = '7c472563474e60185e6ca101a17622133d047e56'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def digest(raw, kind='blob'):
    return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def file_at(root, name):
    parts=PurePosixPath(name)
    need(not parts.is_absolute() and '..' not in parts.parts and str(parts)==name, 'unsafe packet path')
    current=root
    for part in parts.parts:
        current=current/part
        need(not current.is_symlink(), 'symlink in packet path '+name)
    need(current.is_file(), 'missing packet file '+name)
    return current

def inventory(root, manifest):
    seen=set()
    for row in manifest['files']:
        name=row['path'];need(name not in seen,'duplicate inventory path');seen.add(name)
        raw=file_at(root,name).read_bytes()
        need(len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'] and digest(raw)==row['git_blob'], 'source/receipt byte guard: '+name)
    actual={q.relative_to(root).as_posix() for folder in ['capsule','engines','evidence','git-evidence'] for q in (root/folder).rglob('*') if q.is_file()}
    need(actual==seen-{'SOURCE-GUARDS.json'}, 'extra/missing capsule inventory file')
    return len(seen)

def object_at(root,kind,sha):
    raw=file_at(root,'git-evidence/'+kind+'/'+sha).read_bytes()
    need(digest(raw,kind)==sha,'raw Git object hash '+sha)
    return raw

def tree_entries(raw):
    result={};i=0
    while i<len(raw):
        j=raw.index(b' ',i);k=raw.index(b'\0',j);name=raw[j+1:k].decode('utf-8')
        need(name not in result and k+21<=len(raw),'malformed raw Git tree')
        result[name]=(raw[i:j].decode(),raw[k+1:k+21].hex());i=k+21
    return result

def source_guards(root):
    guards=read(root/'SOURCE-GUARDS.json')['rows']
    for row in guards:
        raw=object_at(root,'commit',row['commit']);first=raw.split(b'\n',1)[0].split()
        need(first[0]==b'tree','commit tree header');tree=first[1].decode()
        parts=row['path'].split('/')
        for i,part in enumerate(parts):
            mode,sha=tree_entries(object_at(root,'tree',tree))[part]
            if i==len(parts)-1:
                need(mode=='100644' and sha==row['git_blob'],'raw committed blob identity '+row['path'])
                need(digest(file_at(root,row['local']).read_bytes())==sha,'source alias mismatch '+row['local'])
            else:
                need(mode=='40000','non-tree source ancestor');tree=sha
    # Both commits are sibling children of the author source base. The candidate
    # head is expressly not used as SOURCES.json canonical provenance.
    for commit in [HEAD,MAIN]:
        raw=object_at(root,'commit',commit)
        need(('parent '+BASE+'\n').encode() in raw.split(b'\n\n',1)[0]+b'\n','source base parent relation')
    author=read(root/'capsule/research/kappa-owned-relation-20261023/SOURCES.json')
    need(author['base_commit']==BASE,'original author base')
    need(sum(r['usage']=='input' for r in author['files'])==9 and len(author['files'])==14,'original9input14rowcontract')
    need(sum(r['local'].startswith('capsule/research/kappa-owned-relation-20261023/') for r in guards)==9,'original9filepayload')
    return len(guards)

def cold_receipt(root):
    cold=root/'evidence/cold';v=read(cold/'VALIDATION.json');bound=read(cold/'BOUNDED-REGISTERED-RUN.json')
    need(v['head']==HEAD and v['current_canonical_main_pin']==MAIN,'cold exact source pins')
    need(v['status']=='PASS_OWN_COMPLETE_REGISTERED_PR5377_NORMAL_AND_OPTIMIZED','full frozen cold result')
    need(bound['status']=='PASS_COMPLETE_REGISTERED_NORMAL_AND_OPTIMIZED' and bound['exit']==0 and bound['resource_stop'] is None and not bound['scientific_bytes_changed'],'frozen bounded execution result')
    need(read(cold/'PRE-RUN-HASHES.json')==read(cold/'POST-RUN-HASHES.json'),'cold input immutability')
    for name,sha in v['evidence_sha256'].items():
        need(hashlib.sha256(file_at(cold,name).read_bytes()).hexdigest()==sha,'complete cold receipt '+name)
    original=root/'capsule/research/kappa-owned-relation-20261023/RESULT.json'
    need(hashlib.sha256(original.read_bytes()).hexdigest()==v['full_result_sha256'],'cold full scientific artifact')
    need(v['normal_stdout_result']==v['optimized_stdout_result'],'cold mode result equality')
    need(v['total_control_executions']==24 and v['all_54_strict_outer_positive'] and v['all_four_functional_positive'],'cold complete registered coverage')
    log=(cold/'REGISTERED-COLD.stdout.log').read_text()
    need(log.count('"status": "PASS_CONDITIONAL_KAPPA_00302235_ONE_OWNED_RELATION"')==2 and 'PASS_REGISTERED_RESEARCH_PACKAGE' in log,'cold complete stdout')
    return dict(status=bound['status'],seconds=bound['seconds'],fresh_here=False,source_files_unchanged=bound['hash_inventory_files'],controls=v['total_control_executions'])

def make_engine(root,name,dest):
    shutil.copytree(root/'engines'/name,dest)
    # The engine program can write its result in dest; its source inputs and
    # nested directories are read-only. No package evidence is overwritten.
    sub=dest/('pinned' if name=='physical' else 'frozen')
    for q in sub.rglob('*'):
        if q.is_file():q.chmod(0o444)
    sub.chmod(0o555)
    return sub

def launch(dest,script):
    argv=[sys.executable]
    if sys.flags.optimize:argv+=['-O']
    argv+=['-B',str(dest/script)]
    env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None);env['PYTHONPYCACHEPREFIX']=str(dest/'private-bytecode')
    return subprocess.run(argv,cwd=dest,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=110)

def stable(result):
    result=dict(result);result.pop('seconds',None);return result

def run_engines(root,tmp):
    results={}
    for name,script,expected in [('physical','independent_physical_check.py','evidence/physical/independent-result.json'),('cost','check_cost.py','evidence/cost/RESULT.json')]:
        dest=tmp/name;inputs=make_engine(root,name,dest);before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in inputs.iterdir() if q.is_file()}
        run=launch(dest,script);need(run.returncode==0,'independent '+name+' engine failed: '+run.stderr[-2500:])
        fresh=json.loads(run.stdout);old=read(root/expected)
        # The initial cost receipt predates later provenance captures in its
        # frozen folder. Bind every current hash by CAPSULE+Merkle guards, then
        # require all original receipt hashes and every mathematical field.
        if name=='cost':
            hashes=fresh.pop('sha256');oldhash=dict(old.pop('sha256'))
            need(hashes==before and all(hashes[k]==v for k,v in oldhash.items()),'cost complete frozen source map')
        need(stable(fresh)==stable(old),'complete stable '+name+' result differs')
        need(before=={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in inputs.iterdir() if q.is_file()},'engine changed frozen input')
        results[name]=dict(status=fresh['status'],seconds=fresh['seconds'],complete_stable_result_equal=True,source_hashes=len(before))
    return results

def semantic_controls(root,tmp,manifest):
    # A raw byte mutation must fail before evaluator execution.
    row=next(r for r in manifest['files'] if r['path']=='capsule/research/kappa-owned-relation-20261023/README.md')
    changed_root=tmp/'control-source';changed_root.mkdir()
    target=changed_root/row['path'];target.parent.mkdir(parents=True)
    target.write_bytes((root/row['path']).read_bytes()+b'\n')
    try:
        inventory(changed_root,{'files':[row]})
    except ValueError as error:
        need('source/receipt byte guard: '+row['path'] in str(error),'source control wrong failure')
    else:
        raise ValueError('altered source byte accepted')
    out=['altered source byte rejected by actual inventory guard']
    dest=tmp/'control-cost';shutil.copytree(root/'engines/cost',dest)
    path=dest/'frozen/RESULT.json';receipt=read(path)
    receipt['arithmetic']['targets']['9']+=16
    path.write_text(json.dumps(receipt))
    run=launch(dest,'check_cost.py')
    need(run.returncode!=0 and 'author invoice crosscheck' in run.stderr,
         'productive-credit control wrong failure: '+run.stderr[-2000:])
    out.append('unearned16rank9productive-targets rejected by literal census')
    out.append('fresh physical engine executes its intrinsic wrong-relation and wrong-snapshot controls')
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--integrity-only',action='store_true');args=parser.parse_args();start=time.monotonic()
    raw=(HERE/'CAPSULE.json').read_bytes();need(hashlib.sha256(raw).hexdigest()==CAPSULE_SHA256,'capsule manifest immutable hash')
    manifest=json.loads(raw);need(manifest['frozen_cold_complete'] and manifest['canonical_base']==MAIN and manifest['author_head']==HEAD,'complete packet pins')
    count=inventory(HERE,manifest);guards=source_guards(HERE);cold=cold_receipt(HERE)
    result=dict(status='PASS_INDEPENDENT_PR5377_CAPSULE_INTEGRITY',head=HEAD,inventory_files=count,raw_merkle_source_paths=guards,cold_frozen_receipt=cold)
    if not args.integrity_only:
        with tempfile.TemporaryDirectory(prefix='pr5377-independent-') as folder:
            tmp=Path(folder);result['independent_engines']=run_engines(HERE,tmp);result['wrapper_controls']=semantic_controls(HERE,tmp,manifest)
        inventory(HERE,manifest)
        result.update(status='PASS_INDEPENDENT_PR5377_CONDITIONAL_VALIDATION',kappa='60447/20000000',gain_over_selected4610='2871/5000000000',fixed_profile_root=['302238736347/100000000000000','75559684087/25000000000000'],framework_assumptions=5,selected_record_changed=False)
    result['seconds']=round(time.monotonic()-start,3);print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
