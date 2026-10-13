"""Split-pair recursion with pinned summand orders, built on PR53 skip strips.
Original skip-prefix layout: Avi Eisenberg / Anthropic Claude PR53.
Paired exclusion: icekylinx; alternating common-point order: RaD / hipotures.
Grouping and order refinement here prepared with OpenAI Codex assistance.
Apache-2.0; retained predecessor source notices apply.
"""
from itertools import combinations
import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'research/skip-strips')]
import skip_graph as base
from partial_swap.paired import PairedExclusionCircuit
from partial_swap.shared import SharedPointCircuit

def reorder(c, values, mode):
    order=list(range(len(values)))
    if mode=='reverse': order.reverse()
    elif mode=='desc': order.sort(key=lambda i:(c.support[values[i]].bit_count(),c.support[values[i]]),reverse=True)
    elif mode=='asc': order.sort(key=lambda i:(c.support[values[i]].bit_count(),c.support[values[i]]))
    elif mode=='size_desc': order.sort(key=lambda i:(-c.support[values[i]].bit_count(),c.support[values[i]]))
    elif mode=='support_desc': order.sort(key=lambda i:(c.support[values[i]].bit_count(),-c.support[values[i]]))
    elif mode=='odd_even': order=order[1::2]+order[::2]
    elif mode=='even_odd': order=order[::2]+order[1::2]
    elif mode=='ends': order=[x for pair in zip(order[:len(order)//2],order[::-1][:len(order)//2]) for x in pair]+([len(order)//2] if len(order)%2 else [])
    elif mode!='input': raise ValueError(mode)
    return order

def graph(h,config=None,record=None):
    if config is None:
        config=json.loads((Path(__file__).resolve().parent/f"config-{h}.json").read_text())
    cfg=config or {}; recording=record if record is not None else {}
    totals=cfg.get('totals',{});strips=cfg.get('strips',{})
    class Circuit(base.circuit_class(h)):
        def grouping(self,points):
            groups=super().grouping(points)
            choices=cfg.get('groups',[0,0,0,0,0])
            choice=choices[self._level] if self._level<len(choices) else 0
            if len(points)>3 and choice:
                k={1:0,2:(len(groups)-1)//2,3:len(groups)-1}[choice]
                if len(groups[k])==2:groups[k:k+1]=[[x] for x in groups[k]]
            assert all(len(g) in (1,2) for g in groups) and len(groups)<len(points), "Noncontracting partition"
            return groups
        def pair(self,points):
            self._ti=self._si=0
            return super().pair(points)
        def total(self, values):
            values=[x for x in values if x]
            if len(values)<=1:return values[0] if values else 0
            i=str(self._ti);self._ti+=1
            order=reorder(self,values,cfg.get('total_mode','reverse' if h==23 else 'desc'))
            order=totals.get(i,order)
            assert sorted(order)==list(range(len(values))), 'Invalid total permutation'
            recording.setdefault('totals',{})[i]=order
            result=0
            for j in order: result=self.add(result,values[j])
            return result
        def _block(self, points, edges, weights, level):
            if len(points)<=self.base_threshold:return PairedExclusionCircuit.block(self,points,edges,weights)
            def layout(c,vals):
                i=str(c._si);c._si+=1
                mode=cfg.get('top_mode','reverse') if level==0 else cfg.get('deep_mode','asc' if h==23 else 'support_desc')
                order=reorder(c,vals,mode);order=strips.get(i,order)
                assert sorted(order)==list(range(len(vals))), 'Invalid strip permutation'
                recording.setdefault('strips',{})[i]=order
                total,out=base.skip_prefix(c,[vals[j] for j in order])
                restored=[0]*len(vals)
                for j,k in enumerate(order):restored[k]=out[j]
                return total,restored
            groups=self.grouping(points);ng=len(groups)
            e=lambda a,b:edges[tuple(sorted((a,b)))]
            coarse={(i,j):self.total([e(a,b) for a in groups[i] for b in groups[j]]) for i,j in combinations(range(ng),2)}
            wt={i:self.total([weights[a] for a in g]+[e(a,b) for a,b in combinations(g,2)]) for i,g in enumerate(groups)}
            total,outside,far=self.block(list(range(ng)),coarse,wt)
            strips2,sums={},{}
            for i,g in enumerate(groups):
                other=[j for j in range(ng) if j!=i]
                for a in g:
                    carry=self.total([weights[u] for u in g if u!=a])
                    vals=[self.total([e(u,v) for u in g if u!=a for v in groups[j]]) for j in other]
                    st,one=base.leave_one_out(self,[carry]+vals,layout)
                    strips2[a]={j:z for j,z in zip(other,one[1:])};sums[a]=st
            out={};single={a:self.add(outside[i],sums[a]) for i,g in enumerate(groups) for a in g}
            for i,g in enumerate(groups):
                for a,b in combinations(g,2):out[a,b]=outside[i]
            for i,j in combinations(range(ng),2):
                for a in groups[i]:
                    left=self.add(far[i,j],strips2[a][j])
                    for b in groups[j]:
                        cross=self.total([e(u,v) for u in groups[i] if u!=a for v in groups[j] if v!=b])
                        out[a,b]=self.add(left,self.add(strips2[b][i],cross))
            return total,single,out
    local=Circuit(h-1)
    total=local.pair(list(range(h-1)))[0];local.outputs[()]=total
    stack=[total]
    while stack:
        node=stack.pop()
        if not node or node in local.active:continue
        local.active.add(node)
        if local.args[node]:stack.extend(local.args[node])
    local.additions=sum(local.args[node] is not None for node in local.active)
    def point_order(h,common):
        pairs=[(a,a+1) for a in range(0,h-1,2) if common not in (a,a+1)]
        mode=cfg.get('point_mode','alternating')
        if mode=='alternating':
            if common%2:pairs.reverse()
        elif mode=='reverse-alternating':
            if not common%2:pairs.reverse()
        elif mode=='reverse':pairs.reverse()
        elif mode=='paired-rotate':
            k=(common//2)%len(pairs);pairs=pairs[k:]+pairs[:k]
        elif mode=='common-rotate':
            k=common%len(pairs);pairs=pairs[k:]+pairs[:k]
        elif mode=='xor-pairs':pairs.sort(key=lambda pair:(pair[0]//2)^(common//2))
        elif mode=='center-out':pairs.sort(key=lambda pair:abs(pair[0]-common))
        elif mode=='alternating-ends':
            pairs=pairs[::2]+pairs[1::2][::-1]
            if common%2:pairs.reverse()
        elif mode=='input':pass
        else:raise ValueError(mode)
        order=cfg.get('points',{}).get(str(common),list(range(len(pairs))))
        assert sorted(order)==list(range(len(pairs))), 'Invalid point permutation'
        pairs=[pairs[j] for j in order]
        head=[x for pair in pairs for x in pair]
        return head+[x for x in range(h) if x!=common and x not in head]
    return SharedPointCircuit(h,local,point_order=point_order)
