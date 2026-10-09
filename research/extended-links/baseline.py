"""The #161 files this package reads, rebuilt from a pinned archive.

#161 (eumemic) is not on main. Its 32 files that cxlinks.py, verify.py and make_plan.py read (scripts, frozen arcs and
physical layer, module sources and certificates) are kept in baseline-pr161.tar.gz, following the convention of
research/coordinated-frames-and-entrance-banks. tree() writes them into a temporary directory after checking the
archive's sha256 and every file's sha256 against SOURCE.json, whose hashes are those of commit d14e291. Set
EXTENDED_LINKS_TREE to a full #161 checkout to use that instead.
"""
import atexit
import hashlib
import io
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rebuild(dest):
    src = json.loads((HERE / 'SOURCE.json').read_text())
    data = (HERE / src['archive']).read_bytes()
    if hashlib.sha256(data).hexdigest() != src['archive_sha256']:
        raise SystemExit('baseline archive differs from SOURCE.json')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = [x for x in archive.getmembers() if x.isfile()]
        if sorted(x.name for x in members) != sorted(src['files']):
            raise SystemExit('baseline archive lists other files than SOURCE.json')
        for x in members:
            part = Path(x.name)
            if part.is_absolute() or '..' in part.parts:
                raise SystemExit('unsafe path in baseline archive: ' + x.name)
            handle = archive.extractfile(x)
            if handle is None:
                raise SystemExit('unreadable member in baseline archive: ' + x.name)
            body = handle.read()
            if hashlib.sha256(body).hexdigest() != src['files'][x.name]:
                raise SystemExit('baseline file differs from SOURCE.json: ' + x.name)
            (dest / part).parent.mkdir(parents=True, exist_ok=True)
            (dest / part).write_bytes(body)
    return src['commit']


def tree():
    if os.environ.get('EXTENDED_LINKS_TREE'):
        return Path(os.environ['EXTENDED_LINKS_TREE']).resolve()
    dest = Path(tempfile.mkdtemp(prefix='extended-links-pr161-'))
    atexit.register(shutil.rmtree, dest, True)
    rebuild(dest)
    return dest.resolve()
