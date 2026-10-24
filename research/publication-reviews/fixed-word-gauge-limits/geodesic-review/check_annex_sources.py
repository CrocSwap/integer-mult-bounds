"""Check the frozen annex against its original source objects and parent files."""

import argparse
import ast
from collections import Counter
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def functions(path):
    return {node.name: node for node in ast.parse(path.read_text()).body
            if isinstance(node, ast.FunctionDef)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    repo, package = args.repo.resolve(), args.package.resolve()
    annex = package / 'annex/geodesic-boundary'
    review = Path(__file__).resolve().parent
    manifest = read_json(annex / 'ANNEX-MANIFEST.json')
    expected_manifest = '3ea3ad820cb4466d97aa0b79bd65c4e0fab2890015a69a4449ad7fe7f15966ff'
    require(digest((annex / 'ANNEX-MANIFEST.json').read_bytes()) == expected_manifest,
            'Exact accepted annex manifest')
    annex_files = {str(p.relative_to(annex)): digest(p.read_bytes())
                   for p in annex.rglob('*') if p.is_file()}
    require(set(annex_files) == set(manifest['files']) | {'ANNEX-MANIFEST.json'},
            'Complete annex file inventory')
    require(not any(p.is_symlink() for p in annex.rglob('*')), 'No annex symlinks')
    for name, expected in manifest['files'].items():
        require(annex_files[name] == expected, 'Annex file hash: ' + name)

    parent = read_json(annex / 'PARENT-SNAPSHOT.json')['files']
    primary_files = {str(p.relative_to(package)): digest(p.read_bytes())
                     for p in package.rglob('*')
                     if p.is_file() and 'annex' not in p.relative_to(package).parts}
    require(primary_files == parent, 'Exact complete primary file inventory')
    history = read_json(review / 'PRIMARY-HISTORY-PINS.json')
    require(primary_files['MANIFEST.json'] == history['primary_manifest_sha256'],
            'Accepted primary manifest')
    for item in history['primary_review_files']:
        data = (review.parent / item['path']).read_bytes()
        require(len(data) == item['bytes'] and digest(data) == item['sha256'],
                'Accepted primary review history: ' + item['path'])

    sources = read_json(annex / 'SOURCES.json')
    for item in sources['files']:
        frozen = (annex / item['path']).read_bytes()
        if item['kind'] == 'campaign':
            original = (repo / item['source_path']).read_bytes()
        else:
            require(item['kind'] == 'git', 'Known source kind')
            original = subprocess.check_output(
                ['git', '-C', str(repo), 'show', item['revision'] + ':' + item['source_path']])
        require(frozen == original, 'Exact original source: ' + item['path'])
        require(len(frozen) == item['bytes'] and digest(frozen) == item['sha256'],
                'Source manifest: ' + item['path'])
    for name, expected in sources['parent_inputs'].items():
        require(digest((package / name).read_bytes()) == expected, 'Parent input: ' + name)

    archive_check = read_json(annex / 'ARCHIVE-CHECK.json')
    archive = subprocess.check_output(['git', '-C', str(repo), 'show',
        archive_check['revision'] + ':' + archive_check['archive_path']])
    require(len(archive) == archive_check['archive_bytes'] and
            digest(archive) == archive_check['archive_sha256'], 'Complete historical archive')
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tar:
        for item in archive_check['members']:
            members = [m for m in tar.getmembers() if m.name == item['member']]
            require(len(members) == 1 and members[0].isfile(), 'Unique regular archive member')
            data = tar.extractfile(members[0]).read()
            require(data == (package / item['parent_path']).read_bytes(), 'Exact parent member')
            require(len(data) == item['bytes'] and digest(data) == item['sha256'], 'Member pin')

    math_functions = {}
    for item in read_json(annex / 'PORTABILITY.json'):
        old, new = (annex / item['source']), (annex / item['portable'])
        require(digest(old.read_bytes()) == item['source_sha256'] and
                digest(new.read_bytes()) == item['portable_sha256'], 'Checker source pins')
        old_functions, new_functions = functions(old), functions(new)
        require(set(old_functions) == set(new_functions), 'Same function inventory')
        same = []
        for name in item['unchanged_function_names']:
            require(ast.dump(old_functions[name]) == ast.dump(new_functions[name]),
                    'Exact mathematical function AST: ' + name)
            same.append(name)
        require(set(old_functions) == set(same) | set(item['io_functions_changed']),
                'Every function accounted for')
        math_functions[item['portable']] = same

    original_reader = functions(annex / 'frozen/lanes/temporal-reuse/review_wire_gauge.py')
    portable_reader = functions(package / 'checkers/review_wire_gauge.py')
    require(set(original_reader) == set(portable_reader), 'Parent reader function inventory')
    original_reader['run'].args.args = [a for a in original_reader['run'].args.args if a.arg != 'repo']
    for node in ast.walk(original_reader['run']):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'load_source':
            require(len(node.args) == 1 and isinstance(node.args[0], ast.Name)
                    and node.args[0].id == 'repo', 'Only the source argument changes')
            node.args = []
    same_reader = []
    for name in original_reader:
        if name == 'load_source':
            continue
        require(ast.dump(original_reader[name]) == ast.dump(portable_reader[name]),
                'Parent reader mathematical AST: ' + name)
        same_reader.append(name)

    links = []
    for destination in re.findall(r'\]\(([^)]+)\)', (annex / 'README.md').read_text()):
        if '://' not in destination:
            require((annex / destination.split('#')[0]).is_file(), 'Local README link: ' + destination)
            links.append(destination)
    result = {
        'status': 'PASS_INDEPENDENT_GEODESIC_ANNEX_SOURCES',
        'annex_manifest_sha256': expected_manifest,
        'annex_listed_files': len(manifest['files']),
        'annex_total_files': len(annex_files),
        'annex_bytes_including_manifest': sum(p.stat().st_size for p in annex.rglob('*') if p.is_file()),
        'primary_files_unchanged': len(primary_files),
        'primary_review_history_files_unchanged': len(history['primary_review_files']),
        'primary_manifest_sha256': primary_files['MANIFEST.json'],
        'exact_original_sources': len(sources['files']),
        'source_kinds': dict(Counter(item['kind'] for item in sources['files'])),
        'archive_check': archive_check,
        'unchanged_mathematical_functions': math_functions,
        'parent_reader_functions_equal_after_two_source_io_substitutions': same_reader,
        'readme_local_links': links,
        'annex_files_sha256': annex_files,
        'primary_files_sha256': primary_files,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
