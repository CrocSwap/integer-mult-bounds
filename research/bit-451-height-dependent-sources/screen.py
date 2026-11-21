#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the pinned single R342 case with the exact endpoint log(1)=0."""
from argparse import ArgumentParser
from datetime import datetime,timezone
from decimal import Decimal,localcontext
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import time

PREV = '10cbcc0fe5c7f44c9a2852a13e6acdf87b52471d52b9685c579c05fc63aab2ea'
CAPPED = '3102b30dd179473189560b3181f072561c490a956571949b672b7c4c9954bcca'


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def checked(path, pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest()!=pin:
        raise ValueError('input hash: '+path.name)
    return raw


def log_ends(integer):
    if integer==1:
        return F(0),F(0)
    y = Decimal(integer).ln()
    return F(y.next_minus()),F(y.next_plus())


def power_lower(a,b,e):
    if a==b or e==0:
        return F(1)
    with localcontext() as ctx:
        ctx.prec=80
        z=e*(log_ends(a)[0]-log_ends(b)[1])
        argument=(Decimal(z.numerator)/Decimal(z.denominator)).next_minus()
        result=F(argument.exp().next_minus())
    return F((result*10**25).__floor__(),10**25)


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--campaign-root',type=Path,required=True)
    parser.add_argument('--snapshot',type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic()
    out={'pins':{'round342/screen.py':PREV,'round342/primary.json':CAPPED},
         'case':{'p':18,'h':1804,'B':'5/2','x_split':'7/8','height_cut':32},
         'decision':'RUNNING','events':[]}
    def snapshot(label):
        out['events'].append({'utc':utc(),'stage':label,'elapsed':time.monotonic()-start})
        tmp=args.snapshot.with_suffix('.pending')
        tmp.write_text(json.dumps(out)+'\n')
        tmp.replace(args.snapshot)
    snapshot('child start')
    try:
        base={'__name__':'authenticated_r342'}
        code=checked(args.campaign_root/'round342/screen.py',PREV)
        old=json.loads(checked(args.campaign_root/'round342/primary.json',CAPPED))
        exec(compile(code,'round342/screen.py','exec'),base)
        if log_ends(1)!=(0,0) or old['decision']!='CAPPED_UNRESOLVED':
            raise ValueError('endpoint or predecessor control')
        out['pins'].update(base['PINS'])
        base['power_lower']=power_lower
        def mark(label):
            if label=='complete price and terminal limit':
                if out['price']!=old['price'] or out['terminal']!=old['terminal']:
                    raise ValueError('R342 completed price/limit mismatch')
            if label=='both nonroot branches' and out['nonroot']!=old['nonroot']:
                raise ValueError('R342 completed nonroot mismatch')
            snapshot(label)
        base['discover'](out,args.campaign_root,mark)
        out['decision']='ADVANCE_ONE_SIGNED_REPLAY'
    except Exception as exc:
        out['decision']='MISMATCH_OR_UNRESOLVED'
        if 'base' in locals() and 'Rejected' in base and isinstance(exc,base['Rejected']):
            out['decision']='RETIRE_FROZEN_CERTIFICATE'
        out['reason']=str(exc)
    snapshot('child finished')
    print(out['decision'])


if __name__=='__main__':
    main()
