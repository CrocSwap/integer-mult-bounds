"""Temporal input-support obstruction for literal serial MOVE contacts."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from time import monotonic

DELIVERY_SHA = '184099c694493caa31d6c350be6cfd32520fc9bcef6d8fe4960d248d1c2cd67f'
PILOT = (738, 40528, 40538, 40529)


def dependency(path):
    assert sha256(path.read_bytes()).hexdigest() == DELIVERY_SHA
    spec = importlib.util.spec_from_file_location('exact_delivery_source', path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def ids(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length()-1
        mask ^= low


def runs_and_reads(word, moves, class_id):
    paths, reads = defaultdict(list), defaultdict(list)
    for move in moves:
        paths[move['role']].append(move)
    for i, (op, role, *args) in enumerate(word['program']):
        if op in ('ADD','COPY'):
            reads[args[0]].append((i,args[2]))
    runs, barriers, edges = [], [], []
    contains = defaultdict(set)
    for owner, path in sorted(paths.items()):
        run = []

        def finish():
            if not run:
                return
            group = len(runs)
            runs.append(len(run))
            for left in range(len(run)):
                for right in range(left+1,len(run)):
                    eid = len(edges)
                    edges.append((class_id[run[left]['source']], class_id[run[right]['target']]))
                    for m in run[left:right+1]:
                        contains[m['event']].add(eid)
            for j,(left,right) in enumerate(zip(run,run[1:]),1):
                first = next(((i,f) for i,f in reads[owner] if left['event'] < i < right['event']),None)
                if first is not None:
                    read,label = first
                    assert label == left['target'] == right['source']
                    barriers.append((group,j,owner,left['event'],right['event'],read,label))
        for m in path:
            ascent = m['rank'] == 1 and m['source_dim']+1 == m['target_dim']
            if run and (not ascent or m['source'] != run[-1]['target']):
                finish()
                run = []
            if ascent:
                run.append(m)
        finish()
    return runs, barriers, edges, contains


def query_rows(word, barriers, donor, check_time):
    wanted = {b[5]: b[2] for b in barriers}
    assert len(wanted) == len(barriers)
    live, masks = {}, {}

    def visit(cut, owner, chart, row):
        live[owner] = row.copy()
        if cut in wanted:
            masks[cut] = sum(1 << i for i in live[wanted[cut]])

    donor.replay(word, max(wanted), visit, check_time)
    assert masks.keys() == wanted.keys() and all(masks.values())
    return masks


class Reachability:
    def __init__(self, class_ranks, class_id, word, moves, edges, contains):
        self.class_ranks = class_ranks
        self.order = sorted(range(len(class_ranks)),key=class_ranks.__getitem__,reverse=True)
        self.fixed = [(m['event'],class_id[m['source']],class_id[m['target']]) for m in moves]
        self.edges = edges
        self.contains = contains
        self.counts = Counter(edges)
        self.initial = [0]*len(class_ranks)
        for i,label in enumerate(word['initial']):
            self.initial[class_id[label]] |= 1 << i

    def graph(self, left, right):
        omitted = Counter(self.edges[i] for i in self.contains[left] ^ self.contains[right])
        outgoing = [[] for _ in self.class_ranks]
        for (source,target), count in self.counts.items():
            if count > omitted[source,target]:
                assert self.class_ranks[source] < self.class_ranks[target]
                outgoing[source].append(target)
        return outgoing

    def reachable(self, left, right, cut, target, restore=False):
        outgoing = self.graph(left,right)
        descend = [1 << i for i in range(len(outgoing))]
        for i in self.order:
            for child in outgoing[i]:
                descend[i] |= descend[child]
        closure = [tuple(ids(mask)) for mask in descend]
        available = [0]*len(outgoing)

        def add(i,mask):
            new = mask & ~available[i]
            if new:
                for j in closure[i]:
                    available[j] |= new
        for i,mask in enumerate(self.initial):
            add(i,mask)
        for event,source,dest in self.fixed:
            if event >= cut:
                break
            if restore or event not in (left,right):
                add(dest,available[source])
        return available[target]

    def single_coordinate(self,left,right,cut,target,coordinate):
        outgoing = self.graph(left,right)
        active = set()

        def visit(start):
            stack = [start]
            while stack:
                cur = stack.pop()
                if cur not in active:
                    active.add(cur)
                    stack.extend(outgoing[cur])

        for i,mask in enumerate(self.initial):
            if mask & (1 << coordinate):
                visit(i)
        for event,source,dest in self.fixed:
            if event >= cut:
                break
            if source in active and event not in (left,right):
                visit(dest)
        return target in active


def run(package, cap, seconds):
    started = monotonic()

    def check_time():
        if monotonic()-started >= seconds:
            raise TimeoutError('temporal support budget')

    earlier = dependency(Path(__file__).with_name('paid_delivery.py'))
    chart, owned, rank, donor = [earlier.load(package,n) for n in earlier.PINS]
    root = package/'inputs'
    word, result, caller, gate = chart.read_sources(
        root/'peer',root/'caller/CALLER.json',root/'caller/interval_gate.py',owned,1)
    try:
        spaces,moves,_,_ = owned.scan_word(word,check_time,80000)
        signed,invoice = owned.full_invoice(word,caller,result,moves)
        reps, class_id, class_ranks = {}, [], []
        for space in spaces:
            if space not in reps:
                reps[space] = len(class_ranks)
                class_ranks.append(owned.dimension(space))
            class_id.append(reps[space])
        for m in moves:
            m.update(source_dim=class_ranks[class_id[m['source']]],
                     target_dim=class_ranks[class_id[m['target']]])
        runs,barriers,edges,contains = runs_and_reads(word,moves,class_id)
        assert len(edges) == 3925
        assert Counter(runs) == {1:658,2:190,3:511,4:335,5:12,9:2}
        query = query_rows(word,barriers,donor,check_time)
        engine = Reachability(class_ranks,class_id,word,moves,edges,contains)
    except TimeoutError:
        return dict(status='PREPASS_PENDING',first_pending='exact tape scan',head=owned.HEAD,
                    cap=cap,seconds=seconds,seed=None)
    cuts = [{0,n} for n in runs]
    before = gate.moment(signed,owned.TARGET)
    powers = [gate.exact(0)] + [gate.power(i,owned.TARGET) for i in range(1,max(runs)+1)]

    def margin():
        hist = Counter(right-left for part in cuts for left,right in zip(sorted(part),sorted(part)[1:]))
        ideal = gate.sub(gate.exact(sum(runs)),gate.moment(hist,owned.TARGET))
        return gate.add(before,gate.smul(ideal,owned.STAGES)), hist

    def priority(barrier):
        group,j,*_ = barrier
        low = max(k for k in cuts[group] if k <= j)
        high = min(k for k in cuts[group] if k >= j)
        delta = powers[j-low][0]+powers[high-j][0]-powers[high-low][1]
        return -delta,barrier[5]

    first = next(b for b in barriers if b[2:6] == PILOT)
    _,_,owner,left,right,read,label = first
    target = class_id[label]
    original = engine.reachable(left,right,read,target,restore=True)
    assert query[read] & ~original == 0
    remaining = set(barriers)
    checked = []
    starting,hist = margin()
    current, status = starting, 'EXHAUSTED'
    while remaining:
        if len(checked) >= cap or monotonic()-started >= seconds:
            status = 'CAP_PENDING'
            break
        candidate = first if not checked else min(remaining,key=priority)
        remaining.remove(candidate)
        group,j,owner,left,right,read,label = candidate
        target = class_id[label]
        missing = query[read] & ~engine.reachable(left,right,read,target)
        witness = (missing & -missing).bit_length()-1 if missing else None
        if missing:
            cuts[group].add(j)
            if len(checked) < 8:
                assert not engine.single_coordinate(left,right,read,target,witness)
        checked.append(dict(role=owner,read=read,left=left,right=right,chart=label,
                            absent=missing.bit_count(),first_absent=witness))
        if len(checked) == 1:
            assert owner == 738 and witness == 0 and missing.bit_count() == 23
        current,hist = margin()
        if current[1] < 0:
            status = 'PRICE_CLOSED'
            break
    pending = min(remaining,key=priority) if remaining else None
    retained_blocks = sum(n*(n-1)//2*count for n,count in hist.items())
    return dict(status=status,head=owned.HEAD,target=str(owned.TARGET),seed=None,
                cap=cap,seconds=seconds,pins=owned.PINS | earlier.PINS | {'paid_delivery.py':DELIVERY_SHA},
                invoice=invoice,read_barriers_total=len(barriers),read_barriers_unvisited=len(remaining),
                blocks_total=len(edges),blocks_not_excluded=retained_blocks,blocks_excluded=len(edges)-retained_blocks,
                tested=checked,first_pending=pending,initial_moment=gate.show(starting),
                upper_moment=gate.show(current),upper_run_histogram=hist,
                predecessor_control='Original MOVE at the first pilot restores all needed coordinate support.',
                scope='Other old MOVE clocks retained as a free overgrant. Every eligible fused arc is available timelessly, except those using exactly one of the mandatory adjacent pair. Arbitrary coframed operations and free persistent caches.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package',type=Path)
    parser.add_argument('--cap',type=int,default=1024)
    parser.add_argument('--seconds',type=int,default=600)
    args = parser.parse_args()
    assert __debug__ and 0 < args.cap <= 1024 and 0 < args.seconds <= 600
    print(json.dumps(run(**vars(args)),indent=2,sort_keys=True))
