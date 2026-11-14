#!/usr/bin/env python3
"""Read-only archival hash and recorded receipt checks; no research execution."""
import hashlib
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads((ROOT / path).read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)

manifest = read('MANIFEST.json')
require(manifest['schema'] == 'contact-rechart-archive-manifest/1' and len(manifest['files']) == 85, 'historical manifest denominator')
paths = set()
for row in manifest['files']:
    rel = Path(row['path'])
    require(not rel.is_absolute() and '..' not in rel.parts and str(rel) not in paths, 'invalid manifest path')
    paths.add(str(rel))
    p = ROOT / rel
    require(not p.is_symlink() and p.is_file() and p.stat().st_size == row['bytes'] and digest(p) == row['sha256'], str(rel))
actual_paths = {str(p.relative_to(ROOT)) for directory in ('original', 'corrected') for p in (ROOT / directory).rglob('*') if p.is_file()}
require(paths == actual_paths, 'complete historical file inventory')
for directory, expected in [('original', 'a5dcf94d69936c501ec2d630cdc45b30425756f79aeedee7730114ba877c265a'), ('corrected', '7d89fcb67f70d56bc3b8a4d6f457a88436181fb85f3533ea4603ece11d531d18')]:
    require(digest(ROOT / directory / 'FREEZE.json') == expected, directory + ' freeze digest')
    freeze = read(directory + '/FREEZE.json')
    require(len(freeze['files']) == 20, directory + ' freeze count')
    for row in freeze['files']:
        p = ROOT / directory / row['path']
        require(not p.is_symlink() and p.is_file() and p.stat().st_size == row['bytes'] and digest(p) == row['sha256'], directory + '/' + row['path'])
a = read('original/actual-run/RECEIPT.json'); ar = read('original/actual-run/RESOURCE.json')
require(a['status'] == 'FROZEN_RESOURCE_STOP' and a['visited_expansions'] == 0 and not a['new_kappa'] and not ar['within_declared_budget'], 'original stop flags')
b = read('corrected/actual-run/RECEIPT.json'); br = read('corrected/actual-run/RESOURCE.json'); v = read('corrected/actual-run/VISITED.json'); control = read('corrected/actual-control/RESULT.json')
require(b['status'] == 'NO_NOMINEE_IN_ONE_INPUT_THEN_OUTPUT_SWEEP' and b['visited_expansions'] == 2192 and not b['new_kappa'] and not b['nominee_word_emitted'] and not b['full_qualification_completed'], 'corrected receipt')
require(b['graph'] == {'nodes': 73423, 'edges': 137847, 'frames': 1096, 'mutable_helpers': 1018}, 'graph counts')
require(br['returncode'] == 0 and br['within_declared_budget'] and control['group_empty'], 'corrected resource flags')
require(v['coverage_initialized'] and v['population'] == 2192 and not v['unvisited'] and v['keys'] == [[mode, str(i)] for mode in ('entry', 'exit') for i in range(1096)], 'ordered visited keys')
# Static JSON selection only: these instruction arrays are never executed.
selection = read('SOURCE-SELECTION-1196.json')
selected_roles = {'1196', '885', '705', '1459', '943'}
require(set(selection['all_literal_touches_of_selected_roles']) == selected_roles and set(selection['roles']) == selected_roles, 'selected role denominator')
require([row['index'] for row in selection['local_cache_neighborhood']] == list(range(40714, 40725)), 'selected neighborhood denominator')
require([row['index'] for row in selection['selected_collateral_contacts']] == [37804, 37854, 37855, 38841], 'selected collateral denominator')
word = json.loads(gzip.decompress((ROOT / 'corrected/sources/WORD.json.gz').read_bytes()))
require(isinstance(word['public'], int) and isinstance(word['frames'], list), 'literal word schema')
require(hashlib.sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == selection['canonical_sha256'], 'selected canonical word')
require(selection['source_instruction_count'] == len(word['program']), 'selected instruction count')
def operands(instruction):
    return instruction[1:3] if instruction[0] in ('ADD', 'COPY') else instruction[1:2]
for role, records in selection['all_literal_touches_of_selected_roles'].items():
    owner = int(role)
    expected = [{'index': i, 'instruction': e} for i, e in enumerate(word['program']) if owner in operands(e)]
    require(records == expected, 'complete selected touches: ' + role)
    require(selection['roles'][role] == {'initial': word['initial'][owner], 'final': word['final'][owner], 'public': owner < word['public']}, 'selected boundaries: ' + role)
for records in (selection['local_cache_neighborhood'], selection['selected_collateral_contacts']):
    for row in records:
        require(row['instruction'] == word['program'][row['index']], 'selected local instruction')
require(set(selection['frames']) == {'3', '104', '105', '127', '189', '505', '508', '769', '802'}, 'selected frame IDs')
for frame, vectors in selection['frames'].items():
    require(vectors == word['frames'][int(frame)], 'selected frame vectors: ' + frame)
require(word['program'][41710] == ['ADD', 885, 943, '-1/2', 189], 'corrected later subtraction clock')
print('PASS archival hashes, freeze closure, recorded receipts, and literal JSON selection; no scalar instruction executed')
