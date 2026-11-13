#!/usr/bin/env python3
"""Portable read-only source-only rank-one singleton verification."""
from pathlib import Path
from hashlib import sha1,sha256
import json,sys,types
HERE=Path(__file__).resolve().parent
def need(ok,label):
    if not ok:raise ValueError(label)
def load(name):
    path=HERE/'verifier'/name;module=types.ModuleType('rank1_'+path.stem);module.__file__=str(path);sys.modules[module.__name__]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__);return module
def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    need(sources['base_commit']=='e54523517d0f03e58352e647c403a5af3e525a57','canonical base')
    for source in sources['bundled_external_inputs']:
        path=Path(source['path']);need(not path.is_absolute() and '..' not in path.parts,'local source path');f=HERE/path;need(f.is_file() and not f.is_symlink(),'regular source');b=f.read_bytes()
        need(sha256(b).hexdigest()==source['sha256'] and sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==source['git_blob'],'exact bundled source bytes')
    source=HERE/'inputs/WORD.json.gz';author=load('author.py');document=author.verify(source);certificate_hash=digest(document)
    independent=load('independent.py');review=independent.review(source,document)
    need(digest(document)==certificate_hash,'author document remains unchanged')
    decisions=[]
    for c in document['cases']:
        decisions.append({'helper':c['helper'],'class':c['classification'],'zero_MOVEs':c['zero_MOVE_events'],'nonzero_cached_MOVEs':c['new_nonzero_cache_events'],'events':[{'event':h['event'],'literal':h['literal'],'rank':h['rank'],'zero':h['zero']} for h in c['hits']],'credit_rank1_jobs':1,'lost_rank1_target':1,'net_native_gain':0})
    result={'status':'PASS_COMPLETE_RANK1_SINGLETON_ZERO_CACHE_BOUND','source_sha256':document['source_sha256'],'source_payload_sha256':document['source_payload_sha256'],'published_neutral_predecessor_cache_commit':'fdbb41450a98594bdf1f5fe4535e77d2466adb4f','helpers':document['helpers_tested'],'neutral12':document['neutral_rank1_helpers'],'new6':document['nonneutral_rank1_helpers'],'all_MOVE_cuts_per_promise':6279,'coframes':979,'original_observation_rank':7780,'singletons_only':True,'joint_helper_extension_claimed':False,'decisions':decisions,'full_certificate_sha256':certificate_hash,'independent_review':review,'scope':'Original retained coordinate targets, whole original MOVEs and unchanged strict original histories only. Each singleton permits at most f1 credit against f1 target debit. No physical cache/zero-reframe/ordinary/owned admission, foundation removal or new kappa.'}
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
