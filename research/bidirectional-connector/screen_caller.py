#!/usr/bin/env python3
"""Source-bound screen of a retained centre interface in the selected manifest.

Eight clean/private centre copies and different rank-eight charts are outside
this package's two arbitrary dirty roots and fixed complete-query tariffs.
Apache-2.0. conorholds with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
MANIFEST='research/community-frontier1094-audit/SELECTED-SOURCE.json'
PREFIX='research/gauge44-slots-t16/'
WORD=PREFIX+'evidence/local/CANONICAL-WORD.json.gz'
PROGRAMS=PREFIX+'evidence/local/LOCAL-PROGRAMS.json.gz'


def need(ok,message):
    if not ok:raise ValueError(message)


def run(repo):
    pins=json.loads((HERE/'SOURCES.json').read_text())
    expected={r['path']:r['sha256'] for r in pins['files']}
    payloads={}
    for name in ('certificates/selected-result.json',MANIFEST,WORD,PROGRAMS):
        raw=(repo/name).read_bytes()
        need(name in expected and sha256(raw).hexdigest()==expected[name], 'caller source pin mismatch: '+name)
        payloads[name]=json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    selected=payloads['certificates/selected-result.json'];manifest=payloads[MANIFEST]
    need(selected['source_manifest']==MANIFEST,'not the selected source manifest')
    need(all(manifest['files'][name]==expected[name] for name in (WORD,PROGRAMS)),
         'caller artifacts are not bound by selected manifest')
    word=payloads[WORD];programs=payloads[PROGRAMS]
    centres=word['centers'];frames=[word['frames'][i] for i in word['center_frames']]
    need(len(centres)==len(set(centres))==len(frames)==8,'centre interface changed')
    need(all(len(frame)==8 for frame in frames),'centre rank changed')
    need(len({tuple(frame) for frame in frames})==8,'centre charts are no longer distinct')
    targets=defaultdict(list)
    for op in word['cut']:
        need(op[0]=='add' and op[2] in centres and op[3] in (-1,1) and op[4]==4,
             'cut is outside signed quarter-read class')
        targets[op[1]].append((op[2],op[3],op[4]))
    need(len(targets)==112 and all(len(terms)==2 for terms in targets.values()),'two-read centre target shape changed')
    edges={tuple(sorted(term[0] for term in terms)) for terms in targets.values()}
    graph={source:set() for source in centres}
    for a,b in edges:graph[a].add(b);graph[b].add(a)
    components=[];unseen=set(centres)
    while unseen:
        pending=[min(unseen)];component=set()
        while pending:
            node=pending.pop()
            if node in component:continue
            component.add(node);pending.extend(graph[node]-component)
        unseen-=component;components.append(sorted(component))
    need(len(components)==2 and all(len(c)==4 for c in components),'centre graph changed')
    need(all(tuple(pair) in edges for c in components for pair in combinations(c,2)), 'centre components are not K4')
    preparations={}
    for orientation,events in programs.items():
        copies=[op for op in events if op[0]=='scalar' and op[1][0]=='copy' and op[1][1][0]=='C']
        clears=[op for op in events if op[0]=='scalar' and op[1][0]=='clear' and op[1][1][0]=='C']
        descents=[op for op in events if op[0]=='center']
        preparations[orientation]={'private_centre_copies':len(copies),'private_centre_clears':len(clears),
                                   'centre_path_events':len(descents)}
    need(preparations['forward']=={'private_centre_copies':8,'private_centre_clears':16,'centre_path_events':8},
         'forward clean-centre preparation changed')
    patterns=Counter(tuple(terms) for terms in targets.values())
    return {'schema':'retained-centre-contract-screen-v1','selected_kappa':selected['kappa'],
            'artifact_scope':'Retained canonical centre interface included in selected source manifest; not a replay or census of the currently dispatched provider programs.',
            'source_pins':{name:expected[name] for name in payloads},'centre_carriers':centres,
            'distinct_rank_eight_charts':8,'target_rows':len(targets),'cut_scalar_adds':len(word['cut']),
            'signed_patterns':len(patterns),'source_pair_edges':len(edges),'pair_components':components,
            'literal_private_preparation':preparations,
            'dirty_query_source_floor':2*len(centres),'dirty_query_output_floor':2*len(targets),
            'contract_mismatch':['The selected batch has 112 signed two-source rows, not the universal 255-mask positive batch.',
                                 'The literal program copies into and clears owned private centres; it does not start with two arbitrary dirty query roots.',
                                 'Eight distinct rank-eight source charts and their nested centre paths require a new complete query/port/hosting invoice.'],
            'conclusion':'No selected-supplier replacement or new kappa follows from the palette/walk query savings.',
            'scope':'Fresh source-bound shape/contract extraction only; no full native endpoint, owner, physical invoice or selected cold replay.'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=HERE.parent.parent)
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args();result=run(args.repo)
    path=HERE/'CALLER-SCREEN.json'
    if args.write_receipt:path.write_text(json.dumps(result,indent=2)+'\n')
    else:need(json.loads(path.read_text())==result,'caller screen receipt changed')
    print('PASS_RETAINED_CENTRE_CONTRACT_SCREEN centres=8 targets=112 signed_patterns=24 graph=2K4 full_native=NOT_RUN no_new_kappa')


if __name__=='__main__':main()
