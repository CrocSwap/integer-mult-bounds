"""Changed exclusion graphs with more admissible retained carriers.

Underlying cancellation-free generators: icekylinx PR18/36. Alternating
point order: RaD/hipotures PR41, checkpoint 7e488e6b25dc1713c1f41baaf1cefbf677507cf3.
Compared with PR46, reorder the vector leave-one-out construction by source
support size, breaking ties by ascending support at h23 and descending at
h25; restore the original output indexing. The h23 total folds in reverse
input order, while h25 retains descending (support size, support) order.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
from partial_swap.paired import PairedExclusionCircuit
from partial_swap.shared import SharedPointCircuit


def alternating_points(h,common):
    pairs=[(a,a+1) for a in range(0,h-1,2) if common not in (a,a+1)]
    if common%2:
        pairs.reverse()
    head=[x for pair in pairs for x in pair]
    return head+[x for x in range(h) if x!=common and x not in head]


def graph(h):
    assert h in (23,25)
    class Changed(PairedExclusionCircuit):
        base_threshold=2
        def total(self,values):
            values=[x for x in values if x]
            if h==23:
                values.reverse()
            else:
                values.sort(key=lambda node:(self.support[node].bit_count(),self.support[node]),reverse=True)
            result=0
            for node in values:
                result=self.add(result,node)
            return result
        def vector(self,values,two=True):
            if two:
                return super().vector(values,two)
            sign=1 if h==23 else -1
            order=sorted(range(len(values)),key=lambda i:
                         (self.support[values[i]].bit_count(),sign*self.support[values[i]]))
            total,one,_=super().vector([values[i] for i in order],False)
            restored=[0]*len(values)
            for position,original in enumerate(order):
                restored[original]=one[position]
            return total,restored,{}
    local=Changed(h-1)
    total=local.pair(list(range(h-1)))[0]
    local.outputs[()]=total
    stack=[total]
    while stack:
        node=stack.pop()
        if not node or node in local.active:
            continue
        local.active.add(node)
        if local.args[node]:
            stack.extend(local.args[node])
    local.additions=sum(local.args[node] is not None for node in local.active)
    return SharedPointCircuit(h,local,point_order=alternating_points)
