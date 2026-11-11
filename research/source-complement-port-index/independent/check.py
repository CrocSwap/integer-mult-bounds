"""Independent literal role-word matching and complement-port review.

Expected source sets use explicit parent-word -> (first role, suffix)
edges, not author count/profile/freshness/parent helpers. Production modules
are imported only after constructing a separate literal specification.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path
from types import ModuleType
import json
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = next((p for p in HERE.parents if (p/'groups.py').is_file()),
               HERE.parents[1]/'work/compiler_source_groups/package')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_source(name='peer_source_groups', mutation=None):
    path = PACKAGE/'groups.py'
    text = path.read_text()
    if mutation:
        before, after = mutation
        need(text.count(before) == 1, 'unique review mutation')
        text = text.replace(before, after)
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(text,str(path),'exec'), module.__dict__)
    return module


def literal(roles, rounds, ambient, rank):
    """Build finite words and literal matched target fields before counting."""
    types = sorted({k for _, k in roles})
    smallest = min(types)
    height = 0
    while ambient*smallest**(height+1) <= rank:
        height += 1
    units, point_words, paths = {}, {}, []
    for depth in range(height+1):
        for path in product(range(len(rounds)),repeat=depth):
            paths.append(path)
            rho = prod(rounds[j][0] for j in path)
            words = set()
            buckets = defaultdict(list)
            for word in product(range(len(roles)),repeat=height-depth):
                ranks = tuple(roles[j][1] for j in word)
                if ambient*rho*prod(ranks) <= rank:
                    words.add(word)
                    point = tuple(ranks.count(k) for k in types)
                    buckets[point].append(word)
            units[path], point_words[path] = words, buckets
    matched = set()
    for path in paths:
        if len(path) == height:
            continue
        for word in units[path]:
            first, suffix = word[0], word[1:]
            for site in range(len(rounds)):
                child = path+(site,)
                need(suffix in units[child], 'every parent paid job has an actual child')
                edge = child,suffix,first
                need(edge not in matched, 'literal incoming target uniqueness')
                matched.add(edge)
    sources, interior = [], []
    local = Counter()
    for path in paths:
        rho = prod(rounds[j][0] for j in path)
        for point, words in point_words[path].items():
            column = prod(roles[j][1] for j in words[0])
            for ri,(role,k) in enumerate(roles):
                flags = [(path,word,ri) in matched for word in words]
                need(all(flags) or not any(flags), 'whole Pascal source block')
                for ordinal in range(len(words)):
                    record = path,point,ordinal,ri,role,rho*column*k
                    if flags[0]:
                        interior.append(record)
                    else:
                        sources.append(record)
                        local[path,record[-1]] += 1
    sources.sort()
    subtree = Counter()
    for path,_,_,_,_,s in sources:
        for end in range(len(path)+1):
            subtree[path[:end],s] += 1
    return {'height':height,'paths':paths,'sources':sources,'interior':interior,
            'local':local,'subtree':subtree,'matched':len(matched),
            'units':sum(map(len,units.values()))}


def check(module, roles, rounds, ambient, rank, replicas=12, library=None):
    wanted = literal(roles,rounds,ambient,rank)
    rule = module.C.Rule(roles,rounds,owned=('bank','aux'),ambient=ambient)
    groups = module.SourceGroups(rule,rank,replicas=replicas,namespace='peer')
    expected = wanted['sources']
    by_rank = defaultdict(list)
    for record in expected:
        by_rank[record[-1]].append(record)
    ranks = tuple(sorted(by_rank))
    need(groups.ranks == ranks, 'literal source-rank catalogue')
    need(groups.index.height == wanted['height'], 'independent integer height')
    need(groups.counts == tuple(len(by_rank[s]) for s in ranks), 'literal rank census')
    need(groups.index.size == len(expected), 'literal complete source width')
    if library is None:
        library = tuple(sorted((rank-s,1+(rank-s)%4) for s in ranks if s<rank))
    router = module.ComplementRouter(groups,library)
    widths = dict(library)
    for s in ranks:
        rows = by_rank[s]
        for local,record in enumerate(rows):
            path,point,ordinal,_,role,_ = record
            unit = module.C.Unit(path,point,ordinal)
            need(groups.rank_source(s,unit,role) == local, 'literal filtered row order')
            need(groups.unrank_source(s,local) == (unit,role), 'literal bucket inverse')
            need(groups.job_rank(unit,role) == s, 'actual dilated source job rank')
        bucket = groups._prepare(s)
        for path in wanted['paths']:
            rho = prod(rounds[j][0] for j in path)
            state = len(path),rho,rounds[path[-1]][0] if path else 0
            need(bucket.local[state] == wanted['local'][path,s], 'literal local bucket')
            need(bucket.total[state] == wanted['subtree'][path,s], 'literal subtree bucket')
    seen, batches, skipped = set(),defaultdict(list),0
    for b in range(replicas):
        for j,record in enumerate(expected):
            path,point,ordinal,_,role,s = record
            row = b*len(expected)+j
            identity = ('peer',b,'source',path,point,ordinal,role)
            need(groups.index.owner(row) == identity, 'physical source identity')
            local = by_rank[s].index(record)
            x = b*len(by_rank[s])+local
            if s == rank:
                address = module.NoComplement('peer',s,x)
                skipped += 1
            else:
                call,slot = divmod(x,widths[rank-s])
                address = module.ComplementPort('peer',s,call,slot)
                batches[s,call].append((slot,row))
            need(router.locate(row) == address, 'literal full complement address')
            need(router.row(address) == row, 'literal full complement inverse')
            need(address not in seen, 'source replica/role identity never merged')
            seen.add(address)
    need(len(seen) == replicas*len(expected), 'exact disjoint address cardinality')
    for (s,call), rows in batches.items():
        width = widths[rank-s]
        need(tuple(slot for slot,_ in rows) == tuple(range(width)), 'complete child invocation')
        need(call < router.invocations(s), 'whole invocation ordinal range')
    for record in wanted['interior'][:20]:
        path,point,ordinal,_,role,s = record
        if s in by_rank:
            try:
                groups.rank_source(s,module.C.Unit(path,point,ordinal),role)
            except ValueError:
                pass
            else:
                raise ValueError('matched interior slot promoted to source')
    if expected:
        identity=groups.index.owner(0)
        try:
            groups.index.row(identity[:2]+('owned',)+identity[3:])
        except ValueError:
            pass
        else:
            raise ValueError('owned bank counted as productive source')
    return {'N':str(rank),'height':wanted['height'],'literal_paths':len(wanted['paths']),
            'literal_units':wanted['units'],'matched_fields':wanted['matched'],
            'sources':len(expected),'true_ranks':len(ranks),'replicas':replicas,
            'physical_rows':len(seen),'whole_complement_invocations':len(batches),
            'no_complement_rows':skipped}, groups,router,batches


def rejected(action,label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('review control not detected: '+label)


def main():
    module=load_source()
    family=(
        ((('two_a',2),('eight',8),('four',4),('two_b',2)),
         ((1,'two_b'),(1,'bank')),9,(9,17,18,35,36,71,72)),
        ((('seven_a',7),('eleven',11),('seven_b',7)),
         ((1,'seven_a'),(2,'bank'),(6,'seven_b'),(3,'eleven')),13,
         (13,19,91,97,637,643)),
        ((('single',5),),((1,'single'),(2,'bank'),(2,'single'),(4,'aux')),8,
         (8,39,40,199,200)),
        ((('seven',7),),((1,'seven'),(2,'bank'),(3,'aux'),(6,'seven')),7,(2401,)),
        ((('a',3),('b',5)),((1,'a'),(2,'bank')),5,(45,)),
        ((('one',5),('another',5)),((1,'one'),),5,(5,)),
    )
    cases=[]
    for roles,rounds,ambient,ranks in family:
        for rank in ranks:
            result,_,_,_=check(module,roles,rounds,ambient,rank)
            cases.append(result)
    roles,rounds=(('small',2),('large',5)),((1,'small'),(1,'bank'))
    cross,groups,router,batches=check(module,roles,rounds,5,10,replicas=3,
                                    library=((5,3),(6,1)))
    cases.append(cross)
    first=[row for _,row in batches[5,0]]
    second=[row for _,row in batches[5,1]]
    need(first==[2,3,6] and second==[7,10,11], 'independent cross-replica batches')
    negative=[
        rejected(lambda: module.ComplementRouter(groups,((0,1),(5,3),(6,1))), 'no fabricated B_0'),
        rejected(lambda: module.ComplementRouter(groups,((5,4),(6,1))), 'nonintegral whole batch'),
        rejected(lambda: router.row(module.ComplementPort('peer',10,0,0)), 'no rank-zero invocation'),
        rejected(lambda: router.row(module.NoComplement('peer',5,0)), 'positive complement cannot skip'),
        rejected(lambda: router.row(module.NoComplement('other',10,0)), 'foreign namespace'),
        rejected(lambda: router.row(module.NoComplement('peer',10,3)), 'NoComplement upper endpoint'),
        rejected(lambda: router.locate(3*groups.index.size), 'physical row upper endpoint'),
    ]
    mutations=(
        ('self.groups.rule.ambient*self.rank > self.groups.rank*previous',
         'self.groups.rule.ambient*self.rank >= self.groups.rank*previous','strict parent equality'),
        ('values[-1] += value','values[-1] = value','coincident target products'),
        ('total += multiplicity*self.total[h+1, rho*rank, rank]',
         'total += self.total[h+1, rho*rank, rank]','equal-rank paid positions'),
        ('grouped = replica*self.groups.count(source_rank)+local',
         'grouped = local','replica identity'),
    )
    for i,(before,after,label) in enumerate(mutations):
        bad=load_source('mutated_peer_groups_'+str(i),(before,after))
        if i==0:
            args=((('a',3),('b',5)),((1,'a'),(2,'bank')),5,45)
        elif i==1:
            args=(family[0][0],family[0][1],9,72)
        else:
            args=(roles,rounds,5,10)
        negative.append(rejected(lambda: check(bad,*args),label))
    result={'status':'PASS_SOURCE_GROUPS_PEER_REVIEW',
            'core_sha256':{name:sha256((PACKAGE/name).read_bytes()).hexdigest()
                           for name in ('groups.py','PROOF.md','verify.py')},
            'oracle':'literal ordered role words and parent-word first-role/suffix matching; no author census, freshness or parent helper',
            'cases':cases,'cases_count':len(cases),
            'sources_checked':sum(x['sources'] for x in cases),
            'physical_rows_checked':sum(x['physical_rows'] for x in cases),
            'whole_invocations_checked':sum(x['whole_complement_invocations'] for x in cases),
            'no_complement_rows_checked':sum(x['no_complement_rows'] for x in cases),
            'cross_replica_rows':[first,second],'negative_controls':negative,
            'scope':'logical true-rank metadata and whole complement ports; no physical payload routing or new kappa'}
    (HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'cases='+str(len(cases)),
          'sources='+str(result['sources_checked']),
          'rows='+str(result['physical_rows_checked']),
          'controls='+str(len(negative)))


if __name__=='__main__':
    main()
