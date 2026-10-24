"""Private byte/path transport for frozen independent verifiers only.
Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0; no author search/model/native code is imported or executed.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha256
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate(root, manifest):
    for name, expected in manifest.items():
        p = root / name
        need(p.is_file() and not p.is_symlink(), 'Missing regular input: ' + name)
        need(sha256(p.read_bytes()).hexdigest() == expected, 'Input hash mismatch: ' + name)


def safe_name(name):
    p = PurePosixPath(name)
    need(name and not p.is_absolute() and p.as_posix() == name and
         '..' not in p.parts and '.' not in p.parts and '\\' not in name and ':' not in name,
         'Unsafe archive path')
    return p


def extract(container, contents, destination):
    need(sha256(container.read_bytes()).hexdigest() == contents['container_sha256'], 'Archive container changed')
    records = contents['members']
    seen = set()
    with tarfile.open(container, 'r:gz') as archive:
        for member in archive:
            safe_name(member.name)
            need(member.name in records and member.name not in seen and member.isfile(), 'Archive inventory/type mismatch')
            record = records[member.name]
            need(member.size == record['bytes'] and member.mode == record['mode'], 'Archive member size/mode mismatch')
            need(member.uid == member.gid == member.mtime == 0 and not member.uname and not member.gname,
                 'Archive normalization mismatch')
            stream = archive.extractfile(member)
            need(stream is not None, 'Missing archive stream')
            data = stream.read(record['bytes'] + 1)
            need(len(data) == record['bytes'] and sha256(data).hexdigest() == record['sha256'], 'Archive raw member changed')
            path = destination / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            seen.add(member.name)
    need(seen == set(records), 'Archive inventory incomplete')


def copy_review_bytes(source, destination):
    # Copy only bytes into fresh writable private directories, even when the
    # publication export is read-only. Never preserve source directory modes.
    for item in source.rglob('*'):
        if item.is_file() and '__pycache__' not in item.parts:
            path = destination / item.relative_to(source)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(item.read_bytes())


def run_checker(script, root, label):
    command = [sys.executable, '-I']
    if sys.flags.optimize:
        command.append('-O')
    command += ['-X', 'pycache_prefix=' + str(root / ('cache-' + label)), '-W', 'error', '-B', str(script)]
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_') and k not in
           ('PYTHONINSPECT', 'PYTHONSTARTUP', 'PYTHONPATH', 'PYTHONOPTIMIZE')}
    result = subprocess.run(command, cwd=root, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False, timeout=150)
    need(result.returncode == 0, label + ' failed: ' + result.stderr.decode(errors='replace')[-3000:])
    need(not result.stderr, label + ' unexpected stderr')
    return result.stdout


def stage_pair(root):
    contents = json.loads((HERE / 'ARCHIVE-CONTENTS.json').read_bytes())
    extracted = root / 'pair-archive'
    extract(HERE / 'evidence/author-packet.tar.gz', contents, extracted)
    author = root / 'outputs/joint-clifford-design-20261023'
    author.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(extracted / 'author'), author)
    review = root / 'outputs/joint-clifford-independent-review-20261023'
    copy_review_bytes(HERE / 'evidence/review', review)
    manifest = json.loads((author / 'AUTHOR-FINAL-MANIFEST.json').read_bytes())
    authenticate(author, manifest['files'])
    need(manifest['claims_not_combined'] and manifest['three_group_star_excluded'], 'Original two-claim scope preserved')
    for path, expected in manifest['independent_review_anchors'].items():
        need(sha256((root / path).read_bytes()).hexdigest() == expected, 'Original independent anchor mismatch')
    for request in json.loads((HERE / 'SOURCE-REQUESTS.json').read_bytes()):
        raw = extracted / request['archive_member']
        data = raw.read_bytes()
        need(sha256(data).hexdigest() == request['sha256'], 'Raw Git source mismatch')
        if request.get('author_member'):
            capture = author / request['author_member'].removeprefix('author/')
            if request['capture_relation'] == 'exact bytes':
                need(capture.read_bytes() == data, 'Exact source capture changed')
            else:
                need(capture.read_bytes() == data + b'\n', 'Source LF capture relation changed')
    capture_record = json.loads((author / 'zero-model-inputs/CAPTURE.json').read_bytes())
    relation = json.loads((HERE / 'CAPTURE-RELATIONS.json').read_bytes())
    raw = (extracted / relation['raw_git_member']).read_bytes()
    capture = (author / relation['capture_member'].removeprefix('author/')).read_bytes()
    need(capture == raw + b'\n', 'Discovery LF capture relation changed')
    need(sha256(raw).hexdigest() == capture_record['source_text_sha256'] == relation['raw_sha256'], 'Raw DISCOVERY source pin')
    need(sha256(capture).hexdigest() == capture_record['captured_file_sha256'], 'Original connector capture pin')
    need(sha256((author / 'zero-model-inputs/DISCOVERY-CONNECTOR-RESPONSE.json').read_bytes()).hexdigest() ==
         capture_record['response_sha256'], 'Original connector response pin')
    return author, review


def run_pair(root, review):
    suffix = '-OPTIMIZED' if sys.flags.optimize else ''
    run_checker(review / 'verify_graph_binding.py', root, 'graph')
    need((review / ('SOURCE-GRAPH-BINDING' + suffix + '.json')).read_bytes() ==
         (HERE / 'evidence/review/SOURCE-GRAPH-BINDING.json').read_bytes(), 'Fresh graph receipt differs')
    run_checker(review / 'check_joint_receipt.py', root, 'pair')
    need((review / ('JOINT-RECEIPT-REVIEW' + suffix + '.json')).read_bytes() ==
         (HERE / 'evidence/review/JOINT-RECEIPT-REVIEW.json').read_bytes(), 'Fresh pair receipt differs')
    run_checker(review / 'check_zero_model.py', root, 'zero')
    need((review / 'ZERO-MODEL-REVIEW.json').read_bytes() ==
         (HERE / 'evidence/review/ZERO-MODEL-REVIEW.json').read_bytes(), 'Fresh zero-model receipt differs')
    return {'pair_candidates': 3066, 'pair_profiles': 12264, 'pair_rank_entries': 102200,
            'zero_moves': 43, 'zero_incidence_rows': 172, 'zero_assignments_by_additivity': 2**43}


def stage_star(root):
    contents = json.loads((HERE / 'STAR-ARCHIVE-CONTENTS.json').read_bytes())
    star = root / 'outputs/joint-clifford-three-group-star-20261023'
    extract(HERE / 'evidence/star-packet.tar.gz', contents, star)
    review = root / 'outputs/joint-star-independent-review-20261023'
    copy_review_bytes(HERE / 'evidence/star-review', review)
    manifest = json.loads((star / 'AUTHOR-FINAL-MANIFEST.json').read_bytes())
    authenticate(star, manifest['files'])
    freeze = json.loads((review / 'FREEZE.json').read_bytes())
    authenticate(star, freeze['author_packet_files'])
    authenticate(star, freeze['source_input_hashes'])
    authenticate(root / 'outputs/joint-clifford-independent-review-20261023', freeze['prior_own_dependencies'])
    prior = root / 'outputs/joint-clifford-design-20261023'
    need((star / 'retained/SEARCH-RESULT.json').read_bytes() == (prior / 'SEARCH-RESULT.json').read_bytes(),
         'Star retains the same completed pair receipt')
    return star, review


def run_star(root, review):
    run_checker(review / 'check_star_receipt.py', root, 'star')
    # The frozen star verifier writes this same output filename in both modes.
    need((review / 'STAR-RECEIPT-REVIEW.json').read_bytes() ==
         (HERE / 'evidence/star-review/STAR-RECEIPT-REVIEW.json').read_bytes(), 'Fresh star receipt differs')
    need((HERE / 'evidence/star-review/STAR-RECEIPT-REVIEW.json').read_bytes() ==
         (HERE / 'evidence/star-review/STAR-RECEIPT-REVIEW-OPTIMIZED.json').read_bytes(), 'Frozen star mode equality')
    return {'star_bridge_charts': 1022, 'star_active_candidates': 4088,
            'star_profiles': 8176, 'star_rank_entries': 114464}


def run():
    try:
        safe_name('../escape')
    except ValueError:
        pass
    else:
        raise ValueError('Archive path rejection guard accepted parent traversal')
    with tempfile.TemporaryDirectory(prefix='joint-clifford-independent-') as d:
        root = Path(d)
        _, review = stage_pair(root)
        _, star_review = stage_star(root)
        result = run_pair(root, review)
        result.update(run_star(root, star_review))
    return result
