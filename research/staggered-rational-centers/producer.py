"""Staggered dual-paired rational-center complex producer at h=24, d=24.

Copyright 2026 Thomas Marchand, Apache-2.0. Prepared with Google Antigravity
assistance. Adapted from scripts/stopped_product/complex.py (Copyright 2026
icekylinx, PR #104) and research/reversed-rational-centers/producer.py
(Copyright 2026 Rohan Arun, PR #107), using the credited PairedTriple circuit.
"""
import json, struct, array
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from partial_swap.binary import write_array
from paired_triple_circuit import PairedTriple


class StaggeredPairedTriple(PairedTriple):
    def rtotal(self, values):
        values = [x for x in values if x]
        values.reverse()
        res = 0
        for x in values:
            res = self.add(res, x)
        return res

    def block_vector(self, values):
        n = len(values)
        if n >= 3 and values[0] == 0:
            st, one_nz, _ = self.block_vector(values[1:])
            return st, [st] + one_nz, {}
        prefix = [0] * (n + 1)
        for i in range(n):
            if i % 2 == 0:
                prefix[i + 1] = self.add(prefix[i], values[i])
            else:
                p = self.add(values[i - 1], values[i])
                prefix[i + 1] = self.add(prefix[i - 1], p)
        suffix = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            if i % 2 == 1 and i + 1 < n:
                q = self.add(values[i], values[i + 1])
                suffix[i] = self.add(q, suffix[i + 2])
            else:
                suffix[i] = self.add(values[i], suffix[i + 1])
        return prefix[n], [self.add(prefix[i], suffix[i + 1]) for i in range(n)], {}

    def vector(self, values, two=True):
        if not two:
            if len(values) < 11:
                return self.block_vector(values)
            vals = values[1:]
            n = len(vals)
            prefix = [0] * (n + 1)
            for i in range(n):
                prefix[i + 1] = self.add(prefix[i], vals[i])
            suffix = [0] * (n + 1)
            for i in range(n - 1, -1, -1):
                if i % 2 == 1 and i + 1 < n:
                    suffix[i] = self.add(self.add(vals[i], vals[i + 1]), suffix[i + 2])
                else:
                    suffix[i] = self.add(vals[i], suffix[i + 1])
            st = prefix[n]
            return st, [st] + [self.add(prefix[i], suffix[i + 1]) for i in range(n)], {}
        return super().vector(values, two=two)

    def triple(self, pts, w):
        subsets = [s for k in range(4) for s in combinations(pts, k)]
        if len(pts) <= self.base:
            return {s: self.total([v for t, v in w.items() if not set(s) & set(t)]) for s in subsets}
        groups = self.grouping(pts); ng = len(groups)
        group_of = {u: i for i, g in enumerate(groups) for u in g}
        coarse_parts = defaultdict(list)
        for t, v in w.items(): coarse_parts[tuple(sorted({group_of[u] for u in t}))].append(v)
        coarse = {s: self.rtotal(xs) for s, xs in coarse_parts.items()}
        out_coarse = self.triple(list(range(ng)), coarse)
        one = {}
        for u in pts:
            g = group_of[u]; others = [j for j in range(ng) if j != g]
            pieces = defaultdict(list)
            for t, v in w.items():
                if u not in t: continue
                rest = [a for a in t if a != u]
                if any(group_of[a] == g for a in rest): continue
                pieces[tuple(sorted({group_of[a] for a in rest}))].append(v)
            coeff = {s: self.rtotal(xs) for s, xs in pieces.items()}
            edges = {s: coeff.get(s, 0) for s in combinations(others, 2)}
            weights = {j: coeff.get((j,), 0) for j in others}
            total, single, pair = self.block(others, edges, weights)
            const = coeff.get((), 0)
            one[u] = {(): self.add(const, total)}
            one[u].update({(j,): self.add(const, x) for j, x in single.items()})
            one[u].update({s: self.add(const, x) for s, x in pair.items()})
        two = {}
        for u, v in combinations(pts, 2):
            i, j = group_of[u], group_of[v]
            if i == j: continue
            others = [k for k in range(ng) if k not in (i, j)]
            vals = [self.total([w.get(tuple(sorted((u, v, a))), 0) for a in groups[k]]) for k in others]
            total, leave, _ = self.vector([w.get((u, v), 0)] + vals, False)
            two[u, v] = {(): total} | {(k,): x for k, x in zip(others, leave[1:])}
        result = {}
        for excluded in subsets:
            E = set(excluded); G = tuple(sorted({group_of[a] for a in E}))
            survivors = [u for i in G for u in groups[i] if u not in E]
            assert len(survivors) <= 3
            pieces = {(): out_coarse[G]}
            for u in survivors:
                omit = tuple(i for i in G if i != group_of[u])
                pieces[u,] = one[u][omit]
            for u, v in combinations(survivors, 2):
                omit = tuple(i for i in G if i not in (group_of[u], group_of[v]))
                pieces[u, v] = two[u, v][omit]
            if len(survivors) == 3: pieces[tuple(survivors)] = w.get(tuple(survivors), 0)
            if len(survivors) == 3:
                a, b, c = survivors
                order = [(), (a,), (b,), (a, b), (c,), (a, c), (b, c), (a, b, c)]
            else: order = [s for k in range(len(survivors) + 1) for s in combinations(survivors, k)]
            result[excluded] = self.total([pieces[s] for s in order])
        return result

    def block(self, points, edges, weights):
        bt = self.rtotal
        if len(points) <= 2:
            total = lambda omit: bt([x for p, x in edges.items() if not set(p) & set(omit)] + [x for p, x in weights.items() if p not in omit])
            return total(()), {a: total((a,)) for a in points}, {(a, b): total((a, b)) for a, b in combinations(points, 2)}
        groups = self.grouping(points); ng = len(groups); e = lambda a, b: edges[tuple(sorted((a, b)))]
        coarse = {(i, j): bt([e(a, b) for a in groups[i] for b in groups[j]]) for i, j in combinations(range(ng), 2)}
        wt = {i: bt([weights[a] for a in g] + [e(a, b) for a, b in combinations(g, 2)]) for i, g in enumerate(groups)}
        total, outside, far = self.block(list(range(ng)), coarse, wt)
        strips = {}; sums = {}
        for i, g in enumerate(groups):
            other = [j for j in range(ng) if j != i]
            for a in g:
                carry = bt([weights[u] for u in g if u != a])
                vals = [bt([e(u, v) for u in g if u != a for v in groups[j]]) for j in other]
                st, one, _ = self.block_vector([carry] + vals)
                strips[a] = {j: z for j, z in zip(other, one[1:])}; sums[a] = st
        out = {}; single = {a: self.add(outside[i], sums[a]) for i, g in enumerate(groups) for a in g}
        for i, g in enumerate(groups):
            for a, b in combinations(g, 2): out[a, b] = outside[i]
        for i, j in combinations(range(ng), 2):
            for a in groups[i]:
                left = self.add(far[i, j], strips[a][j])
                for b in groups[j]:
                    cross = bt([e(u, v) for u in groups[i] if u != a for v in groups[j] if v != b])
                    out[a, b] = self.add(left, self.add(strips[b][i], cross))
        return total, single, out


def build(h, prefix, central_disjoint, base=2):
    assert (h, central_disjoint, base) == (24,24,2)
    d=central_disjoint
    assert 0<d<=h
    divisor=abs(3-d)
    assert divisor == 21
    triples=list(combinations(range(h),3)); v=len(triples)
    args=[(0,0)]; support=[0]; core=[0]; cover=[0]; types=[0]; ranks=[0]
    lookup={}; inputs={}; center_coeff={}
    # Each central tree adds h-1 ordinary pair totals, so every intermediate
    # coefficient is at most h-1. Wider lanes rule out hidden integer carries.
    coefficient_bits=h.bit_length()
    def packed(mask):
        result=0
        while mask:
            bit=mask&-mask; mask-=bit
            result |= 1 << (coefficient_bits*(bit.bit_length()-1))
        return result
    for j,t in enumerate(triples):
        mask=sum(1<<a for a in t); x=len(args); inputs[t]=x
        args.append((0,0));support.append(1<<j);core.append(mask);cover.append(mask)
        types.append(1);ranks.append(1);lookup[1<<j]=x
    def add(a,b,center=None):
        if not a:return b
        if not b:return a
        if center is None:
            assert not support[a]&support[b], "Ordinary additions must be cancellation-free"
        s=support[a]|support[b]
        if center is None and s in lookup:return lookup[s]
        x=len(args);args.append((a,b));support.append(s)
        core.append(core[a]&core[b]);cover.append(cover[a]|cover[b])
        if center is not None:
            types.append(3);ranks.append(h-1);core[x]=1<<center
            ca=center_coeff[a] if a in center_coeff else packed(support[a])
            cb=center_coeff[b] if b in center_coeff else packed(support[b])
            center_coeff[x]=ca+cb
        elif core[x].bit_count()>=2:
            types.append(1);ranks.append(s.bit_count());lookup[s]=x
        else:
            types.append(2);ranks.append(cover[x].bit_count());lookup[s]=x
        return x
    def total(xs,center=None):
        xs=[x for x in xs if x]
        while len(xs)>1:
            xs=[add(xs[i],xs[i+1],center) if i+1<len(xs) else xs[i] for i in range(0,len(xs),2)]
        return xs[0] if xs else 0
    paired=StaggeredPairedTriple(h,base)
    allresults=paired.triple(list(range(h)),paired.variables)
    selected=list(paired.outputs.values())+[allresults[(i,)] for i in range(d)]
    active=set();stack=list(selected)
    while stack:
        x=stack.pop()
        if not x or x in active:continue
        active.add(x)
        if paired.args[x]:stack.extend(paired.args[x])
    mapping={0:0}|{j+1:inputs[t] for j,t in enumerate(triples)}
    for x in sorted(active):
        if paired.args[x]:
            a,b=paired.args[x];mapping[x]=add(mapping[a],mapping[b])
    roots=[mapping[paired.outputs[t]] for t in triples];kind=[0]*v
    center_disjoint_roots=[mapping[allresults[(i,)]] for i in range(d)]
    del paired, mapping, active, allresults
    pairtotals={}; pair_outputs={}
    point_masks=[sum(1<<j for j,t in enumerate(triples) if a in t) for a in range(h)]
    full_support=(1<<v)-1
    for t,node in zip(triples,roots):
        assert support[node] == full_support & ~(point_masks[t[0]]|point_masks[t[1]]|point_masks[t[2]])
        target_mask=sum(1<<a for a in t)
        if types[node]==2:
            assert not cover[node]&target_mask
        else:
            assert types[node]==1
            assert not support[node]&(point_masks[t[0]]^point_masks[t[1]]^point_masks[t[2]])
    for i,node in enumerate(center_disjoint_roots):
        assert support[node] == full_support & ~point_masks[i]
        assert types[node]==2 and cover[node]==((1<<h)-1)^(1<<i)
        assert ranks[node]==h-1
    for a,b in combinations(range(h),2):
        others=[i for i in range(h) if i not in (a,b)]
        others.sort(key=lambda i:((i^1) in (a,b),-i))
        w=[inputs[tuple(sorted((a,b,i)))] for i in others]
        pre=[0]
        for idx_w,x in enumerate(w):
            if (a^1)==b and idx_w%2==1 and idx_w<20:
                pre.append(add(pre[-2],add(w[idx_w-1],x)))
            else:
                pre.append(add(pre[-1],x))
        suf=[0]*(len(w)+1)
        for j in range(len(w)-2,-1,-2):
            suf[j+1]=add(w[j+1],suf[j+2]);suf[j]=add(add(w[j],w[j+1]),suf[j+2])
        q20=add(pre[19],w[20])
        for j,i in enumerate(others):
            if (a^1)!=b and 2<=j<18 and (i//2<a//2 or (j//2)%2==0):
                jj=j&-2
                node=add(add(pre[jj],suf[jj+2]),w[jj^(1-(j&1))])
            elif j==19:
                node=add(q20,w[21])
            elif j==21:
                node=add(q20,w[19])
            elif j==20 or ((a^1)==b and j>=4 and j%2==0):
                node=add(pre[j-2],add(add(w[j-2],w[j-1]),suf[j+1]))
            else:
                node=add(pre[j],suf[j+1])
            roots.append(node);kind.append(0)
            pair_outputs[a,b,i]=node
            assert support[node] == point_masks[a]&point_masks[b]&~point_masks[i]
            assert types[node]==1
            assert not support[node]&(point_masks[a]^point_masks[b]^point_masks[i])
        pairtotals[a,b]=pre[-1]
        assert support[pre[-1]] == point_masks[a]&point_masks[b]
    for a in range(d,h):
        root=total([pairtotals[tuple(sorted((a,b)))] for b in range(h) if b!=a],center=a)
        assert center_coeff[root] == 2*packed(point_masks[a]), "Center coefficients must be exactly doubled"
        roots.append(root);kind.append(1)
    roots.extend(center_disjoint_roots);kind.extend([1]*d)
    # Mixed retained centers recover the total by
    # (sum B_i - 2 sum D_i)/(2(3-d)); check each source coefficient.
    Dset=set(range(d))
    for triple in triples:
        k=len(Dset.intersection(triple))
        assert 2*(3-k)-2*(d-k)==2*(3-d)
    # Check the rational substituted center scatter for every realizable pair of
    # target/source memberships. Its coefficient is (intersection-1)/2.
    from fractions import Fraction
    # Every A_i avoids i, so sum A_i = (h-3)T. The selected decoder is
    # T=sum A_i/21 and scatter T-(1/2)sum_{i in target} A_i.
    decoder=Fraction(1,h-3)
    assert decoder==Fraction(1,21)
    scatter_coefficients=[decoder,decoder-Fraction(1,2)]
    for coefficient in scatter_coefficients:
        odd_denominator=coefficient.denominator
        while odd_denominator%2==0:
            odd_denominator//=2
        assert 21%odd_denominator==0 and abs(coefficient)<=1
    for source in triples:
        assert sum(i not in source for i in range(h))*decoder==1
    patterns={}
    for target in triples:
        chosen=len(Dset.intersection(target))
        if chosen not in patterns:
            patterns[chosen]=target
    for chosen,target in patterns.items():
        target_set=set(target)
        for source in triples:
            k=len(Dset.intersection(source))
            total_coefficient=Fraction(2*(3-k)-2*(d-k),2*(3-d))
            scalar=Fraction(len((target_set-Dset).intersection(source)),2)
            scalar-=Fraction(len((target_set&Dset)-set(source)),2)
            scalar+=Fraction(chosen-1,2)*total_coefficient
            assert scalar==Fraction(len(target_set.intersection(source))-1,2)
    # Check the scalar correction for each target, using the verified exact
    # roots. Twice the coefficient is (intersection-1)+[intersection=0]
    # -[intersection=2], which is two precisely for the diagonal.
    for j,t in enumerate(triples):
        masks=[point_masks[a] for a in t]
        two=(masks[0]&masks[1]&~masks[2]) | (masks[0]&masks[2]&~masks[1]) | (masks[1]&masks[2]&~masks[0])
        actual=0
        for a,b in combinations(t,2):
            excluded=next(i for i in t if i not in (a,b))
            actual |= support[pair_outputs[a,b,excluded]]
        assert actual == two
        assert masks[0]&masks[1]&masks[2] == 1<<j
    assert [((k-1)+(k==0)-(k==2)) for k in range(4)] == [0,0,0,2]
    def contained(x,y):
        tx,ty=types[x],types[y]
        if tx==1 and ty==1: return not(core[y]&~core[x] or cover[x]&~cover[y])
        if tx in (1,2) and ty==2: return not cover[x]&~cover[y]
        if tx==1 and ty==3: return bool(core[x]&core[y])
        if tx==2 and ty==3: return not cover[x]&~core[y]
        if tx==3 and ty==2: return cover[y]==(1<<h)-1
        if tx==3 and ty==3: return core[x]==core[y]
        return False
    active=[0]*len(args);stack=list(roots)
    while stack:
        x=stack.pop()
        if not x or active[x]:continue
        active[x]=1
        if args[x][0]:stack.extend(args[x])
    degree=[0]*len(args)
    for x in range(1,len(args)):
        if active[x]:
            if types[x]==1:
                # Shared-pair triple indicators have self-dot one and
                # pairwise dot zero over F2; a source is a single such line.
                assert core[x].bit_count()>=2 and ranks[x]==support[x].bit_count()
            elif types[x]==2:
                assert ranks[x]==cover[x].bit_count()
            else:
                # E_a is the orthogonal complement of the odd vector 1+e_a.
                assert types[x]==3 and core[x].bit_count()==1 and ranks[x]==h-1
        if active[x] and args[x][0]:
            for y in args[x]:
                assert y<x and contained(y,x), "Binary frame nesting failed"
                degree[y]+=1
    for x in roots:degree[x]+=1
    H=[0]*(h+1);c=0;loss=0
    for x in range(1,len(args)):
        if not active[x]:continue
        r=ranks[x]
        if args[x][0]:
            c+=1;H[r]+=degree[x]-1;H[h-r]+=1
            for y in args[x]:
                assert r>=ranks[y]
                H[r-ranks[y]]+=1
        else:H[1]+=degree[x]
    for x,k in zip(roots,kind):
        r=ranks[x]
        if k:H[r]+=1;H[h]+=1;loss+=r
        else:H[h-1-r]+=1;H[1]+=1
    q=len(roots);R=c+q
    result=dict(h=h,v=v,c=c,q=q,R=R,loss=loss,central_disjoint=d,histogram=H,rank_sum=sum(r*n for r,n in enumerate(H)))
    assert loss == h*(h-1) and result['rank_sum'] == h*R+2*loss
    prefix=Path(prefix)
    result['center_denominator']=21
    result['scalar_validation']=dict(ordinary_supports_exact=True, centers_exact=True,
        center_decoder='sum A_i / 21', scatter_coefficients=list(map(str,scatter_coefficients)),
        rational_scalar_identity_exact=True, mixed_center_scatter_exact=True, binary_frames_nested=True,
        binary_frames_nondegenerate=True)
    with open(str(prefix)+'.bin','wb') as f:
        f.write(struct.pack('<4I',h,v,len(args),q))
        write_array(f,array.array('I',(a for pair in args for a in pair)))
        write_array(f,array.array('Q',core));write_array(f,array.array('Q',cover))
        write_array(f,array.array('I',roots));write_array(f,array.array('I',kind))
        write_array(f,array.array('B',active))
    with open(str(prefix)+'.labels','wb') as f:
        write_array(f,array.array('I',ranks));write_array(f,array.array('B',types))
    Path(str(prefix)+'.json').write_text(json.dumps(result,indent=2)+'\n')

    return result
