#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Mutate G within its retirement frame: handoff remains valid, prelude fails."""
import gzip,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from check_interface import HERE,H,span,linear,permutations,sha,require

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())

def main():
    path=HERE/'words/FOUR-base.json.gz';w=read(path);flags=read(HERE/'FLAG-FOUR.json')
    f=next(c for c in flags['cases'] if c['provider']=='gauge44' and c['baseline']=='high48')['records'][0]
    U=f['retirement_basis'];S=f['entrance_basis'];G=f['G_columns'];op=f['operator']
    C=list(U)
    for j in range(H):
        if 1<<j not in span(C):C.append(1<<j)
    _,back=permutations(C);changed=list(C);changed[0],changed[1]=changed[1],changed[0]
    Hcols=[linear(changed,back[1<<j]) for j in range(H)]
    Gbad=[linear(G,x) for x in Hcols]
    require({linear(Gbad,x) for x in span(U)}==span(f['handoff_basis']),'mutation must retain handoff')
    require({linear(Gbad,x) for x in span(S)}!=span([30]),'mutation must break entrance flag')
    require(w['warps'][op-1][2]==G,'word/flag source binding')
    w['warps'][op-1][2]=Gbad
    script=HERE/'transport_lifted.py';script_before=sha(script)
    with tempfile.TemporaryDirectory(prefix='seed39-wrong-prelude-flag-') as td:
        root=Path(td);bad=root/'BAD-WORD.json.gz';out=root/'output'
        bad.write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0))
        result=subprocess.run([sys.executable,'-B',str(script),str(bad),str(out)],capture_output=True,text=True)
        require(result.returncode!=0 and 'warp G does not carry the frame' in result.stderr,'mutant not rejected by new prelude frame check')
        require(not out.exists(),'failed transport wrote a success directory')
        require(sha(script)==script_before,'transport changed while control ran')
        receipt=dict(status='PASS_HANDOFF_PRESERVING_WRONG_ENTRANCE_FLAG_REJECTED',word_sha256=sha(path),transport_sha256=script_before,
            operator=op,lender=f['lender'],old_G=G,mutated_G=Gbad,retirement_frame_preserved=True,entrance_flag_broken=True,
            mutated_word_sha256=sha(bad),exit_code=result.returncode,stderr=result.stderr,stdout=result.stdout,
            scope='Actual adapted transport rejects a G that passes its old retirement-frame obligation but fails the new A-phase entrance-frame obligation. No native/global admission implied.')
        (HERE/'TRANSPORT-FLAG-CONTROL.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])

if __name__=='__main__':main()
