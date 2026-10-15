#!/usr/bin/env python3
"""Merge equal sums across the common-point circuits, with exact certificates.

Supports are represented by their provenance in the small pair circuit, not
by half a million dense global bit vectors. A sum that occurs in two distinct
common-point groups must be a pair-star; its fixed pair and union of vertices
identify its support exactly.
"""
from hashlib import sha256
from itertools import combinations

from exclusion_circuit import ExclusionCircuit


class SharedPointCircuit:
    def __init__(self,h,circuit=None):
        """Merge equal pair-star sums across common-point groups.

        Tooling note (shared-point / bit-compression replay): the merge/lookup
        loop keeps the historical node-allocation order and output keys, but
        pre-sorts the local active set and output items once, unpacks child
        mappings without a per-node generator, and binds hot attributes locally.
        ``merged_additions``, topology and ``circuit_sha256`` are unchanged.
        See ``research/shared-point-init/``.
        """
        assert h>=6 and h!=9, 'The ambient form I-J/9 must be nondegenerate'
        self.h=h
        self.local=circuit or ExclusionCircuit(h-1)
        assert self.local.n==h-1, 'Pair circuit has the wrong ground size'
        self.inputs=list(combinations(range(h),3))
        self.variables={t:i+1 for i,t in enumerate(self.inputs)}
        nin=len(self.inputs)
        self.args=[None]*(nin+1)
        self.core=[0]+[sum(1<<i for i in t) for t in self.inputs]
        self.union=list(self.core)
        self.provenance=[None]*(nin+1)
        self.points=[[j for j in range(h) if j!=i] for i in range(h)]
        local_inputs=self.local.inputs
        self.pair_ids=[{tuple(points[k] for k in pair):i+1
                       for i,pair in enumerate(local_inputs)} for points in self.points]
        lookup={};self.outputs={};self.merged=0
        local_args=self.local.args
        active_sorted=sorted(self.local.active)
        outputs_items=sorted(self.local.outputs.items())
        variables=self.variables
        core=self.core;union=self.union;args=self.args;provenance=self.provenance
        append_args=args.append;append_core=core.append
        append_union=union.append;append_prov=provenance.append
        for common in range(h):
            mapping={}
            pts=self.points[common]
            bit=1<<common
            for node in active_sorted:
                ab=local_args[node]
                if ab is None:
                    a,b=local_inputs[node-1]
                    mapping[node]=variables[tuple(sorted((common,pts[a],pts[b])))]
                    continue
                a=mapping[ab[0]];b=mapping[ab[1]]
                cval=core[a]&core[b];uval=union[a]|union[b]
                assert cval&bit
                if cval.bit_count()>=2:
                    key=(cval,uval)
                    hit=lookup.get(key)
                    if hit is not None:
                        mapping[node]=hit;self.merged+=1
                        continue
                    new=len(args);mapping[node]=new
                    append_args((a,b));append_core(cval);append_union(uval)
                    append_prov((common,node));lookup[key]=new
                else:
                    new=len(args);mapping[node]=new
                    append_args((a,b));append_core(cval);append_union(uval)
                    append_prov((common,node))
            outs=self.outputs
            for pair,node in outputs_items:
                outs[common,tuple(sorted((common,*(pts[x] for x in pair))))]=mapping[node]
        self.active=set();stack=list(self.outputs.values());active=self.active
        while stack:
            n=stack.pop()
            if n in active:continue
            active.add(n)
            edge=args[n]
            if edge:stack.extend(edge)
        self.additions=sum(args[n] is not None for n in active)

    def support_in(self,node,common):
        """Exact pair-input support in coordinates with this common point.

        Tooling note (shared-point / bit-compression frame replay): results are
        memoized in a per-instance dense table indexed by ``node * h + common``
        instead of a process-wide ``lru_cache(maxsize=16384)``. The historical
        full-size checker (``h=46``) asks for far more than 16384 distinct
        ``(node, common)`` pairs during ``verify_frames``, so the small LRU
        thrashed. Leaf triples and two-point stars unpack pairs without a
        generator or ``sorted`` call. Returned bitmasks are unchanged. See
        ``research/shared-point-frame-contains/``.
        """
        try:
            cache=self._support_in_cache
        except AttributeError:
            cache=[None]*(len(self.args)*self.h)
            self._support_in_cache=cache
        h=self.h
        idx=node*h+common
        hit=cache[idx]
        if hit is not None:
            return hit
        core_row=self.core
        core=core_row[node]
        assert core&(1<<common)
        edge=self.args[node]
        if edge is None:
            a,b,d=self.inputs[node-1]
            if a==common:pair=(b,d) if b<d else (d,b)
            elif b==common:pair=(a,d) if a<d else (d,a)
            else:pair=(a,b) if a<b else (b,a)
            answer=1<<(self.pair_ids[common][pair]-1)
        else:
            old,local=self.provenance[node]
            if old==common:
                answer=self.local.support[local]
            else:
                # This node occurs in two groups, so every triple contains both points.
                assert core.bit_count()==2
                fixed=core&~(1<<common)
                other=fixed.bit_length()-1
                remaining=self.union[node]&~core
                answer=0
                pid=self.pair_ids[common]
                while remaining:
                    bit=remaining&-remaining;remaining-=bit
                    x=bit.bit_length()-1
                    pair=(other,x) if other<x else (x,other)
                    answer|=1<<(pid[pair]-1)
        cache[idx]=answer
        return answer

    def contained(self,a,b):
        """Exact support nesting of node ``a`` inside node ``b``'s span."""
        core=self.core
        core_b=core[b]
        common=(core_b&-core_b).bit_length()-1
        if not core[a]&(1<<common):
            return False
        return not (self.support_in(a,common)&~self.support_in(b,common))

    def verify(self):
        """Exact support nesting and a byte-stable circuit digest.

        Tooling note (shared-point / bit-compression replay): node and partial-
        output digest lines are written with the same UTF-8 text that
        ``json.dumps(..., separators=(',',':'))`` produced historically, but
        without building JSON encoder objects per row. Support checks and
        ``circuit_sha256`` are unchanged. See ``research/shared-point-digest/``.
        """
        self.local.verify()
        digest=sha256()
        update=digest.update
        encode=str.encode
        args=self.args
        provenance=self.provenance
        support_in=self.support_in
        local_support=self.local.support
        core=self.core
        union=self.union
        for node in sorted(self.active):
            edge=args[node]
            if edge:
                a,b=edge;common,local=provenance[node]
                assert a<node and b<node
                A=support_in(a,common);B=support_in(b,common)
                assert not A&B
                assert A|B==local_support[local]
                assert core[node]==core[a]&core[b]
                assert union[node]==union[a]|union[b]
                assert core[node]
                # Byte-identical to json.dumps((node,(a,b),(common,local)),
                # separators=(',',':'))+'\n'
                update(encode(f'[{node},[{a},{b}],[{common},{local}]]\n'))
            else:
                assert core[node]
                # Byte-identical to json.dumps((node,None,None),
                # separators=(',',':'))+'\n'
                update(encode(f'[{node},null,null]\n'))
        points=self.points
        local_outputs=self.local.outputs
        for (common,target),node in sorted(self.outputs.items()):
            excluded=tuple(points[common].index(x) for x in target if x!=common)
            assert support_in(node,common)==local_support[local_outputs[excluded]]
            t0,t1,t2=target
            # Byte-identical to json.dumps((common,target,node),
            # separators=(',',':'))+'\n'
            update(encode(f'[{common},[{t0},{t1},{t2}],{node}]\n'))
        return dict(h=self.h,inputs=len(self.inputs),partial_outputs=len(self.outputs),
                    additions=self.additions,roles=self.additions+len(self.outputs),
                    merged_additions=self.merged,
                    all_additions_disjoint=True,all_partial_outputs_exact=True,
                    every_node_has_common_point=True,circuit_sha256=digest.hexdigest())

    compile=ExclusionCircuit.compile

    def verify_frames(self,code=None):
        """Check all role inclusions; reverse frames are orthogonal complements.

        Tooling note (shared-point / bit-compression frame replay): the nesting
        walk uses the same per-instance dense ``support_in`` table as above, but
        through local closures that bind hot rows once per call. Compile input,
        nesting predicates, and the returned receipt fields are unchanged. See
        ``research/shared-point-frame-contains/``.
        """
        code=code or self.compile()
        h=self.h
        try:
            cache=self._support_in_cache
        except AttributeError:
            cache=[None]*(len(self.args)*h)
            self._support_in_cache=cache
        core=self.core;args=self.args;provenance=self.provenance
        inputs=self.inputs;pair_ids=self.pair_ids
        local_support=self.local.support;union=self.union
        variables=self.variables;outputs=self.outputs

        def support_in(node,common):
            idx=node*h+common
            hit=cache[idx]
            if hit is not None:
                return hit
            c=core[node]
            assert c&(1<<common)
            edge=args[node]
            if edge is None:
                a,b,d=inputs[node-1]
                if a==common:pair=(b,d) if b<d else (d,b)
                elif b==common:pair=(a,d) if a<d else (d,a)
                else:pair=(a,b) if a<b else (b,a)
                answer=1<<(pair_ids[common][pair]-1)
            else:
                old,local=provenance[node]
                if old==common:
                    answer=local_support[local]
                else:
                    assert c.bit_count()==2
                    fixed=c&~(1<<common)
                    other=fixed.bit_length()-1
                    remaining=union[node]&~c
                    answer=0
                    pid=pair_ids[common]
                    while remaining:
                        bit=remaining&-remaining;remaining-=bit
                        x=bit.bit_length()-1
                        pair=(other,x) if other<x else (x,other)
                        answer|=1<<(pid[pair]-1)
            cache[idx]=answer
            return answer

        def contained(a,b):
            cb=core[b]
            common=(cb&-cb).bit_length()-1
            return bool(core[a]&(1<<common)) and not (
                support_in(a,common)&~support_in(b,common))

        frames=[0]*code['roles']
        for triple,slot in code['sources'].items():frames[slot]=variables[triple]
        for node,ins,outs in code['gates']:
            for slot in set(ins+outs):
                prev=frames[slot]
                assert not prev or contained(prev,node)
                frames[slot]=node
        for target,slot in code['outputs'].items():assert frames[slot]==outputs[target]
        # Output target lines enter the complement of these output spans.
        # The exact output relation proved above supplies that orthogonality.
        reverse=[0]*code['roles']
        for target,slot in code['outputs'].items():reverse[slot]=outputs[target]
        for node,ins,outs in reversed(code['gates']):
            for slot in set(ins+outs):
                prev=reverse[slot]
                assert not prev or contained(node,prev)
                reverse[slot]=node
        for triple,slot in code['sources'].items():assert reverse[slot]==variables[triple]
        return dict(roles=code['roles'],forward_frames_nested=True,
                    reverse_complement_frames_nested=True,
                    nondegeneracy='Every source span has a common point; its orthogonal complement is nondegenerate.')

    def program(self):
        code=self.compile();index={t:i for i,t in enumerate(self.inputs)}
        return dict(triples=self.inputs,roles=code['roles'],
                    gates=[(ins,outs) for _,ins,outs in code['gates']],
                    sources=[(index[t],slot) for t,slot in code['sources'].items()],
                    outputs=[(index[t],slot) for (_,t),slot in code['outputs'].items()])


if __name__=='__main__':
    c=SharedPointCircuit(46)
    print(c.verify())
    print(c.verify_frames())
