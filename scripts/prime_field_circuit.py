"""Exact producer for the retained F3 five-subset network.

The global graph is enumerated by a standard-library C++ checker. Its keys
are full support descriptions, not fingerprints. A second independent pass
checks the replacement templates and every requested boundary value.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
from hashlib import sha256
import json
import struct
import subprocess
import tempfile
from paired_triple_circuit import PairedTriple


def point_orders(h,mode='aligned'):
    if mode!='aligned' or h%2:raise ValueError('Use aligned pairs at even h')
    orders={}
    for C in combinations(range(h),2):
        intact=[(i,i+1) for i in range(0,h,2) if i not in C and i+1 not in C]
        tail=[i for i in range(h) if i not in C and (i^1) in C]
        orders[C]=[i for pair in intact for i in pair]+tail
        assert sorted(orders[C])==[i for i in range(h) if i not in C]
    return orders


def export_local(path,n=26):
    c=PairedTriple(n);result=c.verify()
    total=c.triple(list(range(n)),c.variables)[()]
    assert c.support[total]==(1<<len(c.inputs))-1
    stack=[total]
    while stack:
        x=stack.pop()
        if not x or x in c.active:continue
        c.active.add(x)
        if c.args[x]:stack.extend(c.args[x])
    core={0:(1<<n)-1}
    with path.open('wb') as f:
        def words(*xs):f.write(struct.pack('<'+'I'*len(xs),*xs))
        words(n,len(c.inputs),len(c.support),len(c.active),len(c.outputs)+1)
        for node in sorted(c.active):
            if c.args[node]:
                a,b=c.args[node]
                assert a<node and b<node
                assert not c.support[a]&c.support[b]
                assert c.support[node]==c.support[a]|c.support[b]
                core[node]=core[a]&core[b]
            else:a=b=0;core[node]=sum(1<<i for i in c.inputs[node-1])
            fixed=tuple(i for i in range(n) if core[node]>>i&1);variables=[]
            if c.args[node] and fixed:
                mask=c.support[node]
                while mask:
                    low=mask&-mask;mask-=low
                    t=tuple(x for x in c.inputs[low.bit_length()-1] if x not in fixed)
                    variables.append(t[0]*32+t[1] if len(t)==2 else t[0])
            words(node,a,b,core[node],len(variables),*variables)
        for S,node in c.outputs.items():words(*S,node)
        words(0xffffffff,0xffffffff,0xffffffff,total)
    result['retained_additions']=sum(c.args[x] is not None for x in c.active)
    result['retained_total_exact']=True
    result['binary_sha256']=sha256(path.read_bytes()).hexdigest()
    return result


def optimize(masks):
    """Greedy disjoint CSE, with fully specified tie breaks and exact supports."""
    leaves=sorted({1<<i for mask in masks for i in range(mask.bit_length()) if mask>>i&1})
    terms=[set(x for x in leaves if mask&x) for mask in masks]
    nodes=set(leaves);gates=[]
    while any(len(t)>1 for t in terms):
        freq=Counter(p for t in terms for p in combinations(sorted(t),2))
        a,b=min(freq,key=lambda p:(-freq[p],(p[0]|p[1]).bit_count(),p[0]|p[1],p))
        assert not a&b
        node=a|b
        if node not in nodes:nodes.add(node);gates.append((a,b))
        for t in terms:
            if a in t and b in t:t.remove(a);t.remove(b);t.add(node)
        for t in terms:
            contained=[x for x in t if x&~node==0]
            if len(contained)>1 and sum(contained)==node:
                t.difference_update(contained);t.add(node)
    assert [next(iter(t)) for t in terms]==masks
    return gates


def canonical(core,masks,h=28):
    order=[x for x in range(h) if not core&(1<<x) and not core&(1<<(x^1))]
    order += [x for x in range(h) if not core&(1<<x) and core&(1<<(x^1))]
    assert len(order)==h-4
    return tuple(sorted(sum(1<<j for j,x in enumerate(order) if m>>x&1) for m in masks))


def export_templates(demands,path,h=28):
    cache={};old=new=stars=0
    for line in demands.read_text().splitlines():
        core,before,*masks=map(int,line.split());key=canonical(core,masks,h)
        if key not in cache:cache[key]=optimize(list(key))
        old+=before;new+=len(cache[key]);stars+=1
    with path.open('wb') as f:
        def words(*xs):f.write(struct.pack('<'+'I'*len(xs),*xs))
        words(h,len(cache))
        for targets,gates in sorted(cache.items()):
            words(len(targets),len(gates),*targets)
            for a,b in gates:words(a,b)
    return dict(stars=stars,templates=len(cache),old_additions=old,new_additions=new,
                saved=old-new,sha256=sha256(path.read_bytes()).hexdigest())


def check_global_producer():
    """Rebuild full h28 support count and independently verify all templates.

    Uses about 1.2 GB memory, under 30 MB temporary storage, and a C++17 compiler.
    No large generated graph or machine-specific executable is committed.
    """
    source=Path(__file__).with_name('prime_field_supports.cpp')
    with tempfile.TemporaryDirectory(prefix='prime-field28-') as folder:
        root=Path(folder);binary=root/'check';local=root/'local.bin';demands=root/'demands.txt';templates=root/'templates.bin'
        local_check=export_local(local)
        subprocess.run(['c++','-std=c++17','-O3',str(source),'-o',str(binary)],check=True)
        first=subprocess.run([str(binary),str(local),'-',str(demands)],check=True,capture_output=True,text=True)
        original=json.loads(first.stdout);original.pop('seconds',None)
        replacements=export_templates(demands,templates)
        second=subprocess.run([str(binary),str(local),'-',str(demands),str(templates)],check=True,capture_output=True,text=True)
        repeated,verified=map(json.loads,second.stdout.splitlines());repeated.pop('seconds',None)
        assert original==repeated
        assert verified['role_upper_bound']==11840940
        assert verified['old_star_additions']==replacements['old_additions']
        assert verified['new_star_additions']==replacements['new_additions']
        return dict(local=local_check,global_before_replacement=original,
                    replacements=replacements,independent_template_check=verified)


if __name__=='__main__':
    print(json.dumps(check_global_producer(),indent=2,sort_keys=True))
