#!/usr/bin/env python3
"""Literal source-field oracle and independent whole-flow rank cancellation."""
from collections import Counter
from hashlib import sha1, sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import comb, gcd, lcm
from pathlib import Path
from types import ModuleType
import json
import sys

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok: raise ValueError(message)


def load(name,path):
    spec=spec_from_file_location(name,path)
    module=module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


G=load('source_grouping',HERE/'groups.py')
C=G.C
oracle_path=HERE/'inputs/finite_dag_audit.py'
need(sha256(oracle_path.read_bytes()).hexdigest()==
     'f842f0e07ca40a181782a565a381b0ee20c6a4b08b8c2b8a4d5d630381bd1e8e',
     'unchanged literal source oracle')
O=load('grouping_literal',oracle_path)


class AmbientRule(O.Rule):
    @property
    def dimension(self): return self._ambient


def literal(rule,rank):
    old=AmbientRule(rule.roles,rule.rounds,rule.owned)
    object.__setattr__(old,'_ambient',rule.ambient)
    tree=O.IntegerTree(old,rank)
    occurrences=Counter()
    units={}
    for record in tree.units:
        key=record['path'],record['point']
        units[record['uid']]=C.Unit(*key,occurrences[key])
        occurrences[key]+=1
    order={role:i for i,(role,_) in enumerate(rule.roles)}
    sources=[(units[row['unit']],row['role'],row['rank']) for row in tree.sources]
    sources.sort(key=lambda row:(row[0].path,row[0].point,row[0].ordinal,order[row[1]]))
    return sources,tree


def check(rule,rank):
    expected,tree=literal(rule,rank)
    by_rank={s:[(unit,role) for unit,role,rank_s in expected if rank_s==s]
             for s in sorted({s for _,_,s in expected})}
    library=tuple(sorted((rank-s,2+(rank-s)%2) for s in by_rank if s<rank))
    replication=lcm(*(width//gcd(width,len(by_rank[rank-q])) for q,width in library))
    groups=G.SourceGroups(rule,rank,replicas=replication)
    router=G.ComplementRouter(groups,library)
    need(groups.ranks==tuple(by_rank) and groups.counts==tuple(map(len,by_rank.values())),
         'literal true source-rank census')
    need(groups.index.size==len(expected),'literal total source width')
    q,d,height=len(groups.index.paid),len(rule.types),groups.index.height
    bound=comb(height+q+d,q+d-1)-comb(height+q,q-1)
    need(groups.candidate_count<=bound,'combined semigroup candidate bound')
    need(sum(len(table.keys) for table in groups.products)<=comb(height+d+1,d),
         'all-degree product table bound')
    local,subtree=Counter(),Counter()
    for unit,role,s in expected:
        local[unit.path,s]+=1
        for end in range(len(unit.path)+1): subtree[unit.path[:end],s]+=1
    for s,rows in by_rank.items():
        if s<rank:
            need(router.invocations(s)*router.width(s)==replication*len(rows),
                 'complete invocation census')
        for index,(unit,role) in enumerate(rows):
            need(groups.rank_source(s,unit,role)==index,'literal within-rank order')
            need(groups.unrank_source(s,index)==(unit,role),'literal bucket inverse')
        bucket=groups._prepare(s)
        for path,_ in tree.classes:
            rho=1
            for j in path: rho*=rule.rounds[j][0]
            previous=rule.rounds[path[-1]][0] if path else 0
            state=len(path),rho,previous
            need(bucket.local[state]==local[path,s], 'literal class local bucket count')
            need(bucket.total[state]==subtree[path,s], 'literal class subtree bucket count')
    skipped=0
    for replica in range(replication):
        for index,(unit,role,s) in enumerate(expected):
            row=replica*len(expected)+index
            local_index=by_rank[s].index((unit,role))
            grouped=replica*len(by_rank[s])+local_index
            if s==rank:
                wanted=G.NoComplement('flow',rank,grouped)
                skipped+=1
            else:
                width=next(width for q,width in library if q==rank-s)
                call,slot=divmod(grouped,width)
                wanted=G.ComplementPort('flow',s,call,slot)
            need(router.locate(row)==wanted,'literal invocation and child input slot')
            need(router.row(wanted)==row,'whole complement port inverse')
    collision={}
    for unit in tree.units:
        collision.setdefault((unit['path'],unit['column']),set()).add(unit['point'])
    return Counter(cases=1,literal_classes=len(tree.classes),literal_sources=len(expected),
                   replicated_rows=replication*len(expected),no_complement_rows=skipped,
                   positive_buckets=len(by_rank),states=len(groups.states),
                   product_collision_classes=sum(len(points)>1 for points in collision.values()))


def independent_histogram(rule,rank,height):
    """Target census minus all actual incoming paid jobs, not freshness tests."""
    words=[Counter({1:1})]
    paths=[Counter({1:1})]
    for _ in range(height):
        next_words,next_paths=Counter(),Counter()
        for product,count in words[-1].items():
            for _,k in rule.roles: next_words[product*k]+=count
        for rho,count in paths[-1].items():
            for r,_ in rule.rounds: next_paths[rho*r]+=count
        words.append(next_words)
        paths.append(next_paths)
    sources=Counter()
    for h in range(height+1):
        for rho,copies in paths[h].items():
            for column,units in words[height-h].items():
                if rule.ambient*rho*column<=rank:
                    for _,k in rule.roles: sources[rho*column*k]+=copies*units
        if h:
            for rho,copies in paths[h-1].items():
                for column,units in words[height-h+1].items():
                    if rule.ambient*rho*column<=rank:
                        for r,_ in rule.rounds: sources[rho*column*r]-=copies*units
    need(all(count>=0 for count in sources.values()),'rank-wise incoming subtraction nonnegative')
    return {s:count for s,count in sorted(sources.items()) if count}


def reject(action,label):
    try: action()
    except (ValueError,AssertionError,IndexError): return label
    raise ValueError('negative control accepted: '+label)


def mutated(old,new,name):
    text=(HERE/'groups.py').read_text()
    need(text.count(old)==1,'unique group mutation site')
    module=ModuleType(name)
    module.__file__=str(HERE/'groups.py')
    sys.modules[name]=module
    exec(compile(text.replace(old,new),name,'exec'),module.__dict__)
    return module


def controls():
    rule=C.Rule((('small',2),('large',5)),((1,'small'),(1,'bank')))
    groups=G.SourceGroups(rule,10,replicas=3)
    router=G.ComplementRouter(groups,((5,3),(6,1)))
    need(groups.count(5)==2,'cross-replica source bucket')
    first=[router.row(G.ComplementPort('flow',5,0,slot)) for slot in range(3)]
    second=[router.row(G.ComplementPort('flow',5,1,slot)) for slot in range(3)]
    need(first==[2,3,6] and second==[7,10,11],'actual whole batches cross replica boundary')
    need([router.row(G.NoComplement('flow',10,j)) for j in range(3)]==[1,5,9],
         'full-rank sources skip complement entirely')
    out=[reject(lambda: G.ComplementRouter(groups,((0,1),(5,3),(6,1))), 'fabricated B_0'),
         reject(lambda: G.ComplementRouter(groups,((5,4),(6,1))), 'nonintegral complement batch'),
         reject(lambda: G.ComplementRouter(groups,((5,3),)), 'missing positive complement library'),
         reject(lambda: router.row(G.ComplementPort('flow',10,0,0)), 'zero-rank invocation'),
         reject(lambda: router.invocations(10), 'zero-rank invocation census'),
         reject(lambda: router.row(G.NoComplement('flow',5,0)), 'skipped positive complement'),
         reject(lambda: router.row(G.ComplementPort('flow',5,2,0)), 'invocation upper endpoint'),
         reject(lambda: router.row(G.ComplementPort('flow',5,0,3)), 'slot upper endpoint'),
         reject(lambda: router.row(G.NoComplement('flow',10,3)), 'no-complement upper endpoint'),
         reject(lambda: router.row(G.ComplementPort('other',5,0,0)), 'foreign invocation namespace'),
         reject(lambda: groups.count(11), 'absent true source rank'),
         reject(lambda: router.locate(3*groups.index.size), 'replicated row upper endpoint')]
    unit,role=groups.unrank_source(5,0)
    out.append(reject(lambda: groups.rank_source(4,unit,role),'wrong source-rank label'))
    other=G.SourceGroups(C.Rule((('a',3),('b',5)),((1,'a'),(2,'bank'))),45)
    out.append(reject(lambda: other.rank_source(10,C.Unit((0,1),(0,0),0),'b'),
                      'matched slot with same rank as a real source'))
    need(other.rank_source(10,C.Unit((1,0),(0,0),0),'b')>=0,'last paid rank retains freshness')
    bad=mutated('self.groups.rule.ambient*self.rank > self.groups.rank*previous',
                'self.groups.rule.ambient*self.rank >= self.groups.rank*previous','bad_fresh_equality')
    out.append(reject(lambda: bad.SourceGroups(C.Rule((('a',3),('b',5)),((1,'a'),(2,'bank'))),45),
                      'non-strict parent cutoff mutation'))
    bad=mutated('values[-1] += value','values[-1] = value','bad_product_collision')
    out.append(reject(lambda: bad.SourceGroups(C.Rule((('a',3),('b',5)),((1,'a'),)),75),
                      'overwritten product collision'))
    bad=mutated('total += multiplicity*self.total[h+1, rho*rank, rank]',
                'total += self.total[h+1, rho*rank, rank]','bad_paid_multiplicity')
    out.append(reject(lambda: bad.SourceGroups(rule,10), 'merged equal-rank paid occurrences'))
    bad=mutated('grouped = replica*self.groups.count(source_rank)+local',
                'grouped = local','bad_replica_merge')
    badgroups=bad.SourceGroups(rule,10,replicas=3)
    badrouter=bad.ComplementRouter(badgroups,((5,3),(6,1)))
    out.append(reject(lambda: need(badrouter.row(badrouter.locate(6))==6,'replica identity'),
                      'merged replicated source arrays'))
    only=G.SourceGroups(C.Rule((('one',3),),((1,'one'),)),3,replicas=5)
    idle=G.ComplementRouter(only,())
    need(all(idle.row(idle.locate(i))==i for i in range(5)), 'empty positive complement library')
    collision=G.SourceGroups(C.Rule((('a',2),('extra',2),('b',4),('c',8)),((1,'a'),)),128)
    need(collision.products[2].get(16)==5,
         'two rank-2 role names with rank 8 plus the rank-4 square')
    return out,{'source_rank':5,'first_invocation_rows':first,'second_invocation_rows':second,
                'no_complement_rows':[1,5,9]}


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())['inputs']
    need(tuple(pin['local_path'] for pin in pins)==(
        'inputs/source_index/source_index.py','inputs/source_index/inputs/pascal_codec.py',
        'inputs/finite_dag_audit.py','reference/FINITE-PRECOMPILATION.md',
        'reference/symbolic-batch-PROOF.md','reference/chronological-batch-README.md'),
        'complete frozen input inventory')
    for pin in pins:
        raw=(HERE/pin['local_path']).read_bytes()
        need(len(raw)==pin['bytes'] and sha256(raw).hexdigest()==pin['sha256'] and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],
             'frozen input bytes')
    cases=[
        (C.Rule((('a',2),('b',4),('c',8),('extra',2)),((1,'a'),(1,'bank'))),
         (8,15,16,31,32,63,64,128)),
        (C.Rule((('large',5),('small',3),('extra',3)),((1,'small'),(1,'bank'),(2,'large')),ambient=7),
         (7,20,21,62,63,188,189)),
        (C.Rule((('a',4),('b',7)),((1,'a'),(2,'bank'),(3,'b'),(1,'a')),ambient=8),
         (8,31,32,127,128)),
        (C.Rule((('single',3),),((1,'single'),)),(3,8,9,10,26,27)),
    ]
    total=Counter()
    for rule,ranks in cases:
        for rank in ranks: total.update(check(rule,rank))
    need(total['product_collision_classes']>0,'literal fitting product coincidences exercised')
    large_rule=C.Rule((('a',3),('b',3),('c',5),('d',5)),
                      ((1,'a'),(1,'bank'),(2,'c')),ambient=7)
    large=G.SourceGroups(large_rule,7*3**24,replicas=6)
    independent=independent_histogram(large_rule,large.rank,large.index.height)
    need(independent==dict(zip(large.ranks,large.counts)),'independent all-rank cancellation census')
    library=tuple(sorted((large.rank-s,2+(large.rank-s)%2)
                         for s in large.ranks if s<large.rank))
    router=G.ComplementRouter(large,library)
    samples=(0,1,large.index.size//2,large.index.size-1,
             3*large.index.size+17,6*large.index.size-1)
    for row in samples: need(router.row(router.locate(row))==row,'large unenumerated row inverse')
    controls_run,example=controls()
    print(json.dumps({'status':'PASS_TRUE_SOURCE_COMPLEMENT_PORTS','source_pins':len(pins),'literal':dict(total),
        'negative_controls':controls_run,'cross_replica_example':example,
        'large':{'height':large.index.height,'states':len(large.states),
                 'candidate_ranks':large.candidate_count,'positive_rank_buckets':len(large.ranks),
                 'source_rows_per_replica':str(large.index.size),'replicas':6,
                 'class_paths_not_enumerated':str((3**25-1)//2),
                 'independently_checked_rank_counts':len(independent),'round_trip_samples':len(samples)},
        'scope':'logical whole-complement port bijection; no physical routing or new kappa'},
        indent=2,sort_keys=True))


if __name__=='__main__': main()
