#!/usr/bin/env python3
"""Exact source-bound block identities and complete ordinary accounting."""
import copy,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import fusion

def need(ok,message):
    if not ok:raise ValueError(message)

def split(events):
    blocks=[[]];separators=[]
    for e in events:
        if e[0] in ('ADD','SCALE','SWAP'):blocks[-1].append(e)
        else:separators.append(e);blocks.append([])
    return blocks,separators

def pullback(events,output,n):
    """Reverse row-functional propagation, independent of the generator."""
    row=[int(j==output) for j in range(n)]
    for e in reversed(events):
        if e[0]=='ADD':row[e[2]]+=int(Q(e[3]))*row[e[1]]
        elif e[0]=='SCALE':row[e[1]]*=int(Q(e[2]))
        elif e[0]=='SWAP':row[e[1]],row[e[2]]=row[e[2]],row[e[1]]
        else:raise ValueError('nonconstant event in pullback')
    return row

def alphabet(caller,limit):
    n=caller['roles']
    for e in caller['events']:
        o=e[0]
        need(o in ('ADD','SCALE','SWAP','LAMBDA','HOST2','IDLE_ONE','QUERY'),'operation alphabet')
        if o in ('ADD','SWAP'):
            need(0<=e[1]<n and 0<=e[2]<n and e[1]!=e[2],'ordinary roles')
        if o=='ADD':
            c=Q(e[3]);need(c.denominator==1 and 0<abs(c)<=limit,'bounded integer ADD')
        if o=='SCALE':need(0<=e[1]<n and Q(e[2])==-1,'unit SCALE minus one')

def equivalent(before,after):
    alphabet(before,3);alphabet(after,3)
    need({k:v for k,v in before.items() if k!='events'}=={k:v for k,v in after.items() if k!='events'},'all caller metadata unchanged')
    old,os=split(before['events']);new,ns=split(after['events'])
    need(os==ns,'nonconstant sequence unchanged')
    need(len(old)==len(new),'same block boundaries')
    changed=0;equations=0
    for a,b in zip(old,new):
        if a==b:continue
        changed+=1
        for output in range(before['roles']):
            need(pullback(a,output,before['roles'])==pullback(b,output,before['roles']),'all-input ordinary block matrix')
            equations+=before['roles']
    return changed,equations

def raw_rest(c):
    roles=c['roles'];events=c['events'];main_maps=idle_maps=query_maps=0
    def swaps(sel):return len(set(sel)-set(range(len(sel))))
    for qp,zero,*stages in c['diagonal']:
        axes=([0] if qp else [])+[a for k,bit in enumerate(stages,1) if bit for a in range(9+8*(k-1),9+8*k)]
        main_maps+=104*(2*swaps(axes)+2*bool(qp)+int(qp==-1))
    for e in events:
        if e[0]=='IDLE_ONE':idle_maps+=208*swaps([a for k in e[2] for a in range(9+8*(k-1),9+8*k)])
        elif e[0]=='QUERY':query_maps+=104*(2+int(e[3]==-1))
    parts={'caller_envelope':32*roles*104*len(events),'thin':16*104*sum(e[0]=='QUERY' for e in events),
           'output_rows':26*roles*104,'main_adapters':1000*main_maps,'idle_adapters':1000*idle_maps,'query_adapters':1000*query_maps}
    return parts,sum(parts.values())

def reject(fn,label):
    try:fn()
    except (ValueError,IndexError,KeyError):return label
    raise ValueError('negative control accepted: '+label)

def growth(c):
    adds=Counter(abs(int(Q(e[3]))) for e in c['events'] if e[0]=='ADD')
    other=sum(e[0] in ('LAMBDA','HOST2','QUERY') for e in c['events'])
    product=2**other
    for a,count in adds.items():product*=(1+a)**count
    lambdas=sum(e[0]=='LAMBDA' for e in c['events'])
    # Per complex coordinate: |a| additions for y += a*x, two real
    # negations for SCALE, six real copies for SWAP.
    literal=sum(2*a*count for a,count in adds.items())+2*sum(e[0]=='SCALE' for e in c['events'])+6*sum(e[0]=='SWAP' for e in c['events'])
    blocks,_=split(c['events']);max_norm=max_entry=1
    for block in blocks:
        rows=[[int(i==j) for j in range(c['roles'])] for i in range(c['roles'])]
        for e in block:
            if e[0]=='ADD':
                q=int(Q(e[3]));rows[e[1]]=[a+q*b for a,b in zip(rows[e[1]],rows[e[2]])]
            elif e[0]=='SCALE':rows[e[1]]=[-a for a in rows[e[1]]]
            elif e[0]=='SWAP':rows[e[1]],rows[e[2]]=rows[e[2]],rows[e[1]]
            max_norm=max(max_norm,max(sum(map(abs,row)) for row in rows))
            max_entry=max(max_entry,max(abs(a) for row in rows for a in row))
    return {'add_absolute_counts':dict(sorted(adds.items())),'coefficient_norm_bound_integer':str(product),
            'coefficient_norm_strict_power_two':product.bit_length(),'denominator_divides_power_two':lambdas,
            'constant_scalar_work_per_complex_coordinate':literal,'largest_constant_block_prefix_row_sum':max_norm,
            'largest_constant_block_prefix_entry':max_entry}

def main():
    before=json.loads((HERE/'data/caller-before.json').read_text())
    after=json.loads((HERE/'data/caller-after.json').read_text())
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for item in sources['retained']:
        need(hashlib.sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256'],'frozen source hash')
    proposed,records=fusion.run(before)
    need(proposed==after,'exact deterministic regeneration')
    changed,equations=equivalent(before,after);alphabet(after,2)
    need((changed,equations)==(38,60800),'all changed blocks checked independently')
    need((len(before['events']),len(after['events']))==(2492,1194),'event counts')
    oldparts,oldrest=raw_rest(before);newparts,newrest=raw_rest(after)
    need(oldrest==783421184 and newrest==610631424,'complete unchanged-interface ordinary invoice')
    need(oldrest-newrest==172789760,'raw work saving')
    need({k:v for k,v in oldparts.items() if k!='caller_envelope'}=={k:v for k,v in newparts.items() if k!='caller_envelope'},'all other raw terms unchanged')
    og,ng=growth(before),growth(after)
    need(og['constant_scalar_work_per_complex_coordinate']==9576 and ng['constant_scalar_work_per_complex_coordinate']==4108,'explicit constant scalar work')
    need(og['coefficient_norm_strict_power_two']==2057 and ng['coefficient_norm_strict_power_two']==784,'fresh formal coefficient growth')
    need(og['denominator_divides_power_two']==ng['denominator_divides_power_two']==124,'denominator bound unchanged')
    need(int(ng['coefficient_norm_bound_integer'])<int(og['coefficient_norm_bound_integer']),'fresh growth bound improves')
    print('PASS 38 changed40x40 block identities:',equations,'exact scalar equalities')
    print('PASS nonconstant sequence, metadata, roles and recursive invoice unchanged')
    print('PASS events2492->1194; raw ordinary saving172789760')
    print('PASS scalar work9576->4108 per complex coordinate; growth<2^2057 -> <2^784; denominator divides2^124')
    print('PREFIX_BOUNDS',json.dumps({label:{k:v for k,v in data.items() if k!='coefficient_norm_bound_integer'} for label,data in [('before',og),('after',ng)]},sort_keys=True))
    controls=[]
    bad=copy.deepcopy(after);j=next(j for j,e in enumerate(bad['events']) if e[0]=='ADD');bad['events'][j][3]=str(-Q(bad['events'][j][3]))
    controls.append(reject(lambda:equivalent(before,bad),'wrong ADD sign'))
    bad=copy.deepcopy(after);del bad['events'][next(j for j,e in enumerate(bad['events']) if e[0]=='ADD')]
    controls.append(reject(lambda:equivalent(before,bad),'deleted constant gate'))
    bad=copy.deepcopy(after);j=next(j for j,e in enumerate(bad['events']) if e[0]=='SCALE');bad['events'][j][2]='1'
    controls.append(reject(lambda:equivalent(before,bad),'wrong unit scaling'))
    bad=copy.deepcopy(after);j=next(j for j,e in enumerate(bad['events']) if e[0]=='HOST2');bad['events'][j][-1]+=1
    controls.append(reject(lambda:equivalent(before,bad),'changed native boundary role'))
    bad=copy.deepcopy(after);bad['events']=[['ADD',0,1,'4'],['ADD',0,1,'-4']]+bad['events']
    controls.append(reject(lambda:equivalent(before,bad),'endpoint-preserving oversized alphabet'))
    print('PASS negative controls:',', '.join(controls))
    print('PASS_CALLER_CONSTANT_BLOCKS')

if __name__=='__main__':main()
