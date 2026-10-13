#!/usr/bin/env python3
"""Cancellation-free circuit for all pair sums avoiding two specified points.

Every addition has disjoint input supports. Node interning shares equal sums;
support tracking verifies the full linear map, not sampled input values.
"""
from itertools import combinations
from hashlib import sha256
import json


class ExclusionCircuit:
    def __init__(self,n):
        assert n>=4
        self.n=n
        self.inputs=list(combinations(range(n),2))
        self.support=[0]+[1<<i for i in range(len(self.inputs))]
        self.args=[None]*len(self.support)
        self.lookup={s:i for i,s in enumerate(self.support)}
        self.variables={p:i+1 for i,p in enumerate(self.inputs)}
        _,_,self.outputs=self.pair(list(range(n)))
        self.active=set()
        stack=list(self.outputs.values())
        while stack:
            x=stack.pop()
            if not x or x in self.active:continue
            self.active.add(x)
            if self.args[x]:stack.extend(self.args[x])
        self.additions=sum(self.args[x] is not None for x in self.active)

    def add(self,a,b):
        if not a:return b
        if not b:return a
        assert not self.support[a]&self.support[b], 'Cancellation is forbidden'
        s=self.support[a]|self.support[b]
        if s in self.lookup:return self.lookup[s]
        node=len(self.support)
        self.lookup[s]=node;self.support.append(s);self.args.append((a,b))
        return node

    def total(self,values):
        if not values:return 0
        if len(values)==1:return values[0]
        m=len(values)//2
        return self.add(self.total(values[:m]),self.total(values[m:]))

    def vector(self,values,two=True):
        """Return total, leave-one-out sums, and optional leave-two-out sums."""
        n=len(values)
        if not two:
            prefix=[0]
            for x in values:prefix.append(self.add(prefix[-1],x))
            suffix=[0]*(n+1)
            for i in range(n-1,-1,-1):suffix[i]=self.add(values[i],suffix[i+1])
            return prefix[-1],[self.add(prefix[i],suffix[i+1]) for i in range(n)],{}
        if n<2:return (values[0] if n else 0),[0]*n,{}
        l=n//2
        tl,ul,wl=self.vector(values[:l]);tr,ur,wr=self.vector(values[l:])
        total=self.add(tl,tr)
        one=[self.add(x,tr) for x in ul]+[self.add(tl,x) for x in ur]
        two={ij:self.add(x,tr) for ij,x in wl.items()}
        two.update({(i+l,j+l):self.add(tl,x) for (i,j),x in wr.items()})
        two.update({(i,j+l):self.add(x,y) for i,x in enumerate(ul) for j,y in enumerate(ur)})
        return total,one,two

    def pair(self,points):
        """Pair-input totals after deleting zero, one, or two vertices."""
        n=len(points)
        if n<2:return 0,{i:0 for i in points},{}
        if n==2:
            a,b=points
            return self.variables[a,b],{a:0,b:0},{(a,b):0}
        l=n//2;left=points[:l];right=points[l:]
        tl,ul,wl=self.pair(left);tr,ur,wr=self.pair(right)
        matrix=[[self.variables[a,b] for b in right] for a in left]
        rows=[self.total(row) for row in matrix]
        cols=[self.total(list(col)) for col in zip(*matrix)]
        tc,row_one,row_two=self.vector(rows)
        _,col_one,col_two=self.vector(cols)
        omit_col=[self.vector(row,two=False)[1] for row in matrix]
        omit_both=[self.vector(list(col),two=False)[1] for col in zip(*omit_col)]
        total=self.total([tl,tr,tc]);one={};two={}
        for i,a in enumerate(left):one[a]=self.total([ul[a],tr,row_one[i]])
        for j,b in enumerate(right):one[b]=self.total([tl,ur[b],col_one[j]])
        for (i,j),x in row_two.items():
            two[left[i],left[j]]=self.total([wl[left[i],left[j]],tr,x])
        for (i,j),x in col_two.items():
            two[right[i],right[j]]=self.total([tl,wr[right[i],right[j]],x])
        for i,a in enumerate(left):
            for j,b in enumerate(right):
                two[a,b]=self.total([ul[a],ur[b],omit_both[j][i]])
        return total,one,two

    def verify(self):
        for node in sorted(self.active):
            if self.args[node]:
                a,b=self.args[node]
                assert a<node and b<node
                assert not self.support[a]&self.support[b]
                assert self.support[node]==self.support[a]|self.support[b]
        for (a,b),node in self.outputs.items():
            expected=sum(1<<i for i,p in enumerate(self.inputs) if a not in p and b not in p)
            assert self.support[node]==expected
        encoded=json.dumps({'inputs':self.inputs,
            'nodes':[(i,self.args[i]) for i in sorted(self.active)],
            'outputs':sorted(self.outputs.items())},separators=(',',':')).encode()
        return dict(n=self.n,inputs=len(self.inputs),outputs=len(self.outputs),
                    additions=self.additions,scratch_roles=self.additions+len(self.outputs),
                    nonzero_coefficients=sum(self.support[x].bit_count() for x in self.outputs.values()),
                    all_output_supports_exact=True,all_additions_disjoint=True,
                    circuit_sha256=sha256(encoded).hexdigest())

    def compile(self):
        """Reversible embedding with additions+outputs roles.

        Gates are (input slots, output slots), sharing their first pivot slot.
        All extra output slots are allocated fresh; nonpivot inputs retire.
        """
        users={x:[] for x in self.active}
        for node in sorted(self.active):
            if self.args[node]:
                for pos,x in enumerate(self.args[node]):users[x].append(('gate',node,pos))
        for target,node in sorted(self.outputs.items()):users[node].append(('output',target))
        edge={};source_slots={};output_slots={};gates=[];size=0
        for node in sorted(self.active):
            if self.args[node]:
                ins=(edge[node,0],edge[node,1]);pivot=ins[0]
            else:
                pivot=size;size+=1;ins=(pivot,)
                source_slots[self.inputs[node-1]]=pivot
            assert users[node]
            outs=(pivot,)+tuple(range(size,size+len(users[node])-1))
            size+=len(users[node])-1
            assert len(set(ins))==len(ins) and set(ins)&set(outs)=={pivot}
            gates.append((node,ins,outs))
            for user,slot in zip(users[node],outs):
                if user[0]=='gate':edge[user[1],user[2]]=slot
                else:output_slots[user[1]]=slot
        assert size==self.additions+len(self.outputs)
        return dict(roles=size,gates=gates,sources=source_slots,outputs=output_slots)

    def verify_embedding(self):
        """Check scalar coefficients and both directions' frame support nesting."""
        code=self.compile();gates=code['gates'];size=code['roles']
        values=[0]*size;frames=[0]*size
        for pair,slot in code['sources'].items():
            values[slot]=frames[slot]=self.support[self.variables[pair]]
        for node,ins,outs in gates:
            frame=self.support[node]
            for slot in set(ins+outs):
                assert frames[slot]&~frame==0
                frames[slot]=frame
            for slot in ins[1:]:values[ins[0]]^=values[slot]
            for slot in outs[1:]:values[slot]^=values[ins[0]]
        for pair,slot in code['outputs'].items():
            assert values[slot]==frames[slot]==self.support[self.outputs[pair]]
        descendants={node:0 for node in self.active}
        target_index={pair:i for i,pair in enumerate(sorted(self.outputs))}
        reverse_frames=[0]*size
        for pair,node in self.outputs.items():
            bit=1<<target_index[pair];descendants[node]|=bit
            reverse_frames[code['outputs'][pair]]=bit
        for node in sorted(self.active,reverse=True):
            if self.args[node]:
                for parent in self.args[node]:descendants[parent]|=descendants[node]
        for node,ins,outs in reversed(gates):
            frame=descendants[node]
            assert frame
            for slot in set(ins+outs):
                assert reverse_frames[slot]&~frame==0
                reverse_frames[slot]=frame
        for source,slot in code['sources'].items():
            expected=sum(1<<i for target,i in target_index.items()
                         if not set(source)&set(target))
            assert reverse_frames[slot]==expected
        return dict(reversible_roles=size,forward_coefficient_map_exact=True,
                    forward_support_frames_nested=True,reverse_support_frames_nested=True,
                    no_forbidden_source_target_path=True)


if __name__=='__main__':
    c=ExclusionCircuit(45)
    print(c.verify())
    print('Reversible roles:',c.compile()['roles'])
