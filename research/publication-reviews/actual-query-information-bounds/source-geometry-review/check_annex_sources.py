"""Check the source-geometry annex against its source files and old package."""

import argparse
import ast
from collections import Counter
import difflib
from hashlib import sha256
import json
from pathlib import Path
import re
import tarfile


def require(test, reason):
    if not test:
        raise ValueError(reason)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def check_records(root, records):
    for name, record in records.items():
        path = root / name
        require(path.stat().st_size == record['bytes'], 'File size: ' + name)
        require(digest(path) == record['sha256'], 'File hash: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    repo, package = args.repo.resolve(), args.package.resolve()
    annex = package / 'annexes/source-geometry'
    review = Path(__file__).resolve().parent
    baseline = read_json(review / 'HISTORICAL-PINS.json')
    check_records(package, baseline['package_files'])
    check_records(review.parent, baseline['prior_review_files'])
    old_paths = {str(p.relative_to(package)) for p in package.rglob('*')
                 if p.is_file() and not p.is_relative_to(annex)}
    require(old_paths == set(baseline['package_files']), 'Complete old package inventory')
    parent = read_json(annex / 'PARENT-SNAPSHOT.json')
    require(parent['files'] == baseline['package_files'], 'Independent parent snapshot match')
    manifest = read_json(annex / 'ANNEX-MANIFEST.json')
    require(digest(annex / 'ANNEX-MANIFEST.json') == args.manifest_sha256, 'Annex freeze')
    check_records(annex, manifest['files'])
    paths = {str(p.relative_to(annex)) for p in annex.rglob('*') if p.is_file()}
    require(paths == set(manifest['files']) | {'ANNEX-MANIFEST.json'}, 'Complete annex inventory')
    require(not any(p.is_symlink() for p in annex.rglob('*')), 'No annex symlinks')

    sources = read_json(annex / 'SOURCES.json')
    for name, record in sources['files'].items():
        require((annex / name).read_bytes() == (repo / record['original_path']).read_bytes(),
                'Exact original source: ' + name)
    check_records(annex, sources['files'])
    check_records(package, sources['parent_runtime_dependencies'])
    prior_sources = read_json(review / 'REVIEWED-SOURCE-PINS.json')
    campaign = repo / 'work/centre-encoding-campaign-20261014'
    check_records(campaign, prior_sources['campaign_relative_sources'])

    archive_check = read_json(annex / 'ARCHIVE-CHECK.json')
    archive_path = repo / archive_check['archive_original_path']
    require(archive_path.stat().st_size == archive_check['archive_bytes'], 'Full archive size')
    require(digest(archive_path) == archive_check['archive_sha256'], 'Full archive hash')
    with tarfile.open(archive_path) as archive:
        for item in archive_check['unique_regular_members']:
            matches = [m for m in archive.getmembers() if m.name == item['archive_member']]
            require(len(matches) == 1 and matches[0].isfile(), 'Unique regular member')
            data = archive.extractfile(matches[0]).read()
            require(data == (package / item['parent_path']).read_bytes(), 'Exact parent archive member')
            require(len(data) == item['bytes'] and sha256(data).hexdigest() == item['sha256'],
                    'Archive member pin')

    portability = read_json(annex / 'PORTABILITY.json')
    reviewed_portability = read_json(review / 'PORTABILITY-REVIEWED-PINS.json')
    require(digest(annex / 'PORTABILITY.patch') == reviewed_portability['patch_sha256'],
            'The complete patch was manually reviewed')
    ast_checks, patch = [], []
    for job in portability['checks']:
        old, new = annex / job['frozen_script'], annex / job['portable_script']
        require(digest(old) == job['original_sha256'] and digest(new) == job['portable_sha256'],
                'Portable source pins: ' + job['name'])
        require(digest(new) == reviewed_portability['portable_scripts'][job['portable_script']],
                'The portable main function was manually reviewed: ' + job['name'])
        functions = []
        for path in (old, new):
            functions.append({node.name: ast.dump(node, include_attributes=False)
                              for node in ast.parse(path.read_text()).body
                              if isinstance(node, ast.FunctionDef) and node.name != 'main'})
        require(functions[0] == functions[1], 'All non-main function ASTs: ' + job['name'])
        require(len(functions[0]) == job['function_count'], 'Function count: ' + job['name'])
        patch.extend(difflib.unified_diff(old.read_text().splitlines(True),
                                         new.read_text().splitlines(True),
                                         fromfile=job['frozen_script'], tofile=job['portable_script']))
        ast_checks.append({'name': job['name'], 'function_names': sorted(functions[0]),
                           'original_sha256': digest(old), 'portable_sha256': digest(new)})
    require(''.join(patch) == (annex / 'PORTABILITY.patch').read_text(), 'Complete portability diff')
    links = []
    for doc in ('README.md', 'NOTICE.md'):
        for target in re.findall(r'\]\(([^)]+)\)', (annex / doc).read_text()):
            if '://' not in target:
                require((annex / target.split('#')[0]).is_file(), 'Local document link: ' + target)
                links.append({'document': doc, 'target': target})
    result = {
        'status': 'PASS_INDEPENDENT_SOURCE_GEOMETRY_CLOSURE',
        'annex_manifest_sha256': args.manifest_sha256,
        'annex_listed_files': len(manifest['files']),
        'annex_total_files': len(paths),
        'annex_bytes': sum((annex / path).stat().st_size for path in paths),
        'old_package_files_unchanged': len(baseline['package_files']),
        'prior_review_files_unchanged': len(baseline['prior_review_files']),
        'exact_original_source_files': len(sources['files']),
        'original_source_roles': dict(Counter(x['role'] for x in sources['files'].values())),
        'parent_runtime_inputs': sources['parent_runtime_dependencies'],
        'complete_archive_check': archive_check,
        'portable_checker_function_checks': ast_checks,
        'all_main_changes_reviewed_as_io_only': True,
        'local_document_links': links,
        'no_git_network_or_external_program_used': True,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
