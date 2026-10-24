"""Catalytic transport of main-only ADDs between different coupled frames.
All source originals return unchanged. Checks use rational free-group words,
so different source/destination K maps are never silently identified.
"""
import argparse
import json
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from algebra import need

def normal(word):
    out=[]
    for x in word:
        if out and out[-1]==(x[0],-x[1]):out.pop()
        else:out.append(x)
    return tuple(out)

def plus(a,b,c=1):
    out=dict(a)
    for k,v in b.items():
        q=out.get(k,F())+c*v
        if q:out[k]=q
        else:out.pop(k,None)
    return out

def apply(a,label,sign=1):
    out={}
    for (source,word),v in a.items():
        k=(source,normal(((label,sign),)+word));q=out.get(k,F())+v
        if q:out[k]=q
        else:out.pop(k,None)
    return out

def K(chart,i):return ('Kp' if i<112 else 'Km')+'_'+chart+'_'+str(i if i<112 else i-112)

def frames(ops,bank,chart,sign):
    ops.extend([['mono',bank+i,K(chart,i),sign] for i in range(120)])

def gather(ops,m,dst,src,c,transpose=False):
    for k,row in enumerate(m):
        for i,v in enumerate(row):
            if v:
                d,s=(dst+i,src+k) if transpose else (dst+k,src+i)
                ops.append(['add',d,s,str(c*v)])

def mixed_frames(ops,xbank,hbank,chart,sign):
    ops.extend([['mono',xbank+i,K(chart,i),sign] for i in range(112)])
    ops.extend([['mono',hbank+k,K(chart,112+k),sign] for k in range(8)])

def cross_chart_program(m,a=F(-4),b=F(3),sign=1,query=False):
    ops=[]
    # Source prefix: expose the top 112 rows of H_s. No need to finish H_s.
    frames(ops,0,'s',1)
    ops.extend([['scale',112+k,str(a)] for k in range(8)])
    gather(ops,m,112,0,-F(1,2))
    gather(ops,m,0,112,F(1,2),True)
    frames(ops,0,'s',-1)
    # Add H_t P times this exposed source. Source h is arbitrary dirty
    # workspace; its original (prefix) value cancels from both destinations.
    xbank=240 if query else 0
    if query:
        for i in range(112):
            ops.extend([['clear',240+i],['copy',240+i,i],['H1_inverse',240+i]])
    mixed_frames(ops,xbank,112,'t',1);frames(ops,120,'t',1)
    ops.extend([['add',120+i,xbank+i,str(sign)] for i in range(112)])
    gather(ops,m,112,xbank,F(1,2))
    gather(ops,m,120,112,-sign*F(1,2),True)
    ops.extend([['add',232+k,112+k,str(sign*b)] for k in range(8)])
    gather(ops,m,112,xbank,-F(1,2))
    gather(ops,m,120,112,sign*F(1,2),True)
    ops.extend([['add',232+k,112+k,str(-sign*b)] for k in range(8)])
    mixed_frames(ops,xbank,112,'t',-1);frames(ops,120,'t',-1)
    if query:ops.extend([['clear',240+i] for i in range(112)])
    # Restore the source prefix in its own chart, not the target chart.
    frames(ops,0,'s',1)
    gather(ops,m,0,112,-F(1,2),True)
    gather(ops,m,112,0,F(1,2))
    ops.extend([['scale',112+k,str(1/a)] for k in range(8)])
    frames(ops,0,'s',-1)
    return ops

def same_chart_program(m,a=F(-4),b=F(3),sign=1):
    """Fuse the two chart descriptions when they really are identical."""
    need(a*b==-12,'involutive gauge')
    ops=[];frames(ops,0,'s',1);frames(ops,120,'s',1)
    ops.extend([['add',120+i,i,str(sign)] for i in range(112)])
    ops.extend([['add',232+k,112+k,str(-168*sign)] for k in range(8)])
    gather(ops,m,232,0,-13*b*sign/2)
    gather(ops,m,112,0,F(1,2))
    gather(ops,m,120,112,F(6)*sign,True)
    gather(ops,m,112,0,-F(1,2))
    gather(ops,m,120,112,F(-13*a-12,2)*sign,True)
    frames(ops,0,'s',-1);frames(ops,120,'s',-1)
    return ops

def Z(m,rows,chart):
    out=[]
    for k in range(8):
        row={}
        for i,c in enumerate(m[k]):
            if c:row=plus(row,apply(rows[i],K(chart,i)),F(c,2))
        out.append(apply(row,K(chart,112+k),-1))
    return out

def W(m,rows,chart):
    out=[]
    for i in range(112):
        row={}
        for k in range(8):
            if m[k][i]:row=plus(row,apply(rows[k],K(chart,112+k)),F(m[k][i],2))
        out.append(apply(row,K(chart,i),-1))
    return out

def expected(m,a,b,sign,same,query=False):
    original=[{(i,()):F(1)} for i in range(352 if query else 240)]
    x=original[:112];h=original[112:120]
    wz=W(m,Z(m,x,'s'),'s');wh=W(m,h,'s')
    exposed=[plus(plus(v,z,-1),u,a) for v,z,u in zip(x,wz,wh)]
    if query:exposed=[apply(v,'Q',-1) for v in exposed]
    zt=Z(m,exposed,'s' if same else 't');wzt=W(m,zt,'s' if same else 't')
    target=original[120:240]
    for i in range(112):target[i]=plus(target[i],plus(exposed[i],wzt[i],-1),sign)
    for k in range(8):target[112+k]=plus(target[112+k],zt[k],sign*b)
    return original[:120]+target+([{} for _ in range(112)] if query else [])

def replay(ops,query=False):
    rows=[{(i,()):F(1)} for i in range(352 if query else 240)]
    for e in ops:
        op,i=e[:2]
        if op=='mono':rows[i]=apply(rows[i],e[2],e[3])
        elif op=='scale':rows[i]={k:F(e[2])*v for k,v in rows[i].items()}
        elif op=='clear':
            need(query and 240<=i<352,'clear only owned query fields');rows[i]={}
        elif op=='copy':
            need(query and i>=240 and not rows[i] and e[2]<112,'copy exposed source into owned zero');rows[i]=dict(rows[e[2]])
        elif op=='H1_inverse':
            need(query and i>=240,'Gaussian acts only owned query copy');rows[i]=apply(rows[i],'Q',-1)
        elif op=='add':
            need(i!=e[2],'distinct junction ADD operands')
            rows[i]=plus(rows[i],rows[e[2]],F(e[3]))
        else:raise ValueError(e)
    return rows

def check(m):
    receipts={}
    for name,same in [('different_charts',False),('same_chart',True)]:
        ops=same_chart_program(m) if same else cross_chart_program(m)
        rows=replay(ops);target=expected(m,F(-4),F(3),1,same)
        need(rows==target,'all-column coupled main-only ADD transport '+name)
        counts=dict(Counter(e[0] for e in ops))
        want={'mono':480,'add':2360} if same else {'mono':960,'scale':16,'add':3712}
        need(counts==want,'complete junction invoice '+name)
        receipts[name]={'operation_counts':counts,'arbitrary_input_columns':240,
            'source_originals_restored':120,'new_owned_fields':0,'paid_Gaussian_calls':0,
            'program_payload_sha256':sha256(json.dumps(ops,separators=(',',':')).encode()).hexdigest(),
            'identity':'dst += H_t P H_s src; src unchanged',
            'distinct_free_chart_words':not same}
    query_ops=cross_chart_program(m,query=True)
    need(replay(query_ops,query=True)==expected(m,F(-4),F(3),1,False,True),'all 352 query input columns and owned returns')
    query_counts=dict(Counter(e[0] for e in query_ops))
    need(query_counts=={'mono':960,'scale':16,'add':3712,'clear':224,'copy':112,'H1_inverse':112},'full query wrapper bill')
    receipts['different_chart_thin_query']={
        'operation_counts':query_counts,'arbitrary_input_columns':352,
        'original_input_columns':240,'source_originals_restored':120,
        'owned_query_fields':112,'owned_fields_returned_zero':112,
        'positive_H1_calls':112,'inverse_child_bit_translations':112,
        'total_physical_monomial_maps_including_inverse_lowering':1072,
        'program_payload_sha256':sha256(json.dumps(query_ops,separators=(',',':')).encode()).hexdigest(),
        'identity':'dst += H_t diag(Q^-1,0) H_s src; src unchanged; owned queries cleared',
        'scope':'Keeps 112 existing thin H1 calls; owned stock, COPY/CLEAR, frames and inverse translations explicitly charged. No new query saving.'}
    # A subtraction is the inverse shear, with the same source and unchanged
    # program length. Linearity makes all destination increments negate.
    minus=same_chart_program(m,sign=-1)
    need(replay(minus)==expected(m,F(-4),F(3),-1,True),'subtractive bridge sign')
    ops=cross_chart_program(m);bad=[e[:] for e in ops]
    # A single omitted final source restoration changes an independent input.
    bad.pop(next(i for i,e in enumerate(bad) if e[0]=='scale' and e[-1]=='-1/4'))
    need(replay(bad)!=expected(m,F(-4),F(3),1,False),'omitted catalytic source restoration rejected')
    receipts['controls']=['same chart simplification','different free chart words retained',
        'subtractive bridge','omitted catalytic source restoration rejected']
    receipts['scope']='Universal operator-word junction for declared H_s/H_t blocks. Placement in the full native X/Y/shared-helper interface remains open; local ADD and thin-query consumers are supplied.'
    return receipts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--emit',required=True,type=Path);args=ap.parse_args()
    normalizer=Path(__file__).resolve().parents[1]/'coded-native-caller/NORMALIZERS.json'
    m=json.loads(normalizer.read_text())['mode_columns']
    # Explicit opt-in only; normal package verification never emits programs.
    need(not args.emit.exists(),'refuse to overwrite an existing junction export')
    obj={'different_charts':cross_chart_program(m),'same_chart':same_chart_program(m),
         'different_chart_thin_query':cross_chart_program(m,query=True)}
    args.emit.write_text(json.dumps(obj,separators=(',',':'))+'\n')
    print('EMITTED_COUPLED_ADD_JUNCTIONS',args.emit)

if __name__=='__main__':main()
