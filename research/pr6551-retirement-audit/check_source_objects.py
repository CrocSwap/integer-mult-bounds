"""Compare retained inputs with Git source objects using an external commit pin.

This optional provenance check needs the publication and three source commits in
one Git object database. It never fetches or executes retained Python. The caller
must obtain the publication commit and checker through a trusted channel.
DLamdata with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

PACKAGE = 'research/pr6551-retirement-audit'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.run(['git', '--no-replace-objects', '-C', str(repo), *args],
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=30).stdout


def check(repo, publication, package):
    need(re.fullmatch('[0-9a-f]{40}', publication) is not None,
         'supply a trusted full publication commit, not a mutable branch name')
    frozen = git(repo, 'show', publication+':'+PACKAGE+'/RETAINED.json')
    need((package/'RETAINED.json').read_bytes() == frozen,
         'working manifest differs from the explicitly pinned publication')
    entries = json.loads(frozen)['files']
    rows = []
    for item in entries:
        relative = PurePosixPath(item['path'])
        need(not relative.is_absolute() and relative.parts[0] == 'source' and
             '..' not in relative.parts, 'confined retained path')
        source = item['source_commit']
        need(re.fullmatch('[0-9a-f]{40}', source) is not None, 'full source commit')
        spec = source+':'+item['source_path']
        original = git(repo, 'show', spec)
        retained = (package/item['path']).read_bytes()
        need(retained == original, 'retained bytes differ from source Git object: '+item['path'])
        sha = hashlib.sha256(original).hexdigest()
        blob = hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()
        need(sha == item['sha256'] and blob == item['git_blob'], 'source pin mismatch: '+item['path'])
        need(git(repo, 'rev-parse', spec).decode().strip() == blob, 'Git blob identity: '+item['path'])
        rows.append({'path': item['path'], 'source_commit': source,
                     'source_path': item['source_path'], 'git_blob': blob, 'sha256': sha})
    return {'status': 'PASS_RETAINED_SOURCE_GIT_OBJECTS', 'publication_commit': publication,
            'manifest_sha256': hashlib.sha256(frozen).hexdigest(), 'files': rows,
            'scope': 'Exact comparison to stored source Git objects under a caller-supplied trusted publication pin; no remote-access or mathematical claim.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--publication-commit', required=True)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(check(args.repository, args.publication_commit, args.package), indent=2, sort_keys=True))
