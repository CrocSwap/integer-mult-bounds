#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the source-bound seven-grade line screen and independent audit."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
FROZEN={'seven.py': '4801f97baf25cbf948eaa77eaaaeba00879da89ddf9982844590a8cffc76fe0b', 'seven_example.py': '726316281d0d1d15bf44ab95fde81f27fe507d579c0f6a470ce61727301e7a22', 'seven_price.py': 'f57ad5fb49a04a04328ea35be314248972963357cc7221fd3beb5a8e38e95fd2', 'check_independent.py': '2cc7a750522dc6f24f021dbf3757d3ff7434cae9f55b9ddd553c0b5b30a4e18e', 'SEVEN.json': '8da5dd33d664ab9d5ec167d923d7ab146b4039586cf8b7b1fce32f588b31c058', 'SEVEN-EXAMPLE.json': 'a2ce2ba9d14871cf9956135d2ed947f1f30288cbe98ebcfc9b59d1da85bce838', 'SEVEN-PRICE.json': '8f6d742d627d62f47a2519b13cf8de8fd7023d78e04cc53fae3f6963b7666ec4', 'INDEPENDENT-RECEIPT.json': 'ddd1c1d0d7aa5ec9b36647bd56445143d65565d2211e7e8950067d60d9bb2be2', 'pinned/strong-bit.json.gz': '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326', 'pinned/EFREE-CALLER.json.gz': '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b', 'pinned/price_audit.py': 'ca650d573f605bf51a8806a772903b6775cd036dfbfe7f043eccd3e51bc9977b', 'check_example.py': 'dcdd0941d773bfdab4661b0dd64f95eeffd05b8b3fa91441b2718461d6e9583d', 'INDEPENDENT-EXAMPLE.json': 'bbbba8df36373d30dfe12f67eec462dd858d48764a63df664e731598b2ad5905'}

def require(condition,message):
    if not condition:raise AssertionError(message)

def blob_hash(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    require(not sys.flags.optimize,'run without optimized assertions')
    for name,digest in FROZEN.items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,'changed replay input: '+name)
    for name,blob in [('pinned/strong-bit.json.gz','16f8cafb1c4d139a99a62e46eb40c118e6176c34'),('pinned/EFREE-CALLER.json.gz','f022272a8d51ede841778dec76e2bfb24b614d04'),('pinned/price_audit.py','829966dd450bdc33409ef0a214ee5a184f89a564')]:
        require(blob_hash((HERE/name).read_bytes())==blob,'Git blob mismatch: '+name)
    graph=HERE/'pinned/strong-bit.json.gz';witness=HERE/'SEVEN.json'
    with tempfile.TemporaryDirectory(prefix='p104-seven-replay-') as t:
        temp=Path(t)
        def run(script,*args,check=True):
            # Every interpreter gets its own fresh bytecode namespace.
            cache=temp/('cache-'+str(run.count));run.count+=1
            args=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(HERE/script),*map(str,args)]
            proc=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=550)
            if not check:
                require(proc.returncode!=0,'negative control accepted: '+script);return None
            require(proc.returncode==0,script+' failed: '+proc.stderr[-4000:])
            return json.loads(proc.stdout)
        run.count=0
        def equal(value,receipt):
            require(value==json.loads((HERE/receipt).read_text()),'receipt mismatch: '+receipt)
        equal(run('seven.py',graph),'SEVEN.json')
        equal(run('check_independent.py',graph,witness),'INDEPENDENT-RECEIPT.json')
        equal(run('seven_example.py',graph),'SEVEN-EXAMPLE.json')
        equal(run('check_example.py',graph),'INDEPENDENT-EXAMPLE.json')
        equal(run('seven_price.py',HERE/'pinned'),'SEVEN-PRICE.json')
        bad=temp/'bad-source.gz';buf=bytearray(graph.read_bytes());buf[-1]^=1;bad.write_bytes(buf)
        run('seven.py',bad,check=False)
        corrupt=json.loads(witness.read_text())
        row=corrupt['classifications'][0];pair=row['two_immune_witnesses_for_root'];row['two_immune_witnesses_for_root']=[pair[0],pair[0]]
        bad_witness=temp/'bad-witness.json';bad_witness.write_text(json.dumps(corrupt))
        run('check_independent.py',graph,bad_witness,check=False)
    print('PASS_SEVEN_GRADE_RETURNS cases=999 independent_cases=999 example_wrong_rows=54')

if __name__=='__main__':main()
