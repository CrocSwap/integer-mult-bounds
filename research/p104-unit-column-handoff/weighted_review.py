#!/usr/bin/env python3
"""Independent replay/controls for the 26/272 alternative.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Credits the retained #6297 source handoff and #5602 local scalar tariff.
"""
from copy import deepcopy
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import argparse,json
from pathlib import Path
from types import ModuleType

_checker_path = Path(__file__).with_name('independent.py')
_checker_bytes = _checker_path.read_bytes()
if sha256(_checker_bytes).hexdigest() != 'f7a76321beb92dbd1151e59092b17e2240d7a3037bc6e90f10b8ba2b31ee5b6a':
    raise ValueError('independent replay implementation bytes')
I = ModuleType('weighted_independent_replay')
I.__file__ = str(_checker_path)
exec(compile(_checker_bytes, str(_checker_path), 'exec'), I.__dict__)


def audit(source,candidate):
    before,snapshot=I.replay(source,checkpoint=I.CUT)
    I.boundary_audit(source,snapshot)
    after,_=I.replay(candidate)
    I.require(candidate['frames']==source['frames'] and candidate['live']==source['live'] and candidate['ports']==source['ports'],'frame/port preservation')
    expected_final=source['final'][:];expected_final[I.PIVOT]=1053;expected_final.append(127)
    I.require(candidate['initial']==source['initial']+[1053] and candidate['final']==expected_final,'exact changed boundaries')
    I.require(after['paid']==before['paid'],'paid profile preservation')
    expected=Counter(before['helpers']);expected[9]-=1;expected[5]+=1;expected[4]+=1
    I.require(after['helpers']==dict(sorted(expected.items())),'physical target split')
    I.require(after['initialized']==after['cleared']==before['initialized']==before['cleared']==8 and after['peak_owned']==before['peak_owned']==1,'owned lifetime preservation')
    I.require(before['public']==735 and before['events']==25140 and before['allowance']==217428,'source fixture inventory')
    I.require(after['public']==736 and after['events']==25166 and after['allowance']==217700,'alternative fixture inventory')
    return {'before':before,'after':after,'inserted_events':26,'inserted_allowance':272}


def controls(source,candidate):
    cases=[]
    x=deepcopy(candidate);x['program'][0][-2]=str(-Fraction(x['program'][0][-2]));cases.append(('changed boundary coefficient',x))
    x=deepcopy(candidate);del x['program'][0];cases.append(('omitted boundary gate',x))
    x=deepcopy(candidate);x['program'][0][-1]=1053;cases.append(('unavailable boundary chart',x))
    x=deepcopy(candidate);x['program'].insert(0,['INIT',735,1053]);cases.append(('erase independent new public input',x))
    x=deepcopy(candidate);del x['program'][next(i for i,e in enumerate(x['program']) if e[0]=='CLEAR')];cases.append(('omit owned clear',x))
    x=deepcopy(candidate);x['final'][596]=127;cases.append(('unsplit retired exit',x))
    x=deepcopy(candidate);x['initial'][735]=3;cases.append(('misplace new independent input',x))
    x=deepcopy(candidate);x['frames'][1053]=[7,25,42,192,192];cases.append(('dependent cut basis',x))
    x=deepcopy(candidate);x['program'].insert(0,['SCALE',596,'3',3]);cases.append(('nonunit SCALE',x))
    x=deepcopy(candidate);x['program'][0][-2]='1/3';cases.append(('nondyadic boundary',x))
    out=[]
    for name,word in cases:
        try:audit(source,word)
        except ValueError as error:
            I.require('fixture inventory' not in str(error),'mutation rejected only by fixture inventory')
            out.append({'name':name,'rejection':str(error)})
        else:raise ValueError('accepted semantic mutant '+name)
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--word',type=Path,required=True);args=p.parse_args()
    I.require(sha256(args.source.read_bytes()).hexdigest()==I.SOURCE_SHA256,'pinned source bytes')
    I.require(sha256(args.word.read_bytes()).hexdigest()=='65375c8fbc810322283495954405b7d46048a3ef66d12712a32276ba7bf90d67','pinned weighted candidate bytes')
    source,candidate=I.load_word(args.source),I.load_word(args.word)
    result=audit(source,candidate);result['controls']=controls(source,candidate)
    print(json.dumps(result,sort_keys=True));print('PASS_INDEPENDENT_WEIGHTED_ALTERNATIVE')

if __name__=='__main__':main()
