"""Authenticate byte-exact predecessor before import; no frozen input changes."""
import hashlib
import importlib.util
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = 'research/qq16-complete-native-decoder/'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage'] == 'input':
            raw = (ROOT/item['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'input hash: '+item['path'])
    for item in json.loads((HERE/'SNAPSHOTS.json').read_text())['files']:
        raw = (HERE/item['snapshot']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'snapshot hash: '+item['snapshot'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == item['git_blob'],
             'snapshot blob: '+item['snapshot'])


class ExportRoot:
    """Only relocate the pinned predecessor package; retain all other input paths."""
    def __truediv__(self, path):
        text = str(path)
        return HERE/'vendor/pr2540'/text[len(PREFIX):] if text.startswith(PREFIX) else ROOT/path


def load():
    authenticate()
    path = HERE/'vendor/pr2540/verify.py'
    spec = importlib.util.spec_from_file_location('retained_complete_2540', path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    old.ROOT = ExportRoot()
    old.N.ROOT = old.ROOT
    return old
