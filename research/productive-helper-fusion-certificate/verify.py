#!/usr/bin/env python3
"""Read-only exact source/rewrite/fusion replay. Apache-2.0.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agents. Source/algorithm attribution is retained in README.md and SOURCES.json.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
SOURCE_PAYLOAD = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'

def need(value, message):
    if not value:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def module(name):
    spec = importlib.util.spec_from_file_location('productive_' + name, HERE/(name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def run():
    pins = json.loads((HERE/'SOURCES.json').read_bytes())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha((ROOT/row['path']).read_bytes()) == row['sha256'],
                 'Changed pinned input: ' + row['path'])
    raw_source = gzip.decompress((ROOT/SOURCE).read_bytes())
    raw_word = gzip.decompress((HERE/'COMBINED-WORD.json.gz').read_bytes())
    wr = gzip.decompress((HERE/'WITNESS.json.gz').read_bytes())
    fr = gzip.decompress((HERE/'FLOW.json.gz').read_bytes())
    source, word, witness, flow = map(json.loads, (raw_source, raw_word, wr, fr))
    trace = json.loads((HERE/'COMMUTATION.json').read_bytes())
    rewrite, fusion = module('check_rewrite'), module('check_fusion')
    directions = rewrite.verify(source, word, trace, SOURCE_PAYLOAD)
    rewrite_controls = rewrite.controls(source, word, trace, SOURCE_PAYLOAD)
    for row in directions.values():
        need((row['merges'], row['cancelled_pairs'], row['removed_scalar_events']) == (70,28,98),
             'Exact declared scalar rewrite')
    fusion.source_bytes(raw_word)
    need(sha(wr) == flow['proposal_source_sha256'], 'Witness bound by flow certificate')
    linear, pair, graph = fusion.reconstruct_energy(witness, word, 'joint-helper')
    fusion.graph_energy(flow, linear, pair)
    flow_result = fusion.verify_flow(flow)
    controls = fusion.rejection_controls(raw_word, witness, flow, 'joint-helper')
    shared = module('check_shared')
    native_metadata = json.loads((HERE/'SHARED-MAPS.json').read_bytes())
    need(set(native_metadata) == {'selected_late_maps', 'prelude_lines',
         'frozen_earlier_warp_nodes', 'excluded_proposals', 'changed_native_tables'},
         'Native metadata contains only checked occurrence fields')
    shared_witness = dict(witness, **native_metadata)
    shared_result = shared.verify(word, shared_witness)
    shared_result['corruption_controls'] = shared.controls(word, shared_witness)
    shared_result['small_formula_calibration'] = shared.small_formula_audit()
    result = {
        'status':'PASS_PRODUCTIVE_HELPER_FUSION_CERTIFICATE',
        'new_kappa':None,
        'source_payload_sha256':sha(raw_source),
        'combined_payload_sha256':sha(raw_word),
        'witness_payload_sha256':sha(wr),
        'flow_payload_sha256':sha(fr),
        'rewrite':directions,
        'rewrite_controls':rewrite_controls,
        'graph':graph,
        'flow':flow_result,
        'fusion_controls':controls,
        'shared_native_minima':shared_result,
        'scope':'Forward 1079-choice canonical chart family, joint helper boundaries and all compatible 72 late native G maps with fixed earlier boundaries; no new physical supplier or global chart optimum.'
    }
    # Normalize dictionary keys to JSON's string representation before comparison.
    return json.loads(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path, help='Explicitly generate a receipt instead of comparing it')
    args = parser.parse_args()
    result = run()
    if args.write_result:
        args.write_result.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    else:
        need(result == json.loads((HERE/'RESULT.json').read_bytes()), 'Deterministic result differs from retained receipt')
    print(result['status'])
    print(json.dumps({'choices':result['graph']['proposals'],
                      'changed_helper_endpoints':result['graph']['helper_endpoints_changed'],
                      'source_arcs':result['flow']['arcs'],
                      'saving_interval':result['flow']['interval_C'],
                      'minimum_polynomial':result['flow']['minimum_polynomial'],
                      'new_kappa':None},sort_keys=True))
