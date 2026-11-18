#!/usr/bin/env python3
"""Check actual banked DAG geometry, physical operator bodies and main boundaries."""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from custody import canonical,read,need,sha,NATIVE


WORD = 'ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d'
DIRECT = 'ab5653d6b6007f8a7987e7ffc6ebab24c662ba852a0d0b446c3a1be19b88db8a'
HEAD = '28b2af322a1fab01b3734365988930920f9dda48'
SCIENCE = '26b6c469aa6c4aa04322ce25a22150f90e5fb14e'
PIVOTS = 'fb22afc8aaf543e62709fa682f222577e6bdf4e1f1994d307784468314c3da85'
PEER_RESULT = '00340c699fd7e2895d31a41d1eb60aebf91d7ba2c1c193dc002f69315298cd38'
CUSTODY_PACKED = '18cd4ff7bfaab88dc0c13fba636d1355350cd6199f83ef18c9fe477b33460d23'
DEC_CALLER = '62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf'
CLAIM = 'https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19702865'
RECEIPT = 'progress.kappa-leading-20261118t0540z.00000027'
ENGINE_PINS = {'clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
               'native_verify.py':'3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38'}
PEER_PINS = {'PIVOTS.json':PIVOTS,'RESULT.json':PEER_RESULT,
             'network.py':'a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546',
             'catalogue.py':'11b1b270e366f68bcae333e31716613f1cb9f0ac2ed3e687d70f8ebd7bc7c9c1',
             'SOURCES.json':'76818b74ee05a1a562813b1385b3609dea2bb548c260ebda1b3f8a7aeab236c9'}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    with path.open('xb') as stream:
        stream.write(canonical(value)+b'\n')


def pinned_import(folder, name, digest):
    path = folder / (name+'.py')
    need(sha(path.read_bytes()) == digest,f'{name} source pin')
    sys.path.insert(0,str(folder))
    try:
        module = importlib.import_module(name)
        need(Path(module.__file__).resolve() == path.resolve(),'exact module import path')
        return module
    finally:
        sys.path.pop(0)


def frame_span(vectors):
    members = {0}
    for value in vectors:
        need(type(value) is int and 0 < value < 512 and value not in members,'binary independent chart basis')
        members |= {value^m for m in members}
    return members


@cache
def coefficient(value):
    fraction = Fraction(value)
    need(fraction != 0 and str(fraction) == value,'nonzero exact canonical rational coefficient')
    return fraction


@dataclass
class Graph:
    kind: str
    metadata: dict
    frames: list
    initial: list
    final: list
    first: int
    moves: dict
    forms: dict
    schedule: list


def frozen_graph(root,binding,kind):
    item = binding['graphs'][kind]
    wanted = kind.upper()+'-GRAPH.json.gz'
    need(item['file'] == wanted,'exact graph file name')
    packed = (root/wanted).read_bytes()
    blob = gzip.decompress(packed)
    need(sha(packed) == item['gzip_sha256'] and sha(blob) == item['canonical_sha256'],'immutable bank graph custody')
    data = json.loads(blob)
    need(canonical(data) == blob,'canonical leased graph bytes')
    meta = {'schema':'p104-exact-banked-dag/v1','kind':kind,'peer_head':HEAD,'scientific_commit':SCIENCE,
            'source_word_sha256':WORD,'role230_direct_word_sha256':DIRECT if kind=='candidate' else None,
            'caller_sha256':DEC_CALLER,'fixed_pivot_sha256':PIVOTS,'published_result_sha256':PEER_RESULT}
    need(data['metadata'] == meta and data['first_output'] == 150522,'same tagged bank graph namespace and source')
    moves = {key:(a,b) for key,a,b in data['moves']}
    forms = {key:[(donor,coefficient(q)) for donor,q in terms] for key,terms in data['forms']}
    need(len(moves) == len(data['moves']) == 6142 and len(forms) == len(data['forms']) == 7643,
         'actual initial+terminal row denominator and unique paid slots')
    return Graph(kind,meta,data['frames'],data['initial'],data['final'],data['first_output'],moves,forms,data['schedule'])


def graph_inputs(peer,root,expected_pair=None):
    for name,digest in PEER_PINS.items():
        need(sha((peer/name).read_bytes()) == digest,f'peer source pin {name}')
    network = pinned_import(peer,'network',PEER_PINS['network.py'])
    word = network.source_word()
    need(sha(canonical(word)) == WORD,'exact source word header and ancestry')
    binding = read(root/'GRAPH-BINDING.json')
    need(binding['status'] == 'FROZEN_BOTH_ORDERS_WITH_EXACT_STABLE_KEYS'
         and binding['published_pivot_inventory_reproduced'] and binding['first_output'] == 150522,
         'frozen paired graph receipt')
    got = {k:r['canonical_sha256'] for k,r in binding['graphs'].items()}
    need(expected_pair is None or got == expected_pair,'exact qualified bank graph digests')
    before = frozen_graph(root,binding,'peer')
    after = frozen_graph(root,binding,'candidate')
    for g in (before,after):
        need(g.frames == word['frames'] and g.initial == word['initial'] and g.final == word['final'],
             'common exact ordered frames and public entrances/exits')
    original,peer_net,stamps = network.networks(word)
    need(peer_net.moves == before.moves and
         {k:tuple(sorted(terms.items())) for k,terms in peer_net.forms.items()} == {k:tuple(v) for k,v in before.forms.items()}
         and peer_net.schedule() == before.schedule,'base literally rebuilt by published #7674 scientific code')
    return word,before,after,binding,original.moves,stamps,network.main_roles(word)


def graph_census(g, mains):
    spans = list(map(frame_span,g.frames))
    need(len(mains) == 400 and len(g.initial) == len(g.final) == 1501,'exact public main/helper denominator')
    ends = set(range(g.first,g.first+len(g.final)))
    need(set(g.forms) == ends|g.moves.keys() and len(g.schedule) == len(g.forms) and set(g.schedule) == set(g.forms),
         'unique complete schedule covering paid and terminal slots')
    move_occurrences, helper_occurrences = defaultdict(list),defaultdict(list)
    paid, productive = Counter(),Counter()

    def positive(a,b):
        need(a in range(len(spans)) and b in range(len(spans)), 'paid or helper chart indices')
        need(spans[a] < spans[b] or spans[b] < spans[a], 'strict nested positive rank')
        return abs(len(g.frames[a])-len(g.frames[b]))

    for key,(a,b) in g.moves.items():
        paid[positive(a,b)] += 1
        move_occurrences[a,b].append(key)
    for role,(a,b) in enumerate(zip(g.initial,g.final,strict=True)):
        if role not in mains:
            rank = positive(a,b)
            need(spans[a] < spans[b],'each productive helper E/G is strictly ascending')
            productive[rank] += 1
            helper_occurrences[a,b].append(role)
    known = {~role:chart for role,chart in enumerate(g.initial)}
    total_terms = 0
    for key in g.schedule:
        a,b = g.moves[key] if key in g.moves else (g.final[key-g.first],)*2
        seen = set()
        for donor,_ in g.forms[key]:
            need(donor in known and donor not in seen and known[donor] == a,
                 f'bank dependency or chart mismatch at slot {key}')
            seen.add(donor)
        total_terms += len(seen)
        if key in g.moves:
            known[key] = b
    return move_occurrences,helper_occurrences,{'native_paid':dict(paid),'native_targets':dict(productive),
        'move_occurrences':sum(paid.values()),'productive_occurrences':sum(productive.values()),
        'move_pairs':len(move_occurrences),'productive_pairs':len(helper_occurrences),
        'directed_union':len(move_occurrences.keys()|helper_occurrences.keys()),'scheduled_forms':len(g.schedule),
        'local_terms':total_terms,'helper_325_1087_EG': {r:[g.initial[r],g.final[r]] for r in (325,1087)}}


def cached_maps(path):
    depot = read(path,CUSTODY_PACKED)
    need(depot['source'] == WORD and depot['candidate'] == DIRECT and depot['native_result_sha256'] == NATIVE,
         'scoped rising direct-word proof provenance')
    need(depot['engines'] == {'clifford_exact.py':{'sha256':ENGINE_PINS['clifford_exact.py'],
                                                 'git_blob':'166841a037f069249f6f7f6dedb89248812f59e2'},
                             'native_verify.py':{'sha256':ENGINE_PINS['native_verify.py'],
                                                 'git_blob':'2c209dfa9cfade3bc20ac5fc9d876b433a147f8c'}},
         'cached compiler and checker are exactly the same frozen bytes')
    need(sha(canonical([[*ids,recipe] for ids,_,recipe,_,_ in depot['maps']])) == depot['semantic_recipe_sha256'],
         'immutable complete operator body archive')
    by_basis = {}
    for ids,(a,b),recipe,shard,pin in depot['maps']:
        by_basis.setdefault((tuple(a),tuple(b)),(ids,recipe,shard,pin))
    return by_basis


def engine_pair(folder):
    return tuple(pinned_import(folder,name[:-3],digest) for name,digest in ENGINE_PINS.items())


def main_boundaries(word, producer, checker):
    frames = word['frames']
    h = word['hosted']
    hosted = dict(zip(h['Dports'],zip(h['X2'],h['Y2'],strict=True),strict=True))
    rows = []
    for j,(x,q) in enumerate(zip(word['live'],word['ports'],strict=True)):
        y = x+112
        a,b,c,d = word['initial'][x],word['initial'][y],word['final'][x],word['final'][y]
        need(frames[a] == [q] and frames[b] == [] and
             frame_span(frames[d]) == {s for s in range(512) if (s&q).bit_count() %2 ==0}, 'actual main port axes')
        ar,_ = producer.lower_child(producer.cgate(9,q,1).adjoint().then(producer.canonical_frame(9,tuple(frames[a]))))
        br,_ = producer.lower_child(producer.canonical_frame(9,tuple(frames[d])).adjoint().then(
                producer.cgate(9,q,-1).then(producer.fourier(9))))
        need(ar['rank'] == br['rank'] == 0,'main adapter physical rank zero')
        checker.equal(checker.recipe(ar),(('C',q,-1),)+checker.frame(frames[a],9),'actual input main phase')
        checker.equal(checker.recipe(br),checker.adjoint(checker.frame(frames[d],9))+(('C',q,-1),)+checker.fourier(9),
                      'actual output main phase')
        checker.equal(checker.frame(frames[c],9),checker.fourier(9),'main Fourier return')
        if j in hosted:
            u,v = hosted[j]
            need((word['initial'][u],word['initial'][v],word['final'][u],word['final'][v]) == (a,b,c,d),
                 'byte-equal corresponding hosted boundaries')
        rows.append({'j':j,'q':q,'main_roles':[x,y],'hosted_roles':hosted.get(j),'charts':[a,b,c,d],
                     'input_recipe':ar,'output_recipe':br})
    need(len(rows)==104 and len(hosted)==96,'complete actual 104/96 boundary denominator')
    return rows


def check_operators(frames, keys, forced, custody, producer, checker):
    records = []

    @cache
    def chart(a):
        return producer.canonical_frame(9,tuple(frames[a]))

    @cache
    def ideal(a):
        return checker.frame(frames[a],9)

    for a,b in sorted(keys):
        ordered = tuple(frames[a]),tuple(frames[b])
        archived = custody.get(ordered)
        fresh = archived is None or (a,b) in forced
        if fresh:
            recipe,_ = producer.lower_child(chart(a).adjoint().then(chart(b)))
        else:
            recipe = archived[1]
        need(recipe['rank'] == abs(len(frames[a])-len(frames[b])) > 0, f'paid or productive rank {a}->{b}')
        actual,target = checker.recipe(recipe),checker.adjoint(ideal(a))+ideal(b)
        checker.equal(actual,target,f'{a}->{b} signed Pauli and exact absolute phase')
        if fresh:
            for u,v in ((actual,target),(checker.adjoint(actual),checker.adjoint(target))):
                for column in range(512):
                    need(checker.state(u,column)==checker.state(v,column),f'literal all columns {a}->{b} col {column}')
        records.append({'pair':[a,b],'recipe':recipe,'all_column_comparison':512 if fresh else 0,
                        'compared_signed_pauli_and_absolute_phase':True,
                        'reuse': {'prior_pair':archived[0],'shard':archived[2],'proof_sha256':archived[3]} if not fresh else None})
    return records


def pivot_geometry(steps,stamps,pivots,old_moves,direct,results):
    expected = [[r['direction'],r['remove'],r['pivot'],6156-i] for i,r in enumerate(pivots)]
    need(expected == stamps == results['application']['pivots'] and len(stamps)==15,
         'frozen seven forward and eight transpose pivot identities')
    for i,(step,stamp) in enumerate(zip(steps,stamps,strict=True)):
        d,drop,lead,count = stamp
        need((i,d,drop,lead,count,True) == (step['index'],step['direction'],step['remove'],step['lead'],step['surviving_slots'],
                                             step['same_directed_forms_after_commutation']), 'disjoint pivot stages and actual direction')
    changed = {pair for key,pair in direct.moves.items() if pair != old_moves[key]}
    expected_keys = {tuple(p) for shard in results['catalogue'] for p in shard['columns']}
    need(changed == expected_keys and len(changed)==10,'published ten final rerouted ordered bases')
    proof_routes = []
    for step in steps:
        final = tuple(step['lead_final_forward'])
        actual = final if step['direction']=='forward' else final[::-1]
        proof_routes.append({'index':step['index'],'direction':step['direction'],'lead':step['lead'],
                             'in_pivot_direction':actual,'forward':final,
                             'lead_before':step['lead_before_in_direction']})
    return changed,proof_routes


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--peer-package',type=Path,required=True)
    p.add_argument('--engine-dir',type=Path,required=True)
    p.add_argument('--graphs',type=Path,required=True)
    p.add_argument('--custody',type=Path,required=True)
    p.add_argument('--expect-peer',required=True)
    p.add_argument('--expect-child',required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    out=args.out
    out.mkdir()
    expected = {'peer':args.expect_peer,'candidate':args.expect_child}
    write(out/'START.json',{'observed_at':stamp(),'scope':RECEIPT,'claim':CLAIM,'head':HEAD,'pivot_manifest':PIVOTS,
                             'graph_pins':expected,'program_sha256':sha(Path(__file__).read_bytes()),
                             'map_custody_sha256':CUSTODY_PACKED})
    word,parent,child,binding,old_moves,stamps,mains = graph_inputs(args.peer_package,args.graphs,expected)
    source_m,source_h,source_account = graph_census(parent,mains)
    child_m,child_h,child_account = graph_census(child,mains)
    need(source_h == child_h and parent.moves.keys()==child.moves.keys() and parent.forms.keys()==child.forms.keys(),
         'fixed productive fields and scheduled banks for both constructions')
    changed = [k for k in parent.moves if parent.moves[k]!=child.moves[k]]
    need(sorted(changed) == binding['changed_move_keys'] == [97471,102393],'actual changed role230 slots')
    need(sum(Counter(child_account['native_targets']).values())==1101,'preserved productive targets')
    price = Counter(child_account['native_paid'])
    price.subtract(source_account['native_paid'])
    need({k:v for k,v in price.items() if v} == {2:1,3:-2,4:1},'no extra paid job or target loss')
    pivot_pairs,orientation = pivot_geometry(binding['stages'],stamps,read(args.peer_package/'PIVOTS.json',PIVOTS),
                                              old_moves,parent,read(args.peer_package/'RESULT.json',PEER_RESULT))
    from_source = {parent.moves[k] for k in changed}
    from_child = {child.moves[k] for k in changed}
    actual_keys=source_m.keys()|source_h.keys()|child_m.keys()|child_h.keys()
    direction_keys={tuple(s['in_pivot_direction']) for s in orientation}
    recently_changed=from_source|from_child|pivot_pairs|direction_keys
    producer,checker=engine_pair(args.engine_dir)
    custody = cached_maps(args.custody)
    phase = check_operators(word['frames'],actual_keys|direction_keys,recently_changed,custody,producer,checker)
    actual_change = child.moves[97471]
    found=next(r for r in phase if tuple(r['pair'])==actual_change)
    altered = deepcopy(found['recipe'])
    altered['left']['phase']=(altered['left']['phase']+1)%4
    desired = checker.recipe(found['recipe'])
    bad = checker.recipe(altered)
    need(checker.tableau(bad)==checker.tableau(desired),'phase-only control unchanged signed Pauli action')
    try:
        checker.equal(bad,desired,'mutated actual role230 recipe')
    except ValueError as exc:
        need(str(exc).endswith('exact global phase'),'actual wrong phase failure reason')
    else:
        raise ValueError('phase fault entered the checked bank catalogue')
    forms = child.forms.copy()
    forms[97471] = [(97471,Fraction(1)),*forms[97471]]
    bad_graph=Graph(child.kind,child.metadata,child.frames,child.initial,child.final,child.first,child.moves,forms,child.schedule)
    try:
        graph_census(bad_graph,mains)
    except ValueError as exc:
        need(str(exc)=='bank dependency or chart mismatch at slot 97471','actual cycle mutation rejected at changed slot')
    else:
        raise ValueError('edited dependency cycle escaped')
    write(out/'MAIN-BOUNDARIES.json', main_boundaries(word,producer,checker))
    write(out/'PIVOT-DIRECTIONS.json', orientation)
    by_pair = []
    for record in phase:
        pair=tuple(record['pair'])
        by_pair.append({**record,'in_forward_union':pair in actual_keys,'peer_moves':source_m.get(pair,[]),
                        'candidate_moves':child_m.get(pair,[]),'productive_roles':source_h.get(pair,[])})
    with (out/'BANK-RECIPES.json.gz').open('xb') as stream:
        stream.write(gzip.compress(canonical(by_pair),mtime=0))
    write(out/'RESULT.json',{'status':'PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS','complete_at':stamp(),'source_head':HEAD,
         'graph_pins':expected,'source_word':WORD,'role230_direct':DIRECT,'caller_sha256':DEC_CALLER,
         'source':source_account,'candidate':child_account,'pivot_manifest_sha256':PIVOTS,
         'forward_union':len(actual_keys),'diagnostic_only_pivot_orientations':len(direction_keys-actual_keys),
         'fresh_maps_512_each_direction':sum(bool(r['all_column_comparison']) for r in phase),
         'cached_same_basis_bodies_fresh_pauli_and_phase':sum(r['reuse'] is not None for r in phase),
         'actual_phase_control_rejected':[97471,*actual_change],'actual_cycle_control_rejected':97471,
         'main_boundary_pairs':104,'hosted_correspondences':96,
         'artifact_sha256':{f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},
         'scope':'Actual bank graph map census, all fresh exact Pauli/phase, all columns on changed/unbound pairs and pivot orientations. Separate full held-array and physical storage/resource tests.'})
    print('PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS',len(actual_keys),len(direction_keys-actual_keys),flush=True)


if __name__=='__main__':
    main()
