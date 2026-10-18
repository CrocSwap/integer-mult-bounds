#!/usr/bin/env python3
"""Offline provenance/reconciliation integrity; --git-blobs checks retained source bytes.

This is not a multiplication-theorem verifier and does not replay historical CI.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def load(name):
    b = (HERE/name).read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)


def oid(kind, raw):
    return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def tree_oid(files):
    tree = {}
    for f in files:
        p = PurePosixPath(f['path'])
        require(not p.is_absolute() and '..' not in p.parts and str(p) == f['path'], 'Unsafe source path')
        node = tree
        for part in p.parts[:-1]:
            node = node.setdefault(part, {})
        require(p.name not in node, 'Duplicate source path')
        require(f['mode'] in ('100644', '100755'), 'Unexpected source mode')
        node[p.name] = (f['mode'], f['blob'])
    def encode(node):
        entries = []
        for name, value in node.items():
            directory = isinstance(value, dict)
            mode, sha = ('40000', encode(value)) if directory else value
            entries.append(((name+('/' if directory else '')).encode(), mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(sha)))
        return oid('tree', b''.join(raw for key, raw in sorted(entries)))
    return encode(tree)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-blobs', action='store_true')
    args = parser.parse_args()
    manifest = load('MANIFEST.json')
    for path, sha in manifest['files'].items():
        require(hashlib.sha256((HERE/path).read_bytes()).hexdigest() == sha, 'Changed evidence: '+path)
    for path, sha in manifest.get('integrated_files', {}).items():
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, 'Changed integrated source: '+path)
    source = load('SOURCES.json.gz')['pull_requests']
    snapshot = {r['number']:r for r in load('STARTING-SNAPSHOT.json')['pull_requests']}
    decisions = {r['number']:r for r in load('DISPOSITIONS.json')['pull_requests']}
    review = load('REVIEW.json')
    coverage = load('FILE-DISPOSITIONS.json.gz')
    require(len(source) == len(snapshot) == len(decisions) == 100, 'Frozen batch cardinality')
    require(set(snapshot) == set(decisions) == {r['number'] for r in source}, 'Frozen batch identity')
    blobs = {}
    for r in source:
        n=r['number']; d=decisions[n]
        require(r['head'] == snapshot[n]['headRefOid'] == d['reviewed_head'], f'#{n}: head mismatch')
        require(r['metadata']['author'] == snapshot[n]['author'], f'#{n}: lost author')
        require(oid('commit', r['commit_object'].encode()) == r['head'], f'#{n}: commit authentication')
        require(r['commit_object'].startswith('tree '+r['tree']+'\n'), f'#{n}: commit tree')
        require(tree_oid(r['files']) == r['tree'], f'#{n}: complete original tree')
        require(str(n) in review and review[str(n)]['mechanism'], f'#{n}: missing scoped review')
        expected={(f['path'],f['status'],f['old_blob'],f['new_blob']) for f in r['changed_files']}
        actual={(f['path'],f['status'],f['old_blob'],f['new_blob']) for f in coverage[str(n)]}
        require(len(coverage[str(n)])==len(expected) and actual==expected, f'#{n}: incomplete original diff coverage')
        require(all(f['treatment'] for f in coverage[str(n)]), f'#{n}: file without treatment')
        flags=d['review_completion']
        require(set(flags)=={'changed_file_coverage','scoped_mechanism_review','required_execution_complete','published'}
                and all(type(v) is bool for v in flags.values()), f'#{n}: malformed completion flags')
        if d['disposition']=='incorporated':
            require(all(flags.values()) and d['unresolved_question'] is None, f'#{n}: premature incorporation')
        if d.get('closure'):
            require(d['github_state'] in ('CLOSED','MERGED'), f'#{n}: closure state')
            require(d['current_head']==r['head'], f'#{n}: closure on changed head')
        for f in r['files']:
            old=blobs.setdefault(f['blob'], (f['sha256'],f['bytes']))
            require(old==(f['sha256'],f['bytes']), 'Inconsistent source blob inventory')
    for receipt in load('EXECUTION.json')['receipts']:
        require(receipt['head']==snapshot[receipt['number']]['headRefOid'], 'Local receipt head differs')
        digest=receipt.get('sha256', receipt.get('log_sha256'))
        raw=gzip.decompress((HERE/receipt['retained_log']).read_bytes())
        require(hashlib.sha256(raw).hexdigest()==digest, 'Local log receipt differs')
    for row in load('CI-EVIDENCE.json.gz'):
        require(row['head']==snapshot[row['number']]['headRefOid'], 'CI receipt head differs')
        for run in row['runs']:
            require(run['head']==row['head'], 'CI run belongs to a different head')
        for log in row['inspected_logs']:
            raw=gzip.decompress((HERE/'logs'/log['file']).read_bytes())
            require(hashlib.sha256(raw).hexdigest()==log['log_sha256'], 'CI log receipt differs')
    for log in load('CI-EXTRA.json.gz'):
        require(log['head']==snapshot[log['number']]['headRefOid'], 'Extra CI head differs')
        raw=gzip.decompress((HERE/'logs'/log['file']).read_bytes())
        require(hashlib.sha256(raw).hexdigest()==log['log_sha256'], 'Extra CI log differs')
    sources_by_number={r['number']:r for r in source}
    for row in load('CI-SOURCE-CONTEXT.json.gz'):
        n=row['number']
        require(not row.get('error') and row['submitted_head']==snapshot[n]['headRefOid'], 'CI context error')
        require(row['checkout_commit']['sha']==row['checkout_head'], 'CI checkout commit differs')
        tree=row['checkout_tree']
        require(not tree['truncated'] and tree['sha']==row['checkout_commit']['tree']['sha'], 'CI tree incomplete')
        files=[dict(path=f['path'],mode=f['mode'],blob=f['sha']) for f in tree['tree'] if f['type']=='blob']
        require(tree_oid(files)==tree['sha'], 'CI checkout tree authentication')
        actual={f['path']:(f['mode'],f['blob']) for f in files}
        mismatch=[f['path'] for f in sources_by_number[n]['files'] if actual.get(f['path'])!=(f['mode'],f['blob'])]
        require(mismatch==[f['path'] for f in row['mismatches']], 'CI source comparison differs')
        require(row['all_submitted_files_match']==(not mismatch), 'CI match status differs')
        require(not mismatch or (n==297 and set(mismatch)<={'.gitattributes','CONTRIBUTING.md','CONTRIBUTORS.md','Makefile','README.md','certificates/selected-result.json','scripts/verify_selected_result.py'}), 'Unreviewed CI checkout differences')
    archive=load('ARCHIVE.json')
    require(set(archive['parents'])>={r['head'] for r in source}, 'Source archive omitted a head')
    require(oid('commit',archive['commit_object'].encode())==archive['commit'], 'Archive commit authentication')
    require(set(x[7:] for x in archive['commit_object'].splitlines() if x.startswith('parent '))==set(archive['parents']), 'Archive parent binding')
    if (HERE/'PUBLICATION.json').exists():
        publication=load('PUBLICATION.json')
        require(publication['source_archive_commit']==archive['commit']
                and publication['source_archive_tag']==archive['tag'], 'Published archive differs')
        for decision in decisions.values():
            if decision['review_completion']['published']:
                require(decision['publication']['integration_commit']==publication['integration_commit'],
                        'Published integration differs')
    if (HERE/'CLOSURE-RECEIPTS.json').exists():
        receipts=load('CLOSURE-RECEIPTS.json')
        require(len(receipts)==100 and {r['number'] for r in receipts}==set(decisions), 'Incomplete closure reconciliation')
        for receipt in receipts:
            n=receipt['number']; observation=receipt['observed']; decision=decisions[n]
            require(observation['headRefOid']==decision['current_head'], 'Closure receipt current head differs')
            require(observation['state']==decision['github_state'], 'Closure receipt state differs')
            if receipt['status']=='closed_after_published_review':
                require(decision['current_head']==snapshot[n]['headRefOid'], 'Closed an unreviewed head')
                require(decision['closure']['comment_url']==receipt['comment']['url'], 'Closure comment differs')
                require(decision['disposition']=='incorporated' and observation['state']=='CLOSED', 'Premature closure')
            elif receipt['status']=='retained_open':
                require(observation['state']=='OPEN' and decision['unresolved_question'], 'Lost open blocker')
    if (HERE/'REGENERATED.json').exists():
        for result in load('REGENERATED.json'):
            raw=gzip.decompress((HERE/result['path']).read_bytes())
            require(hashlib.sha256(raw).hexdigest()==result['uncompressed_sha256'], 'Changed regenerated arithmetic')
    if args.git_blobs:
        proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        try:
            for sha,(digest,size) in blobs.items():
                proc.stdin.write((sha+'\n').encode());proc.stdin.flush()
                header=proc.stdout.readline().decode().split()
                require(header==[sha,'blob',str(size)], 'Missing source object: '+sha)
                raw=proc.stdout.read(size);require(proc.stdout.read(1)==b'\n','Git protocol')
                require(oid('blob',raw)==sha and hashlib.sha256(raw).hexdigest()==digest, 'Changed source bytes: '+sha)
        finally:
            proc.stdin.close();proc.stdout.close();proc.wait()
    print(f'PASS 100 pinned full trees, {len(blobs)} distinct blobs, original-diff coverage, scoped decisions and evidence integrity; no theorem claim')


if __name__ == '__main__':
    main()
