"""Literal seven-grade contact into chart 8 with one subsequent outgoing recode."""
from collections import Counter
from functools import reduce
import gzip,json,operator,sys
from hashlib import sha256
from pathlib import Path


def run(g,change):
    ch=dict(enumerate(g['start']));v={i:1<<i for i in ch};dirty=Counter();edges=Counter();d={int(j):f['dim'] for j,f in g['frames'].items()};source=None;second=None;ops=Counter()
    donors=[2841,2842,2942,2965,2966,2967,3003,3023,3045]
    for k,(op,i,*a) in enumerate(g['program']):
        adds=[]
        if change and 10994<=k<=11013:
            if k!=10994:continue
            rows=[['INIT',3148,1]]+[['ADD',3148,j,1] for j in donors]+[['MOVE',3148,1,8],['INIT',3150,0]]
        elif change and op=='CLEAR' and i==3149:continue
        elif change and op=='CLEAR' and i==3148:rows=[['CLEAR',3148,8]]
        elif change and k==11026:rows=[['ADD',3153,3148,8],[op,i,*a]]
        else:rows=[[op,i,*a]]
        for name,own,*args in rows:
            ops[name]+=1
            if name=='INIT':assert own not in ch;ch[own]=args[0];v[own]=0
            elif name=='CLEAR':assert ch.pop(own)==args[0];dirty['nonzero' if v.pop(own) else 'zero']+=1
            elif name=='ADD':s,c=args;assert ch[own]==ch[s]==c;v[own]^=v[s]
            elif name=='MOVE':
                s,t=args;assert ch[own]==s;ch[own]=t;edges[abs(d[s]-d[t])]+=1
                if (change and own==3148 and s==1) or (not change and k==11013):source=v[own]
                if k==11026:second=v[own]
            elif name=='SWAP':s,=args;ch[own],ch[s]=ch[s],ch[own];v[own],v[s]=v[s],v[own]
            else:raise ValueError(name)
    assert ch==dict(enumerate(g['final']))
    return v,source,second,dirty,edges,ops


def rank(rows):
    b={}
    for r in rows:
        while r:
            p=r.bit_length()
            if p not in b:b[p]=r;break
            r^=b[p]
    return len(b)


def control(g):
    old,f,h,d,e,ops=run(g,False);new,received,coded,dd,ee,newops=run(g,True);assert received==f and coded==h^f
    diff=[i for i in old if new[i]!=old[i]];assert diff and all((old[i]^new[i])==f for i in diff)
    assert [old[i] for i in range(630)]==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)] and rank(old.values())==630;changed_rank=rank(new.values());assert changed_rank==630 and len(diff)==54;assert (e-ee)==Counter({1:1,2:1,4:1}) and ee-e==Counter({7:1})
    return {'deleted_chain_move_clocks':[10997,11002,11013],'new_receiver_chart':8,'physical_top_sending_owners':[2841,2842,2942,2965,2966,2967,3003,3023,3045],'full_native_message_delivered_at_line':True,'changed_chart8_departure_original_clock':11026,'changed_departure_equals_XOR_of_both_native_completed_returns':True,'rank_of_630_changed_rows':changed_rank,'wrong_output_count':len(diff),'wrong_output_ids':diff,'symbolically_nonzero_dirty_clears':dd['nonzero'],'symbolically_zero_private_clears':dd['zero'],'paid_change':{'removed':dict(e-ee),'inserted':dict(ee-e)},'changed_opcode_counts':dict(newops)}

if __name__=='__main__':
    data=Path(sys.argv[1]).read_bytes();assert sha256(data).hexdigest()=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
    print(json.dumps(control(json.loads(gzip.decompress(data))),sort_keys=True,indent=2))
