"""Replay portable calibrated rational births from a canonical word and layout.

The source lock supplies the ordinary Python PR 7776 scalar-edit and graph
locality engines. The endpoint, journal, inventory and canonical byte checks
in this file also run on compressed input or output words.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def read(path):
    value=path.read_bytes()
    if value.startswith(b'\x1f\x8b'):
        value=gzip.decompress(value)
    return json.loads(value)


def decode(Net,word):
    return Net(word['first_output'],list(word['initial']),list(word['final']),
               {k:(a,b) for k,a,b in word['moves']},
               {k:{d:Q(c) for d,c in row} for k,row in word['forms']})


def encode(graph,frames):
    return dict(frames=frames,initial=graph.initial,final=graph.final,first_output=graph.first_output,
                moves=[[k,a,b] for k,(a,b) in sorted(graph.moves.items())],
                forms=[[key,[[i,str(q)] for i,q in sorted(row.items())]] for key,row in sorted(graph.forms.items())],
                schedule=graph.schedule())


def span(frame):
    values={0}
    for axis in frame:
        require(0<axis<512 and axis not in values,'independent nine-axis chart')
        values|={axis^i for i in values}
    return values


def target_operator(layout,n):
    rows=[{i:Q(1)} for i in range(n)]
    mains=set()
    hosted=set(layout['hosted']['Dports'])
    for i,x in enumerate(layout['live']):
        y=x+112
        mains.update([x,y])
        if i in hosted:
            rows[y][x]=Q(1)
        else:
            rows[x][y]=Q(-1)
            rows[y]={x:Q(1,2),y:Q(1,2)}
    for x,y in zip(layout['hosted']['X2'],layout['hosted']['Y2'],strict=True):
        rows[x][y]=Q(-1)
        mains.update([x,y])
    require(len(mains)==400,'all main ports')
    return rows,mains


def transpose(rows):
    answer=[{} for row in rows]
    for i,row in enumerate(rows):
        for j,val in row.items():
            answer[j][i]=val
    return answer


def tally(net,frames,mains):
    spaces=[span(f) for f in frames]
    p,t=Counter(),Counter()
    for a,b in net.moves.values():
        require(spaces[a]<spaces[b] or spaces[b]<spaces[a],'nested charged route')
        p[abs(len(frames[a])-len(frames[b]))]+=1
    for i,(a,b) in enumerate(zip(net.initial,net.final,strict=True)):
        if i not in mains:
            require(spaces[a]<spaces[b],'positive productive target')
            t[len(frames[b])-len(frames[a])]+=1
    return {'paid':p,'targets':t}


def operator_check(net,expected):
    values={~i:(1,{i:1}) for i in range(len(net.initial))}
    for node in net.schedule():
        parts=[(d*q.denominator,row,q.numerator) for move,q in net.forms[node].items()
               for d,row in (values[move],) if row]
        den=lcm(*(d for d,_,_ in parts))
        result={}
        for d,row,n in parts:
            k=n*(den//d)
            for i,v in row.items():
                result[i]=result.get(i,0)+k*v
        result={i:v for i,v in result.items() if v}
        divisor=gcd(den,*result.values())
        if node in net.moves:
            values[node]=(den//divisor,{i:v//divisor for i,v in result.items()})
        else:
            got={i:Q(s,den) for i,s in result.items()}
            want=expected[node-net.first_output]
            if got!=want:
                return node-net.first_output
    return None


def edit(net,step,split,fault=None):
    reverse=step['reverse']
    work=net.transpose() if reverse else type(net)(net.first_output,list(net.initial),list(net.final),
                                                dict(net.moves),{i:dict(row) for i,row in net.forms.items()})
    event=step['event']
    for change in step['paid_subdivisions']:
        e,s,mid=change['old_key'],change['new_key'],change['chart']
        require(e in work.moves and s not in work.forms and 0<=s<work.first_output,'paid identities')
        a,b=work.moves[e]
        require([a,b]==change['old_charts'],'paid route preimage')
        work.moves[s]=(a,mid)
        work.moves[e]=(mid,b)
        work.forms[s]=work.forms[e]
        work.forms[e]={s:Q(1)}
    fresh=len(work.initial)
    result=split(work,{**event,**({'pulse':[]} if fault=='no_pulse' else {})})
    result.initial[fresh]=event.get('fresh_source_chart',event['split_chart'])
    if fault=='fresh_into_old' and result.initial[fresh]==event['split_chart']:
        result.forms[result.first_output+event['role']][~fresh]=Q(1)
    return result.transpose() if reverse else result


def write_pair(directory, word, layout):
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in [('WORD', word), ('LAYOUT', layout)]:
        (directory / f'{name}.json.gz').write_bytes(gzip.compress(canonical(data), mtime=0))


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--supplier',type=Path,required=True,help='source-locked p104-dual-supplier-lift directory')
    for key in ('word','layout','journal','out'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--faults',action='store_true')
    p.add_argument('--checkpoint',type=Path,help='write the result after the second birth')
    args=p.parse_args()
    supplier=args.supplier.resolve()/'complex'
    sys.path[:0]=[str(supplier),str(supplier/'retained'/'vendor')]
    from network import Network
    from birth_event import apply_split
    raw,layout,journal=read(args.word),read(args.layout),read(args.journal)
    source=journal['source']
    require(digest(raw)==source['word_sha256'] and digest(layout)==source['layout_sha256'] and raw['frames']==layout['frames'],
            'compressed source and layout pins')
    g=decode(Network,raw)
    frames=raw['frames']
    expected,mains=target_operator(layout,len(g.initial))
    require(operator_check(g,expected) is None and operator_check(g.transpose(),transpose(expected)) is None,
            'exact source forward and adjoint')
    results=[]
    for index, step in enumerate(journal['steps'],1):
        prior=tally(g,frames,mains)
        n=len(g.initial)
        protected={i:(a,b) for i,(a,b) in enumerate(zip(g.initial,g.final,strict=True)) if i!=step['event']['role']}
        frames=frames+step.get('added_frames',[])
        target=expected+[{n:Q(1)}]
        changed=edit(g,step,apply_split)
        require(all((changed.initial[i],changed.final[i])==pair for i,pair in protected.items()),
                'unchanged endpoint pairs for every other old owner')
        require(operator_check(changed,target) is None and operator_check(changed.transpose(),transpose(target)) is None,
                'full enlarged forward and adjoint operators')
        width=max(max(abs(q.numerator).bit_length(),q.denominator.bit_length())
                  for k,row in changed.forms.items() if row!=g.forms.get(k) for q in row.values())
        require(width<=24,'padded scalar width')
        controls={}
        if args.faults:
            faults=['no_pulse']
            if step['event'].get('fresh_source_chart',step['event']['split_chart'])==step['event']['split_chart']:
                faults.append('fresh_into_old')
            for name in faults:
                fault=edit(g,step,apply_split,name)
                found=[operator_check(fault,target),operator_check(fault.transpose(),transpose(target))]
                require(all(x is not None for x in found),'negative control rejected in both orientations')
                controls[name]=found
        after=tally(changed,frames,mains)
        paid_delta={field:{rank:after[field].get(rank,0)-prior[field].get(rank,0)
                           for rank in after[field].keys()|prior[field].keys()
                           if after[field].get(rank,0)!=prior[field].get(rank,0)} for field in ('paid','targets')}
        word=encode(changed,frames)
        new_layout=dict(layout,frames=frames,public=n+1,source_labels=layout['source_labels']+[max(layout['source_labels'])+1])
        require(digest(word)==step['word_sha256'] and digest(new_layout)==step['layout_sha256'],'ordered step output pins')
        require({kind:{str(r):v for r,v in table.items()} for kind,table in paid_delta.items()}==step['native_delta'],
                'both sides of the actual native invoice move')
        results.append(dict(word_sha256=digest(word),layout_sha256=digest(new_layout),owners=n+1,
                            coefficients_each_direction=(n+1)**2,controls=controls,max_altered_scalar_bits=width,
                            native_delta=paid_delta))
        if args.checkpoint is not None and index == 2:
            write_pair(args.checkpoint, word, new_layout)
        g,layout,expected=changed,new_layout,target
    write_pair(args.out, word, layout)
    (args.out/'REPLAY.json').write_text(json.dumps(dict(source=source,steps=results),indent=2,sort_keys=True)+'\n')
    print('PASS',results[-1]['word_sha256'],results[-1]['owners'],flush=True)


if __name__=='__main__':
    main()
