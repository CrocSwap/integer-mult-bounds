"""Bounded complete canonical transport checks; no scientific replay or timing."""
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import types
ROOT=Path(__file__).resolve().parent
pins=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
for name in ('check_artifacts.py','archive_support.py'):
    if sha256((ROOT/name).read_bytes()).hexdigest()!=pins[name]:raise ValueError('transport wrapper source pin: '+name)
S=types.ModuleType('_gf2_transport_support');S.__file__=str(ROOT/'archive_support.py')
exec(compile((ROOT/'archive_support.py').read_bytes(),S.__file__,'exec'),S.__dict__)


def typed(node):
    S.need(type(node) is list and bool(node) and type(node[0]) is str,'exact typed node')
    tag=node[0]
    if tag=='None':S.need(len(node)==1,'typed None')
    elif tag=='Fraction':S.need(len(node)==3 and type(node[1]) is type(node[2]) is int and node[2]>0,'exact Fraction pair')
    elif tag in ('bool','str'):S.need(len(node)==2 and type(node[1]) is (bool if tag=='bool' else str),'exact primitive type')
    elif tag=='int':S.need(len(node)==2 and type(node[1]) is str and str(int(node[1]))==node[1],'canonical exact integer string')
    elif tag=='float':S.need(len(node)==2 and type(node[1]) is str and float.fromhex(node[1]).hex()==node[1],'lossless float hex')
    elif tag in ('list','tuple'):
        S.need(len(node)==2 and type(node[1]) is list,'typed sequence')
        for item in node[1]:typed(item)
    elif tag=='dict':
        S.need(len(node)==2 and type(node[1]) is list,'ordered typed dictionary')
        for item in node[1]:
            S.need(type(item) is list and len(item)==2,'ordered dictionary pair')
            typed(item[0]);typed(item[1])
    else:raise ValueError('unknown exact type tag')


def main():
    S.need(len(sys.argv)==1,'no alternate transport input')
    S.authenticate();science=json.loads((ROOT/'anchor.json').read_text())['science']
    directory=ROOT/'evidence/canonical';manifest=json.loads((directory/'MANIFEST.json').read_text())
    expected={'witness.json.gz':science['side']['exact_witness_sha256'],'rank-trace.json.gz':science['side']['rank_trace_sha256'],
              'full-return.lossless.json.gz':science['full_return_lossless_sha256'],'complex-network.json':science['full_cli_certificate_sha256'],
              'original-stdout.txt':science['full_cli_stdout_sha256']}
    complement=(json.dumps(science['ordered_complements'],sort_keys=True,separators=(',',':'))+'\n').encode()
    expected['complement-transcript.json']=sha256(complement).hexdigest()
    S.need(manifest['schema_version']==1 and set(manifest['artifacts'])==set(expected),'complete six-payload transport census')
    totals={};small={}
    for name,expected_hash in expected.items():
        row=manifest['artifacts'][name];path=directory/name
        S.need(path.is_file() and not path.is_symlink(),'regular canonical artifact')
        S.need(type(row['logical_bytes']) is int and 0<=row['logical_bytes']<=128*1024**2 and row['logical_sha256']==expected_hash,'anchor-bound logical payload')
        encoding='gzip' if name.endswith('.gz') else 'plain'
        S.need(row['encoding']==encoding and type(row['transport_bytes']) is int and path.stat().st_size==row['transport_bytes'] and S.digest(path)==row['transport_sha256'],'committed transport integrity')
        h=sha256();count=0;parts=[]
        with (gzip.open(path,'rb') if encoding=='gzip' else path.open('rb')) as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):
                count+=len(block);S.need(count<=row['logical_bytes'],'bounded complete payload')
                h.update(block)
                if name not in ('witness.json.gz','rank-trace.json.gz'):parts.append(block)
        S.need(count==row['logical_bytes'] and h.hexdigest()==expected_hash,'complete decompressed payload equality')
        totals[name]=count
        if parts:small[name]=b''.join(parts)
    S.need(totals['witness.json.gz']==science['side']['serialized_bytes']['witness'] and totals['rank-trace.json.gz']==science['side']['serialized_bytes']['rank_trace'],'complete witness/rank byte counts')
    typed(json.loads(small['full-return.lossless.json.gz']))
    S.need(small['complex-network.json']==(ROOT/'reference/certificates/complex-network.json').read_bytes(),'literal original certificate bytes')
    S.need(small['complement-transcript.json']==complement,'complete complement receipt')
    S.authenticate()
    print(json.dumps(dict(status='PASS_FULL_NETWORK_CANONICAL_TRANSPORT',payload_bytes=totals,full_typed_shape=True,no_benchmark_or_theorem_claim=True,regenerated_container_hash_is_not_mathematical_identity=True),sort_keys=True))


if __name__=='__main__':main()
