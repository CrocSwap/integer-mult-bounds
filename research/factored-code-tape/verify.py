"""Check the complete local kernel and emitted words. Apache-2.0.
Ali Romman with OpenAI Codex assistance.
"""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
import json
import argparse

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok, why):
    if not ok: raise ValueError(why)

def module(path):
    ns={'__name__':path.stem,'__file__':str(path)}
    exec(compile(path.read_bytes(),str(path),'exec'),ns)
    return SimpleNamespace(**ns)

def run():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage']=='input':
            need(sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'Source pin')
    source=module(ROOT/'research/coded-inverse-fixed-grid/kernel.py')
    new=module(HERE/'kernel.py')
    modes=json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())['mode_columns']
    (gather,gp),(scatter,sp)=new.emit(modes)
    need((len(gather),len(scatter))==(308,280),'Emitted operation count')
    need(max(gp,sp)<=8,'Temporary allocation')
    for column in range(112):
        words=[[0]*9 for _ in range(129)];words[column]=source.encode(1,9)
        for instruction in gather:new.signed_sum(words,instruction)
        need([source.decode(w) for w in words[112:120]]==[c[column] for c in modes],'Gather basis')
    for column in range(8):
        words=[[0]*9 for _ in range(129)];words[112+column]=source.encode(1,9)
        for instruction in scatter:new.signed_sum(words,instruction)
        need([source.decode(w) for w in words[:112]]==[-v for v in modes[column]],'Scatter basis')
    vectors=0;batch_cases=0
    for H in (0,1,6,26,51,250):
        W=source.word_width(H)
        for N in (0,1,3):
            data=[[[((i*i+17*j+13)%(2*H+1))-H for i in range(112)] for j in range(N)],
                  [[H if i%2 else -H for i in range(112)] for _ in range(N)]]
            for columns in data:
                records=[[source.encode(columns[j][i],W) for j in range(N)] for i in range(112)]
                scratch=[[1]*W for _ in range(17)]
                receipt=new.recode_many(records,scratch,H,modes,source)
                need(all(not any(w) for w in scratch),'Owned return')
                for j,x in enumerate(columns):
                    old=[source.encode(v,W) for v in x]
                    source.recode(old,modes,H,[[1]*W for _ in range(9)])
                    need([row[j] for row in records]==old,'Exact source word equality')
                    vectors+=1
                bound=17*(2*W+4)+N*(112*(8*W+16)+588*(2*W+4)+8*(24*W+64)+16*(2*W+4)+W+1)+N*(W+1)+64
                need(receipt['transitions_upper']==bound,'Independent invoice sum')
                if N:
                    need(bound<source.tape_invoice(W,N)['transition_upper'],'Strict local tariff reduction')
                batch_cases+=1
    # Break a live numerical coefficient, not only a metadata field.
    bad=list(gather);dst,left,right,a,b=bad[0];bad[0]=(dst,left,right,-a,b)
    rejects=False
    for column in range(112):
        words=[[0]*9 for _ in range(129)];words[column]=source.encode(1,9)
        for instruction in bad:new.signed_sum(words,instruction)
        if [source.decode(w) for w in words[112:120]]!=[c[column] for c in modes]:rejects=True;break
    need(rejects,'Signed coefficient mutation')
    W=source.word_width(1);records=[[source.encode(0,W)] for _ in range(112)]
    records[1]=records[0]
    try:new.recode_many(records,[[0]*W for _ in range(17)],1,modes,source)
    except ValueError:pass
    else:raise ValueError('Owner alias accepted')
    return {'status':'PASS_FACTORED_CODE_TAPE','gather_columns':112,'scatter_columns':8,
            'mixed_and_extreme_vectors':vectors,'batch_cases':batch_cases,'signed_sums':588,
            'temporary_words':max(gp,sp),'tapes':130,'scratch_words':17,
            'transition_upper':'N(2298W+4722)+34W+132','zero_scans':'144N+17',
            'controls':['wrong_sign','owner_alias'],'physical_caller_run':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-result',action='store_true')
    args=parser.parse_args()
    result=run()
    path=HERE/'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(json.loads(path.read_text())==result,'Receipt mismatch')
    print(json.dumps(result,sort_keys=True))
