"""Authenticate exact source bytes before the native recipe producer runs."""
from hashlib import sha256
from pathlib import Path
import gzip
import io
import json
import tarfile

P = Path(__file__).resolve().parent


def need(ok, why):
    if not ok: raise ValueError(why)


def member(raw,name):
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        entries = [m for m in archive.getmembers() if m.name == name]
        need(len(entries) == 1 and entries[0].isfile(), 'Exact regular source member')
        return archive.extractfile(entries[0]).read()


def authenticate():
    for pin in json.loads((P/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            path = Path(pin['path']).relative_to('research/scaled-fusion-native-columns')
            need(sha256((P/path).read_bytes()).hexdigest() == pin['sha256'], 'Source hash: '+str(path))
    archive = (P/'inputs/source.tar').read_bytes()
    source = json.loads((P/'inputs/SOURCE.json').read_text())
    need(sha256(archive).hexdigest() == source['archive_sha256'], 'Exact PR6453 export')
    provenance = json.loads((P/'inputs/PROVENANCE.json').read_text())[0]
    raw = archive
    for path in provenance['archive_chain']: raw = member(raw,path)
    compiler = member(raw,provenance['path'])
    need(compiler == (P/'inputs/clifford_exact.py').read_bytes()
         and sha256(compiler).hexdigest() == provenance['sha256'], 'Actual nested compiler bytes')
    old = json.loads(gzip.decompress(member(archive,'research/p104-third-anchor-clean-mixed-root/WORD.json.gz')))
    new = json.loads(gzip.decompress((P/'inputs/WORD.json.gz').read_bytes()))
    specs = json.loads((P/'inputs/SPEC.json').read_text())
    need(old['frames'] == new['frames'], 'Unchanged actual frame table')
    for item in specs:
        role,a,b = item['role'],item['first'],item['second']
        e,f,g = item['E'],item['F'],item['G']
        need(old['program'][a] == ['MOVE',role,e,f,False]
             and old['program'][b] == ['MOVE',role,f,g,False], 'Exact old interval boundaries')
        need(new['program'].count(['MOVE',role,e,g,False]) == 1, 'Exact new direct transport')
    return new,specs
