"""Freeze the connected source successor; issue no runtime records or grants."""
import ast
import hashlib
import json
from pathlib import Path

W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
D = Path(__file__).resolve().parent
OLD = W / 'outputs/connected-caller-assembly-20261107T2053Z/repair-v3'
NEW = D / 'successor'
OLD_MANIFEST_SHA = 'bb8f5f74089ecb9ce26a44652ec4e655fb1d3c17929e593b28eb4cc814f8ebc5'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()

def pin(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=sha(raw), mode=0o444)

def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.chmod(0o600)
    path.write_bytes(raw)
    path.chmod(0o444)

def verify(row):
    p = Path(row['path'])
    raw = p.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], str(p)
    assert p.stat().st_mode & 0o777 == row['mode']
    return raw

def relocate(value):
    if isinstance(value, str):
        return value.replace(str(OLD), str(NEW))
    if isinstance(value, list):
        return [relocate(v) for v in value]
    if isinstance(value, dict):
        return {relocate(k): relocate(v) for k, v in value.items()}
    return value

def replace_assignment(text, name, expected, replacement):
    tree = ast.parse(text)
    matches = [n for n in tree.body if isinstance(n, ast.Assign)
               and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
               and n.targets[0].id == name]
    assert len(matches) == 1, (name, 'one exact module assignment')
    n = matches[0]
    current = ast.get_source_segment(text, n)
    assert current == expected, (name, current)
    lines = text.splitlines(True)
    lines[n.lineno - 1:n.end_lineno] = [replacement + '\n']
    return ''.join(lines)

def prepare():
    assert not NEW.exists(), 'immutable successor already exists'
    original_bytes = (OLD / 'implementation/bindings/SOURCE-MANIFEST-v2.json').read_bytes()
    assert sha(original_bytes) == OLD_MANIFEST_SHA
    original = json.loads(original_bytes)
    NEW.mkdir()
    origins = {}
    # Only selected ordinary source/profile leaves and declared stage members.
    for row in [*original['source_pins'].values(), *original['profiles'].values(),
                *original['control_pins']]:
        raw = verify(row)
        p = Path(row['path'])
        if p.is_relative_to(OLD):
            q = NEW / p.relative_to(OLD)
            if q.exists():
                assert q.read_bytes() == raw
            else:
                put(q, raw)
            origins[str(q)] = row
    for leaf in ('joined-full-candidate-v1', 'joined-full-candidate-refusal-v1'):
        base = OLD / 'implementation/bindings/stages' / leaf
        declared = json.loads((base / 'STAGE.json').read_bytes())
        for rel, row in declared['files'].items():
            assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
            p = base / rel
            raw = verify(dict(path=str(p), bytes=p.stat().st_size, **row))
            q = NEW / p.relative_to(OLD)
            if q.exists():
                assert q.read_bytes() == raw
            else:
                put(q, raw)
    # All spellings of this exact selected predecessor root, including W + '/outputs/...'.
    old_relative = str(OLD.relative_to(W)).encode()
    new_relative = str(NEW.relative_to(W)).encode()
    for p in sorted((NEW / 'implementation').rglob('*')):
        if p.is_file() and '/stages/' not in str(p) and p.suffix in ('.py', '.json'):
            raw = p.read_bytes().replace(str(OLD).encode(), str(NEW).encode())
            raw = raw.replace(old_relative, new_relative)
            put(p, raw)
    association = NEW / 'implementation/bindings/environment_association.py'
    expected = "R = W + '/outputs/connected-caller-assembly-20261107T2053Z'"
    replacement = 'R = W + ' + repr('/' + str(NEW.relative_to(W)))
    put(association, replace_assignment(association.read_text(), 'R', expected, replacement).encode())
    entry = NEW / 'implementation/source/candidate_entry.py'
    text = entry.read_text()
    tree = ast.parse(text)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
             and n.func.value.id == 'subprocess' and n.func.attr == 'Popen']
    assert len(calls) == 1
    cwd = [k.value for k in calls[0].keywords if k.arg == 'cwd']
    assert len(cwd) == 1 and isinstance(cwd[0], ast.Name) and cwd[0].id == 'stage'
    n = cwd[0]
    lines = text.splitlines(True)
    line = lines[n.lineno - 1]
    lines[n.lineno - 1] = line[:n.col_offset] + 'READ_ROOT' + line[n.end_col_offset:]
    put(entry, ''.join(lines).encode())
    freeze(original, origins)

def freeze(original, origins):
    source = NEW / 'implementation/source'
    common = pin(source / 'run_guarded_v3.py')
    supervisor = source / 'fresh_supervisor.py'
    old_common = original['source_pins']['common_runner']['sha256']
    put(supervisor, replace_assignment(supervisor.read_text(), 'RUNNER_SHA',
        'RUNNER_SHA = ' + repr(old_common), 'RUNNER_SHA = ' + repr(common['sha256'])).encode())
    for p in (NEW / 'implementation').rglob('*.py'):
        if '/stages/' not in str(p):
            ast.parse(p.read_bytes(), filename=str(p))
    entry = pin(source / 'candidate_entry.py')
    receiver = pin(source / 'full_result_receiver.py')
    relay = pin(source / 'bounded_relay.py')
    stages = {}
    for mode, leaf in [('normal', 'joined-full-candidate-v1'),
                       ('optimized', 'joined-full-candidate-refusal-v1')]:
        base = NEW / 'implementation/bindings/stages' / leaf
        put(base / 'integration/candidate_entry.py', (source / 'candidate_entry.py').read_bytes())
        declared = json.loads((base / 'STAGE.json').read_bytes())
        declared['files']['integration/candidate_entry.py'] = dict(sha256=entry['sha256'], mode=0o444)
        declared['runner_sha256'] = common['sha256']
        declared['full_receiver_sha256'] = receiver['sha256']
        declared['relay_sha256'] = relay['sha256']
        put(base / 'STAGE.json', encode(declared))
        stages[mode] = pin(base / 'STAGE.json')
    queue = NEW / 'implementation/bindings/control/IndependentPrefixDATAComposedV1-QUEUE.json'
    q = json.loads(queue.read_bytes())
    for case in q['cases']:
        case['stage_sha256'] = stages[case['job']]['sha256']
    put(queue, encode(q))
    packet_path = NEW / 'implementation/bindings/SELECTED-SOURCE-PACKET-v1.json'
    packet = json.loads(packet_path.read_bytes())
    for path in packet['files']:
        row = pin(Path(path))
        packet['files'][path] = {k:v for k,v in row.items() if k != 'path'}
    put(packet_path, encode(packet))
    manifest = relocate(original)
    for key, row in manifest['source_pins'].items():
        manifest['source_pins'][key] = pin(Path(row['path']))
    for key, row in manifest['profiles'].items():
        manifest['profiles'][key] = pin(Path(row['path']))
    assert manifest['source_pins']['runner'] == manifest['source_pins']['common_runner']
    assert manifest['source_pins']['private_loader']['path'] == str(NEW / 'implementation/bindings/private_loader.py')
    put(NEW / 'implementation/bindings/SOURCE-MANIFEST-v2.json', encode(manifest))
    receipt = dict(schema='caller-binding-successor-v1', predecessor_manifest_sha256=OLD_MANIFEST_SHA,
        manifest=pin(NEW / 'implementation/bindings/SOURCE-MANIFEST-v2.json'),
        source_roles=len(manifest['source_pins']), profiles=len(manifest['profiles']),
        historical_controls=len(manifest['control_pins']), stages=stages,
        substantive_repairs=['exact selected association loader root', 'native launch preserves READ_ROOT cwd'],
        all_other_runtime_changes='exact selected-root relocation and dependent pins only',
        runtime_records_or_grants_issued=False, execution_permission=False,
        original_credit_delta=0, physical_costs='OPEN_NOT_ZERO', origins=origins)
    put(NEW / 'control/ASSEMBLY-v1.json', encode(receipt))
    print(json.dumps({k:v for k,v in receipt.items() if k != 'origins'}, indent=2))

if __name__ == '__main__':
    prepare()
