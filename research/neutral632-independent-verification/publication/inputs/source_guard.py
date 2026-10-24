"""Exact working bytes, portable Git origins and scoped inherited evidence."""
import base64
import gzip
import hashlib
import json
import stat
from pathlib import Path, PurePosixPath

MAIN = '1ec1119972c9aefe42525172d07b332fcff81cb4'
MAIN_TREE = 'bfb420045d2bc04dd026b5020aea84d547873ef4'
MODE_POLICY = {
    'declared_modes': [420, 493],
    'allowed_actual_modes': 'declared mode or declared mode & ~0o222',
    'scope': 'Only write bits may be removed for read-only transport; all read and execute bits remain unchanged.',
}
HEADS = {
    'canonical': MAIN,
    'pr5402': '3348fccea855082786d5f0fc5558b73d4974e745',
    'pr5398': '174fb211493b43a42210434083e9702b4fb7a2ce',
    'pr5400': '7ea72fb692cbfd64fea556de84327bbf88555986',
    'pr5407': 'b62252c61113d2863b36ce2419aa81a07f393c42',
}
CLAIMS_EXPECTED = json.loads("{\"additional_global_normalizer_fieldmaps\":30368,\"assumptions\":[{\"id\":\"native_all_columns\",\"statement\":\"Retained native operators, phase conventions, spectators and whole-job adapters work at every positive column multiplicity.\"},{\"id\":\"owned_erasure\",\"statement\":\"Owned streams and suspended centers obey the retained allocation, erasure and ownership contracts.\"},{\"id\":\"compiler\",\"statement\":\"The finite mixed-target compiler and chronological product, completion and splitting satisfy the retained uniform closure contract.\"},{\"id\":\"precision_tape\",\"statement\":\"Retained fixed-tape movement and precision/storage prescriptions apply to the new fixed finite template.\"},{\"id\":\"analytic_recovery\",\"statement\":\"Analytic decomposition, fine-prime avoidance and exact integer recovery follow the retained upstream/outer framework.\"}],\"candidate_kappa\":\".003027288235\",\"canonical_main\":\"1ec1119972c9aefe42525172d07b332fcff81cb4\",\"comparison_kappa\":\".00302728823\",\"conjunction_sha256\":\"2172779f65f16b073a25e393bb0ac9cc320135360ad57c6f576917cda1ffd106\",\"construction_credit\":\"Dillon (@dillona), PR5402, supplies the unrestricted coupled provider; Ali Romman supplies PR5383 cached-center identities and PR5398 direct backward controller. Chris R/Clear1nsight supplies PR5407 independent component review, PR5400 predecessor caller review and this completion. All existing notices and earlier contributor credit are retained.\",\"gain\":\"1/200000000000\",\"gain_type\":\"compiler headroom only; no recursive economic saving\",\"global_extra_paid_H8\":144,\"global_extra_productive_H8\":144,\"global_paid_count\":64260,\"global_productive_count\":10928,\"global_route_plan_sha256\":\"a02e79fb4615f4f987e3b3617c2b42eea2c1d7415cc66fa702a8b0cd28e6387e\",\"implementation\":\"NEUTRAL-CALLER-v16c raw macro/physical IDs plus WHOLECALLER-PLAN-v1 authoritative common145 geometry and chronological target/IDLE route words; joined by CALLER-BINDING-RESULT-v1.\",\"kappa_maximality_claimed\":false,\"local_original_arbitrary_inputs\":632,\"local_owned_arbitrary_inputs\":17,\"local_owned_zero_returns\":17,\"local_positive_helper_count\":408,\"native_provider\":\"Unchanged PR5402 unrestricted component accepted by PR5407 is authenticated reuse; no new full native provider replay.\",\"new_contribution\":\"A complete 632-input local caller restoring the eight coupled modes through eight explicitly paid rank-8 jobs, composed with the existing direct controller, with a fresh compiler-headroom candidate.\",\"new_unconditional_or_formal_kernel_theorem\":false,\"raw_ceiling_changed\":false,\"raw_global_private_fields\":418,\"raw_signed_profile_changed\":false,\"same_selected_assumptions_required\":true,\"schema_version\":1,\"scientific_status\":\"PASS_CONDITIONAL_COMPLETE_CONJUNCTION\",\"selected_baseline\":\".0030217758\",\"selected_record_changed\":false,\"selection_authorized\":false,\"tested_saving\":\".003027288245\"}")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def regular(root, relative):
    parts = PurePosixPath(relative).parts
    require(parts and not relative.startswith('/')
            and str(PurePosixPath(relative)) == relative
            and all(p not in ('', '.', '..') for p in parts),
            'Noncanonical package path: ' + relative)
    path = root
    for part in parts:
        path = path / part
        require(not path.is_symlink(), 'Symlink input component: ' + relative)
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode),
            'Missing regular input: ' + relative)
    require(path.stat().st_nlink == 1, 'Hardlinked input alias: ' + relative)
    return path


def oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode()
                        + b'\0' + raw).hexdigest()


def tree_entries(raw):
    entries, offset = {}, 0
    while offset < len(raw):
        blank = raw.index(b' ', offset)
        zero = raw.index(b'\0', blank + 1)
        require(zero + 21 <= len(raw), 'Truncated raw tree')
        mode = raw[offset:blank].decode()
        name = raw[blank + 1:zero].decode('utf8')
        require(name and '/' not in name and name not in ('.', '..')
                and name not in entries, 'Invalid raw tree member')
        entries[name] = (mode, raw[zero + 1:zero + 21].hex())
        offset = zero + 21
    require(offset == len(raw), 'Truncated raw tree end')
    return entries


def origin_proof(root, relative, expected_head):
    proof = json.loads(regular(root, relative).read_bytes())
    require(proof['schema'] == 'raw-git-selected-path-origins/v1'
            and proof['commit'] == expected_head, 'Wrong exact source head')
    objects = {}
    for identity, row in proof['objects'].items():
        require(len(identity) == 40 and row['type'] in ('commit', 'tree', 'blob'),
                'Invalid raw Git object kind')
        raw = base64.b64decode(row['base64'], validate=True)
        require(len(raw) == row['bytes'] and oid(row['type'], raw) == identity,
                'Raw Git object hash or length changed')
        objects[identity] = (row['type'], raw)

    def obj(identity, kind):
        require(identity in objects and objects[identity][0] == kind,
                'Missing raw Git origin object')
        return objects[identity][1]

    commit = obj(expected_head, 'commit')
    first = commit.split(b'\n', 1)[0].split()
    require(len(first) == 2 and first[0] == b'tree', 'Commit root tree missing')
    root_tree = first[1].decode()
    require(root_tree == proof['root_tree'], 'Changed commit root tree')
    files = {}
    for row in proof['files']:
        name = row['path']
        parts = PurePosixPath(name).parts
        require(name == str(PurePosixPath(name)) and parts
                and not name.startswith('/') and '..' not in parts
                and name not in files, 'Invalid or duplicate source path')
        require(len(row['tree_chain']) == len(parts), 'Wrong Merkle path depth')
        current = root_tree
        for part, step in zip(parts, row['tree_chain']):
            require(step['tree'] == current and step['name'] == part,
                    'Changed source tree chain')
            entries = tree_entries(obj(current, 'tree'))
            require(part in entries, 'Source tree member missing')
            mode, current = entries[part]
            require((step['mode'], step['object']) == (mode, current),
                    'Changed source tree binding')
        require(mode in ('100644', '100755') and current == row['git_blob'],
                'Source file mode or blob mismatch')
        raw = obj(current, 'blob')
        require(len(raw) == row['bytes']
                and hashlib.sha256(raw).hexdigest() == row['sha256'],
                'Source blob digest mismatch')
        files[name] = {'sha256': row['sha256'], 'git_blob': current,
                       'git_mode': mode, 'bytes': len(raw)}
    return {'head': expected_head, 'root_tree': root_tree,
            'files': files, 'objects': len(objects)}


def source_history(root):
    history = json.loads(regular(root, 'SOURCE-HISTORY.json').read_bytes())
    require(history['schema'] == 'neutral-completion-source-history/1'
            and history['canonical_main'] == MAIN
            and history['canonical_tree'] == MAIN_TREE,
            'Wrong canonical source-history anchor')
    require(history['side_pr_heads_asserted_ancestors'] is False,
            'Unsupported side-head ancestry claim')
    require(history['mode_policy'] == MODE_POLICY,
            'Changed portable read-only mode policy')
    require(set(history['origin_proofs']) == set(HEADS),
            'Missing or extra declared source origin')
    proofs = {label: origin_proof(root, history['origin_proofs'][label], head)
              for label, head in HEADS.items()}
    require(proofs['canonical']['root_tree'] == MAIN_TREE,
            'Canonical anchor tree mismatch')
    seen = set()
    for binding in history['copy_bindings']:
        path = binding['package_path']
        require(path not in seen, 'Duplicate source copy binding')
        seen.add(path)
        label, origin_path = binding['origin'], binding['source_path']
        require(label in proofs and origin_path in proofs[label]['files'],
                'Unknown selected source origin')
        source = proofs[label]['files'][origin_path]
        raw = regular(root, path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == source['sha256']
                and len(raw) == source['bytes']
                and oid('blob', raw) == source['git_blob'],
                'Copied source differs from raw Git origin: ' + path)
    return {'status': 'PASS_PORTABLE_EXACT_SOURCE_ORIGINS',
            'canonical_main': MAIN, 'canonical_tree': MAIN_TREE,
            'copy_bindings': len(seen),
            'side_pr_ancestry': 'No ancestry assertion; exact side-head bytes only.',
            'mode_policy': MODE_POLICY,
            'origins': {label: {'head': proof['head'],
                                'files': len(proof['files']),
                                'objects': proof['objects']}
                        for label, proof in proofs.items()}}


def check(root):
    root = Path(root).absolute()
    for part in (root, *root.parents):
        require(not part.is_symlink(), 'Symlink package ancestor')
    regular(root, 'verify.py')
    manifest = json.loads(regular(root, 'SOURCE-BINDINGS.json').read_bytes())
    require(manifest['schema'] == 'neutral-completion-bindings/1',
            'Wrong working-input manifest schema')
    rows = manifest['files']
    paths = [row['path'] for row in rows]
    require(len(paths) == len(set(paths))
            and 'verify.py' not in paths and 'SOURCE-BINDINGS.json' not in paths,
            'Duplicate or cyclic working-input inventory')
    actual = set()
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'Symlink anywhere in package')
        require(path.name != '__pycache__' and path.suffix not in ('.pyc', '.pyo'),
                'Bytecode cache in frozen package')
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
        else:
            require(path.is_dir(), 'Special input in frozen package')
    require(actual == set(paths) | {'verify.py', 'SOURCE-BINDINGS.json'},
            'Missing or undeclared working input')
    digests = {}
    for row in rows:
        path = regular(root, row['path'])
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(type(row['mode']) is int and row['mode'] in (420, 493)
                and stat.S_IMODE(path.stat().st_mode)
                in (row['mode'], row['mode'] & ~0o222),
                'Changed input mode: ' + row['path'])
        require(len(raw) == row['bytes'] and digest == row['sha256'],
                'Changed input bytes: ' + row['path'])
        if row.get('payload_sha256'):
            require(hashlib.sha256(gzip.decompress(raw)).hexdigest()
                    == row['payload_sha256'], 'Changed compressed payload')
        digests[row['path']] = digest
    for name, digest in manifest.get('frozen_engines', {}).items():
        require(digests.get(name) == digest, 'Changed mathematical engine')
    claims = json.loads(regular(root, 'CLAIMS.json').read_bytes())
    require(claims == CLAIMS_EXPECTED, 'Changed or unsupported scientific scope')
    custody = source_history(root)
    return {'status': 'PASS_ACTUAL_WORKING_INPUT_BINDINGS', 'files': len(rows),
            'custody': custody, 'source_history': custody,
            'mode_policy': MODE_POLICY, 'digests': digests}
