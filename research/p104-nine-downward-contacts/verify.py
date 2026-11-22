#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run source authentication and independently implemented lower/upper replays."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FROZEN = {'NINE-LOWER.json': '0ab146410ed1115e75faed8dc47c138111628143448423366797710f037e9c32', 'NINE-WORD.json.gz': '4a4bd4faf0b084fbdc4c3e671eea3895c8318bb42aaf44c7afebef7859bb8f2a', 'NINE-WORD-RESULT.json': '5992ad093c7e67f635fc17e5a2b4dffecd69897fe4d4453a1cfca97c8f565a8b', 'NINE-PRICE.json': 'b732c6c584ea7985f587b6d55d99d09464a44b2ededb69aef1e918345f8b548d', 'NINE-DIRECT.json': 'adf8473fe3e783874112eb49af4f052f6fe25f6220e5e38d20b6b74b816b75d9', 'DIRECT-RECEIPT.json': '0d6482126967451a123c1a56bd0eec08c4379d059ca3d4b86dc6ac95d91cbc4e', 'nine_lower.py': '29981be84e5beaad60ab31574c8d1e94559e0022c596de0ab91830bb88e39615', 'nine_word.py': '60b2736f91d9b9f7fb362c41a5e4437d578da95cfd59aa67933ca7a3eb54d716', 'nine_price.py': 'e9f84641bf73038c3df066aa592a17d586dd6366fa811819ec483478d817ac05', 'nine_direct.py': '01d9f2155d539addfdce6e6f0245eb30278f8758c7538bab0f19d4982f4281a1', 'check_index.py': 'f64afca4cfd39de0b1f101a9d5535d37f246d5eee62d463d8fb6b4e4c2b4cf62', 'INDEX-WITNESS.json': 'fa3931913410799f0bc98257701bbdf253d2ba6acc0f95ddd94868f6f9e28a5b', 'INDEX-RECEIPT.json': '9a820a9ac952e65e07edcffa61d9addd13945ab22835691058d3792e7b973e16', 'check_word.py': 'dd71f767620e7cca4e6bedf8b9802a9fd68ed31d0f72befc46861733186f858f', 'WORD-RECEIPT.json': 'ddb5cfbaad6c81f110167da46b18e5c522a16effa0cce9ca98d5a2e20a32532f', 'check_direct.py': 'e613c71eb867416a5e451dded26c71fbcb2e8f490dce554341767d3ff452ec90', 'pinned/strong-bit.json.gz': '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326', 'pinned/EFREE-CALLER.json.gz': '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b', 'pinned/price_audit.py': 'ca650d573f605bf51a8806a772903b6775cd036dfbfe7f043eccd3e51bc9977b', 'FIRST-PASS-RESULT.json': 'd349b8e8c1c95fcde98b256ec26c9ede25de31e03cb04f306c05ce6b73fa64ba'}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def blob_hash(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    require(not sys.flags.optimize, 'run without optimized assertions')
    for name, digest in FROZEN.items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest,
                'changed replay input: ' + name)
    for name, expected in (
        ('pinned/strong-bit.json.gz','16f8cafb1c4d139a99a62e46eb40c118e6176c34'),
        ('pinned/EFREE-CALLER.json.gz','f022272a8d51ede841778dec76e2bfb24b614d04'),
        ('pinned/price_audit.py','829966dd450bdc33409ef0a214ee5a184f89a564'),
    ):
        require(blob_hash((HERE / name).read_bytes()) == expected, 'Git blob mismatch: '+name)
    graph=HERE/'pinned/strong-bit.json.gz'
    word=HERE/'NINE-WORD.json.gz'
    witness=HERE/'INDEX-WITNESS.json'
    with tempfile.TemporaryDirectory(prefix='p104-nine-replay-') as directory:
        temp=Path(directory)
        def run(script,*args,check=True):
            # Fresh namespace also blocks reads from pre-existing bytecode.
            cache=temp/('cache-'+str(run.counter));run.counter+=1
            cmd=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(HERE/script),*map(str,args)]
            proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=550)
            if check:
                require(proc.returncode==0, script+' failed: '+proc.stderr[-4000:])
                return json.loads(proc.stdout)
            require(proc.returncode!=0, 'negative control accepted: '+script)
        run.counter=0
        def equal(value,receipt):
            require(value==json.loads((HERE/receipt).read_text()), 'receipt mismatch: '+receipt)
        equal(run('nine_lower.py',graph),'NINE-LOWER.json')
        equal(run('check_index.py',graph,witness),'INDEX-RECEIPT.json')
        equal(run('nine_direct.py',graph),'NINE-DIRECT.json')
        equal(run('check_direct.py',graph),'DIRECT-RECEIPT.json')
        first=run('nine_word.py',graph)
        first_expected=json.loads((HERE/'FIRST-PASS-RESULT.json').read_text())
        first.pop('new_graph_compressed_sha256');first_expected.pop('new_graph_compressed_sha256')
        require(first==first_expected, 'first-pass construction receipt mismatch')
        rebuilt=temp/'word.json.gz'
        result=run('nine_word.py',graph,'--top-first','--write-word',rebuilt)
        expected=json.loads((HERE/'NINE-WORD-RESULT.json').read_text())
        # Recompression can differ across zlib implementations; compare the
        # canonical uncompressed word, while authenticating the retained gzip.
        result.pop('new_graph_compressed_sha256');expected.pop('new_graph_compressed_sha256')
        require(result==expected, 'construction receipt mismatch')
        require(gzip.decompress(rebuilt.read_bytes())==gzip.decompress(word.read_bytes()),
                'rebuilt word differs from frozen word')
        equal(run('check_word.py',graph,word),'WORD-RECEIPT.json')
        equal(run('nine_price.py',HERE/'pinned',word),'NINE-PRICE.json')
        bad_graph=temp/'bad-source.gz';buf=bytearray(graph.read_bytes());buf[-1]^=1;bad_graph.write_bytes(buf)
        run('nine_lower.py',bad_graph,check=False)
        bad_word=temp/'bad-word.gz';buf=bytearray(word.read_bytes());buf[-1]^=1;bad_word.write_bytes(buf)
        run('check_word.py',graph,bad_word,check=False)
    print('PASS_NINE_DOWNWARD_CONTACTS lower_witness=13 direct_sender_audits=2 upper_rows=630 adjoint_rows=630 caller_histograms=0,1,36')

if __name__=='__main__':
    main()
