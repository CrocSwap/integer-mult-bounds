#!/usr/bin/env python3
"""Reject frame omissions, cap violations, cost misreports and scalar changes.
Apache-2.0. Prepared by OpenAI Codex with substantial AI assistance.
"""
import argparse, contextlib, copy, gzip, hashlib, importlib.util, io, json, subprocess, sys, tempfile
from pathlib import Path
import build_frame_raises as B


def main():
    if not __debug__: raise RuntimeError('Assertions are required; do not use Python -O')
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('input','recipe','word','audit','main','out'): ap.add_argument('--'+k,type=Path,required=True)
    a=ap.parse_args(); raw=gzip.decompress(a.input.read_bytes()); base=json.loads(raw); recipe=json.loads(a.recipe.read_text())
    word=json.loads(gzip.decompress(a.word.read_bytes()))
    assert hashlib.sha256(raw).hexdigest()==recipe['input_sha256']
    assert hashlib.sha256(gzip.decompress(a.word.read_bytes())).hexdigest()==recipe['output_sha256']
    s=importlib.util.spec_from_file_location('independent_audit',a.audit); audit=importlib.util.module_from_spec(s); s.loader.exec_module(audit)
    records=[]
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        def check(w):
            p=tmp/'mutant.json.gz';p.write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0))
            with contextlib.redirect_stdout(io.StringIO()): audit.run(p,tmp/'audit.json',a.main)
        def reject(name,fn,prefix):
            try:fn()
            except (AssertionError,RuntimeError) as e:
                got=str(e.args[0]) if e.args else type(e).__name__
                assert got.startswith(prefix),(name,prefix,got)
                records.append(dict(name=name,rejection=got[:240])); return
            raise AssertionError('mutation accepted: '+name)
        check(word)
        for j,change in enumerate(recipe['changes']):
            site='%s%d'%(change['section'],change['index'])
            bad=copy.deepcopy(recipe);bad['changes'][j]['old']=[]
            reject(site+'-wrong-old-frame',lambda bad=bad:B.apply(base,bad),"('old frame mismatch'")
            bad=copy.deepcopy(recipe);bad['changes'][j]['new']=[256,128,64,32,16,8,4,2,1]
            reject(site+'-above-successor-cap',lambda bad=bad:B.apply(base,bad),"('above successor cap'")
            bad=copy.deepcopy(recipe);bad['changes'].pop(j)
            reject(site+'-recipe-edit-omitted',lambda bad=bad:B.apply(base,bad),'final profile')
            bad=copy.deepcopy(word);bad[change['section']][change['index']][-1]=change['old']
            reject(site+'-word-frame-reverted-cost-kept',lambda bad=bad:check(bad),'paid profile mismatch')
        bad=copy.deepcopy(word);e=bad['B'][recipe['changes'][0]['index']];assert e[0]=='add';e[3]+=e[4]
        reject('changed-scalar-with-frames-intact',lambda:check(bad),'all-column endpoint failure')
        bad=copy.deepcopy(word);bad['report']['local_profile']['4']+=1
        reject('misreported-paid-rank-four-count',lambda:check(bad),'paid profile mismatch')
        tampered=copy.deepcopy(base);tampered['report']['local_profile']['1']+=1
        p=tmp/'tampered.json.gz';p.write_bytes(gzip.compress(json.dumps(tampered,separators=(',',':')).encode(),mtime=0))
        result=subprocess.run([sys.executable,'-B',B.__file__,'--input',str(p),'--recipe',str(a.recipe),'--out',str(tmp/'badbuild')],capture_output=True,text=True)
        assert result.returncode!=0 and 'AssertionError: input word pin' in result.stderr,'input pin control'
        records.append(dict(name='tampered-input-pin',rejection='input word pin'))
    assert len(records)==35
    a.out.write_text(json.dumps(dict(status='PASS_FRAME_RETIMING_35_NEGATIVE_CONTROLS',honest='PASS',rejected=records),indent=2)+'\n')
    print('PASS_FRAME_RETIMING_35_NEGATIVE_CONTROLS',flush=True)


if __name__=='__main__':main()
