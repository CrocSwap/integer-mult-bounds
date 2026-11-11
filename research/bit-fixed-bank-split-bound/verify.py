"""Reverse the support census and independently verify the complete paid invoice."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import runpy
from signal import alarm

HERE = Path(__file__).resolve().parent


def dependencies(matrix):
    rows = [[x,1<<i] for i,x in enumerate(matrix)]
    pivot = 0
    for bit in range(max(matrix,default=0).bit_length()):
        q = next((i for i in range(pivot,len(rows)) if rows[i][0]>>bit&1),None)
        if q is None:
            continue
        rows[pivot],rows[q] = rows[q],rows[pivot]
        x,y = rows[pivot]
        for i in range(pivot+1,len(rows)):
            if rows[i][0]>>bit&1:
                rows[i][0] ^= x
                rows[i][1] ^= y
        pivot += 1
    return [m for x,m in rows[pivot:]]


def action(rows,mask):
    y=0
    for i,x in enumerate(rows):
        if mask>>i&1:
            y^=x
    return y


def support(rows,cols,exterior):
    left = dependencies([x&exterior for x in rows])
    if not left:
        return False
    right = dependencies([x&exterior for x in cols])
    if not right:
        return False
    for a in left+[x^y for x,y in combinations(left,2)]:
        c = action(rows,a)
        first = any((a&b).bit_count()%2 for b in right)
        second = any((c&action(cols,b)).bit_count()%2 for b in right)
        if first and second:
            return True
    return False


def census(word, inv):
    n=word['public']
    m=n+word['owned_fields']
    prog=word['program']
    identity = [1<<i for i in range(n)]+[0]*(m-n)
    left=identity.copy()
    orders=list(range(m))
    erased={}
    for t,(op,d,*args) in enumerate(prog):
        if op=='ADD':
            left[d]^=left[args[0]]
        elif op=='SWAP':
            s=args[0]
            for arr in (left,orders):
                arr[d],arr[s]=arr[s],arr[d]
        elif op=='CLEAR':
            erased[t]=left[d]
            left[d]=0
        elif op=='INIT':
            assert left[d]==0
    right=identity.copy()
    owner=orders[:n]+[None]*(m-n)
    frame=word['final']+[None]*(m-n)
    slots=defaultdict(dict)
    support_mask=defaultdict(int)
    for row in inv['helpers']:
        i=row['helper']
        group=row['initial_chart'],row['final_chart']
        support_mask[group] |= 1<<i
        for _,f,_ in row['interior_landings']:
            slots[f][i]=group
    full=(1<<n)-1
    coverage=Counter()
    totals=Counter()
    checked_last=-1
    for t in range(len(prog)-1,-1,-1):
        op,d,*args=prog[t]
        if op=='SWAP':
            changed={frame[d],frame[args[0]]}
        elif op=='MOVE':
            changed=set(args)
        else:
            changed={args[-1]}
        for f in changed:
            groups=set()
            for i,group in slots.get(f,{}).items():
                if owner[i]==i and frame[i]==f:
                    groups.add(group)
                    coverage[i]+=1
            if not groups:
                continue
            checked_last=max(checked_last,t)
            totals['chart_banks']+=1
            bank=[i for i,x in enumerate(frame) if x==f]
            rows=[left[i] for i in bank]
            cols=[right[i] for i in bank]
            for g in groups:
                totals['group_contexts']+=1
                assert not support(rows,cols,full^support_mask[g]), (t,f,g)
        if op=='ADD':
            s,f=args
            assert frame[d]==frame[s]==f and d!=s
            left[d]^=left[s]
            right[s]^=right[d]
        elif op=='SWAP':
            s=args[0]
            for arr in (left,right,frame,owner):
                arr[d],arr[s]=arr[s],arr[d]
        elif op=='MOVE':
            assert frame[d]==args[1]
            frame[d]=args[0]
        elif op=='INIT':
            assert frame[d]==args[0] and not left[d] and owner[d]>=n
            right[d]=0
            frame[d]=owner[d]=None
        else:
            assert op=='CLEAR' and owner[d] is frame[d] is None
            frame[d],owner[d]=args[0],n+t
            left[d]=erased[t]
            right[d]=0
    assert left==identity and frame==word['start']+[None]*(m-n)
    assert owner==list(range(n))+[None]*(m-n)
    return totals,coverage,checked_last


def verify(deps,adapter,receipt):
    own=runpy.run_path(str(HERE/'worker.py'))
    old,word,_,inventory,price=own['authenticate'](deps,adapter)
    support_path=adapter/'frozen/SUPPORT.json'
    assert sha256(support_path.read_bytes()).hexdigest()=='f6be6685471957d4e2bece0b05fa3f433518972325400ed761af00b341f6131c'
    verification=adapter/'verify.py'
    assert sha256(verification.read_bytes()).hexdigest()=='baa4ee28218820e7f5cf3b4f056fc0a7db4a033b80cb62241b9f91aa4febea3c'
    separate=runpy.run_path(str(verification))
    prior=separate['verify'](deps,adapter/'frozen')
    assert prior['paid_lineage_edges']==62474 and prior['rejected_omitted_paid_move']
    totals,coverage,clock=census(word,inventory)
    proof=json.loads((receipt/'PRICE.json').read_bytes())
    assert proof['status']=='COMPLETE' and proof['copies']==36
    assert proof['adapter_relative_pins']==own['ADAPTER'] and proof['dependency_relative_pins']==old['PINS']
    assert proof['stats']==dict(totals) and proof['last_tested_clock']==clock
    assert len(coverage)==proof['covered_pivots']==434
    assert proof['pivot_event_counts']=={str(i):v for i,v in coverage.items()}
    assert not proof['positive_pivots'] and not proof['positive_pivot_credits'] and not proof['unresolved_pivots']
    assert proof['whole_signed_baseline']==price['signed_baseline_interval']
    assert F(proof['whole_stock_saving_upper'])==0
    assert F(proof['whole_target_margin_upper'])==F(price['signed_baseline_interval'][1])<0
    assert str(old['TARGET'])==proof['target'] and not (receipt/'SUPPORT.json').exists()
    assert support([1],[1],0) and not support([1],[1],1)
    return {'status':'PASS_INDEPENDENT_REVERSE_BANK_STOCK','lineage_edges':prior['paid_lineage_edges'],
            'omitted_paid_move_rejected':True,'bank_census':dict(totals),
            'pivots':len(coverage),'target':proof['target'],
            'target_margin_upper':proof['whole_target_margin_upper'],'saving_upper':'0'}


if __name__=='__main__':
    assert __debug__
    p=ArgumentParser(description=__doc__)
    p.add_argument('deps',type=Path)
    p.add_argument('adapter',type=Path)
    p.add_argument('receipt',type=Path)
    a=p.parse_args()
    alarm(60)
    print(json.dumps(verify(a.deps,a.adapter,a.receipt),indent=2,sort_keys=True))
    alarm(0)
