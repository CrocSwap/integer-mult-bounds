"""Retained predecessor #6805 step: one deterministic retiming and independent-helper split; no search at replay.
Package replay rebuilds the #6805 word with this module (payload pin in EXPECTED.json), then lift.py applies the new step.

Jerry Chen / @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The helper-basis constructor is adapted from Ali Romman; see retained sources.
"""
from copy import deepcopy
import native as N
from split import split

def construct(source, witness):
    h=witness['screen_hit']
    N.need((h['cut'],h['frame'],h['pivot'])==(12372,243,368),'Frozen successful cut')
    N.need(len(h['paths'])==1,'One genuinely paid retiming')
    p=h['paths'][0]
    N.need((p['role'],p['old'],p['new'],p['moves'],p['private'])==(80,749,127,[14088],False),
           'Exact advanced rank-six request')
    N.need(source['program'][14088]==['MOVE',80,749,127,False],'Bound source event')
    for e in source['program'][12372:14088]:
        N.need(e[1]!=80 and not(e[0]in('ADD','COPY')and e[2]==80),'No intervening role80 contact')
    prepared=deepcopy(source)
    prepared['program']=source['program'][:12372]+[['MOVE',80,749,243,False],['MOVE',80,243,127,False]]+source['program'][12372:14088]+source['program'][14089:]
    N.replay(prepared)
    N.need(witness['prepared_cut']==witness['split']['cut_after']==12372,'Basis lies between paid subdivisions')
    return split(prepared,witness['split'])

if __name__=='__main__':
    import argparse,gzip,json
    from pathlib import Path
    here=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    word=construct(N.read(here/'retained/native/PR6702-WORD.json.gz'),N.read(here/'WITNESS.json'))
    raw=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    args.output.write_bytes(gzip.compress(raw,mtime=0)if args.output.suffix=='.gz'else raw+b'\n')
