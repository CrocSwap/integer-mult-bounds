"""Read-only archive byte/static check. Never import or execute archived code."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import stat


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    require(manifest['self_excluded'] == 'MANIFEST.json', 'manifest exclusion differs')
    rows = manifest['files']
    names = [r['path'] for r in rows]
    require(len(names) == len(set(names)), 'duplicate manifest path')
    actual = []
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'symlink in archive')
        if path.is_file():
            actual.append(path.relative_to(root).as_posix())
    require(sorted(actual) == sorted(names + ['MANIFEST.json']), 'file inventory differs')
    total = 0
    for row in rows:
        p = PurePosixPath(row['path'])
        require(not p.is_absolute() and str(p) == row['path'] and
                all(x not in ('', '.', '..') for x in p.parts), 'unsafe manifest path')
        path = root / row['path']
        mode = path.stat().st_mode
        require(stat.S_ISREG(mode) and not mode & 0o111, 'nonregular/executable archived file')
        require(row['mode'] == '100644', 'manifest mode differs')
        data = path.read_bytes()
        require(len(data) == row['bytes'], 'size differs: ' + row['path'])
        require(sha256(data) == row['sha256'], 'sha256 differs: ' + row['path'])
        require(git_blob(data) == row['git_blob'], 'Git blob differs: ' + row['path'])
        data.decode('utf-8')
        total += len(data)
    mapping = json.loads((root / 'SOURCE-MAP.json').read_text())
    by_name = {r['path']: r for r in rows}
    for row in mapping['files']:
        require(row['path'] in by_name, 'unlisted source map entry')
        require(all(row[k] == by_name[row['path']][k]
                    for k in ['bytes', 'sha256', 'git_blob', 'mode']), 'source map pin differs')
        require(row['archived_code_execution'] is False, 'source execution claim')
    domain = json.loads((root / 'evidence/c05-consumer-domain/DOMAIN-v1.json').read_text())
    witness = json.loads((root / 'ROLE-PROOF.json').read_text())
    for key in ['resolved_direct_domain', 'Gamma_schema_fixed_before_inventory_and_results',
                'linked_native_domain', 'callchain_and_dataflow', 'admission_resolution',
                'precise_open_predicates']:
        require(witness[key] == domain[key], 'static witness differs: ' + key)
    direct = domain['resolved_direct_domain']
    require(direct['ordered_roles'] == ['pyinit_failure', 'exec_failure'], 'roles differ')
    require(len(direct['D_variant']) == 2 and len(direct['six_literal_role_occurrences']) == 6,
            'direct domain count differs')
    require(all('-nostartfiles' in row['argv'] for row in direct['D_variant']),
            'variant option differs')
    native = domain['linked_native_domain']['D_native_packet']
    require(len(native) == 3 and all('-nostartfiles' not in row['argv'] for row in native),
            'separate native triple differs')
    variant = (root / 'snapshot/original/variant/variant_driver_v1.py.txt').read_text()
    require('# native_packet.prepare, api[2], create_dynamic, exec_dynamic or a fixture loader.'
            in variant, 'build-only source anchor missing')
    require("command = ['/usr/bin/x86_64-linux-gnu-gcc-13', '-nostartfiles', '-shared',"
            in variant, 'variant command anchor missing')
    require("command, directory, 'control', 15, context)" in variant,
            'variant helper anchor missing')
    helper = (root / 'snapshot/original/cold_helper/cold_build_evidence.py.txt').read_text()
    require('process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,\n'
            '                                   close_fds=True, start_new_session=False, preexec_fn=callback)'
            in helper, 'inherited actual context source anchor missing')
    archive = json.loads((root / 'ARCHIVE.json').read_text())
    for obj in [domain, witness, archive]:
        require(obj['full_C05'] is False and obj['full_V03'] is False and
                obj['runtime_admission'] is False and obj['original_activity_credit_added'] == 0
                and obj['costs'] == 'OPEN_NOT_ZERO', 'scope/credit boundary differs')
    require(archive['original_completion_percent'] == 43.5, 'progress boundary differs')
    print(json.dumps({'status': 'PASS', 'scope': 'archive bytes and stated static anchors only',
                      'files': len(actual), 'manifest_payload_bytes': total,
                      'source_map_entries': len(mapping['files']),
                      'direct_variant_commands': 2, 'separate_linked_native_commands': 3,
                      'archived_code_imported_or_executed': False,
                      'scientific_or_runtime_admission': False}, sort_keys=True))


if __name__ == '__main__':
    main()
