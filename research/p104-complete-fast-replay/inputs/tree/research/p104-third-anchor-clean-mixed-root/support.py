"""Authenticate retained source bytes before importing them.
Adapted from the PR6417 support module (Rohan Arun with substantial OpenAI Codex assistance, Apache-2.0).
Changes for the third-anchor stack by the Claude Sonnet 5.5 main session for Erwan L., marked CANDIDATE CHANGE.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha256, sha1
from fractions import Fraction as Q
import importlib.util
import json
import gzip
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def encode(v):
    if isinstance(v, Q):
        return str(v)
    if isinstance(v, dict):
        return {str(k): encode(x) for k,x in v.items()}
    if isinstance(v, (tuple,list)):
        return [encode(x) for x in v]
    return v


def authenticate(data, pin):
    need(sha256(data).hexdigest() == pin['sha256'], 'Source SHA256: '+pin['path'])
    need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['git_blob'], 'Source Git blob: '+pin['path'])


def inputs(destination):
    rows = read(HERE/'SOURCES.json')['files']
    pins = {x['path']:x for x in rows}
    need(len(pins) == len(rows), 'Unique source pins')
    for row in rows:
        if row['usage'] == 'input':
            authenticate((ROOT/row['path']).read_bytes(),row)
    manifest = read(HERE/'RETAINED-INPUTS.json')
    all_members = set()
    for group in ('native','root','contact','lift'):  # CANDIDATE CHANGE: also the PR6372/PR6353 and PR6375 retained sources
        entry = manifest[group]
        archive = HERE/entry['archive']
        need(sha256(archive.read_bytes()).hexdigest() == entry['sha256'], 'Exact retained archive')
        members = {x['path']:x for x in entry['files']}
        need(len(members) == len(entry['files']), 'Unique archive pins')
        with tarfile.open(archive,'r:') as tar:
            seen = set()
            for member in tar.getmembers():
                path = PurePosixPath(member.name)
                need(member.isfile() and not path.is_absolute() and '..' not in path.parts and ':' not in member.name and '\\' not in member.name, 'Regular safe source member')
                need(member.name in members and member.name not in seen and member.name not in all_members, 'Unique declared source member')
                seen.add(member.name)
                raw = tar.extractfile(member).read()
                authenticate(raw,members[member.name])
                authenticate(raw,pins[member.name])
                need(pins[member.name]['pin'] == 'head:'+entry['head']+':'+member.name, 'Exact upstream provenance')
                target = destination/member.name
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(raw)
            need(seen == set(members), 'Complete archive')
            all_members |= seen
    need(len(all_members) == 31, 'Every retained source file')  # CANDIDATE CHANGE: 16 + 8 contact + 7 lift members


def reject(action):
    try:
        action()
    except ValueError as ex:
        return str(ex)
    raise ValueError('Corruption accepted')
