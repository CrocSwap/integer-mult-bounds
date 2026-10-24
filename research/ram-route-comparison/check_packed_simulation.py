"""Finite independent controls for fixed-tape packed macro locality/writeback.
These finite Python tests do not certify asymptotic native instruction costs.
"""
from random import Random
import itertools,json

def need(p,m):
    if not p:raise ValueError(m)

def run(table,state,tapes,heads,steps):
    tapes=[list(t) for t in tapes];heads=list(heads);done=0
    for _ in range(steps):
        if state==3:break
        symbols=tuple(tapes[i][heads[i]] for i in range(2))
        nxt,writes,moves=table[state,symbols]
        for i in range(2):
            tapes[i][heads[i]]=writes[i];heads[i]+=moves[i]
        state=nxt;done+=1
    return state,tapes,heads,done

def pack(tape,b):
    return [sum(v<<j for j,v in enumerate(tape[q:q+b])) for q in range(0,len(tape),b)]

def window(blocks,head,b):
    q,off=divmod(head-b,b)
    combined=sum(blocks[q+j]<<(j*b) for j in range(4))
    return (combined>>off)&((1<<(2*b+1))-1)

def replace(blocks,head,b,code):
    q,off=divmod(head-b,b);mask=(1<<(2*b+1))-1
    combined=sum(blocks[q+j]<<(j*b) for j in range(4))
    combined=(combined&~(mask<<off))|(code<<off)
    blocks=blocks.copy()
    for j in range(4):blocks[q+j]=(combined>>(j*b))&((1<<b)-1)
    return blocks

def main():
    rng=Random(20261022);checks=halts=boundary=0
    for machine_seed in range(3):
        mr=Random(machine_seed)
        table={(state,symbols):(mr.randrange(4),tuple(mr.randrange(2) for _ in range(2)),
                                tuple(mr.randrange(-1,2) for _ in range(2)))
               for state in range(3) for symbols in itertools.product(range(2),repeat=2)}
        for b in range(1,5):
            patterns=range(1<<(2*(2*b+1))) if b<=2 else [rng.randrange(1<<(2*(2*b+1))) for _ in range(800)]
            for code in patterns:
                codes=[(code>>(i*(2*b+1)))&((1<<(2*b+1))-1) for i in range(2)]
                for state in range(4):
                    local=[[v>>j&1 for j in range(2*b+1)] for v in codes]
                    entry=run(table,state,local,[b,b],b)
                    newcodes=[sum(v<<j for j,v in enumerate(t)) for t in entry[1]]
                    offsets=(rng.randrange(b),rng.randrange(b))
                    heads=[4*b+offsets[i] for i in range(2)]
                    tapes=[[rng.randrange(2) for _ in range(12*b)] for _ in range(2)]
                    for i in range(2):tapes[i][heads[i]-b:heads[i]+b+1]=local[i]
                    original=[t.copy() for t in tapes]
                    packed=[pack(t,b) for t in tapes]
                    need([window(packed[i],heads[i],b) for i in range(2)]==codes,'window key')
                    for i in range(2):packed[i]=replace(packed[i],heads[i],b,newcodes[i])
                    out=[[blocks[j//b]>>(j%b)&1 for j in range(12*b)] for blocks in packed]
                    actual=run(table,state,tapes,heads,b)
                    delta=[entry[2][i]-b for i in range(2)]
                    need(out==actual[1] and entry[0]==actual[0] and entry[3]==actual[3],'macro simulation')
                    need([heads[i]+delta[i] for i in range(2)]==actual[2],'head displacement')
                    for i in range(2):
                        need(all(out[i][j]==original[i][j] for j in range(12*b)
                                 if not heads[i]-b<=j<=heads[i]+b),'dirty exterior')
                    checks+=1;halts+=entry[0]==3;boundary+=any(o in(0,b-1) for o in offsets)
    print(json.dumps({'status':'PASS_FINITE_PACKED_TM_MACRO_CONTROLS',
                      'macro_cases':checks,'halting_cases':halts,'boundary_offset_cases':boundary,
                      'fixed_tapes':2,'binary_alphabet':True,'macro_lengths':[1,2,3,4],
                      'scope':'Finite exact simulation and masked writeback controls, not universal proof or native runtime evidence.'},indent=2))
if __name__=='__main__':main()
