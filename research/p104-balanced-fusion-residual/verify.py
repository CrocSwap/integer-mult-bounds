#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the balanced word, caller obstruction, and counterfactual invoice."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
FROZEN={'candidate.py': 'd848ce922da44a1aae7eb22b1d12e09ef6ddd59b4ba804a149e00b9b7b7e1b89', 'ONE-RESIDUAL-RESULT.json': 'e46455ee7bedc9ecbd8cd780bd0dc167a4ca7963922715d5fbe992e2d703e12d', 'verify_candidate.py': 'b026de749f1a92ae714934f46e73e8c13a396491445e562f625ce4cb41dac782', 'CANDIDATE-AUDIT.json': 'ad481bc8c4f44c944c1adeaf1012ffaecc87c01d034f0955de7f30711b60cfe4', 'constant_composition.py': 'd665b36f5009bdb0e22bd7dd2297df989029cd8816595b4fdfb4ca765ac8790f', 'constant_composition.json': '8bbb270553968fbeed190b1741fb2d56a6f801243d77243aaa674c4b4c0c1cfb', 'caller_dual_check.py': '28e2008c0d455b7c09ab925293c905e621c3cbb87fc9cf4b849c1266f85a05c2', 'caller_dual_check.json': '88fb6faca7fcdfe01bcef09fee6a65a2a632469031253e368c8e88237c1736a8', 'composition_controls.py': '3909d89285d0155d50e06ed50e6ec0ba55a22351fc0160414f6bad5e405c1130', 'COMPOSITION-CONTROLS.json': '2cd68e11e3656571dad8fe07628967c32a9ae3e3ee18c495a755a76119012e8f', 'hinge_screen.py': '4a391a93e7f5b7ad3484f9bccb435c313ea2efc8ac60c08f0858c434d7d6e4ff', 'HINGE.json': '66b035c97ffa1977108c62388eea50a0be165a633a06bc8cb3fe186db67014ad', 'hinge_audit.py': 'cabebddf56444fe8193551b8e4ca506ebb07eff41b8ecf32618a4e363122f72a', 'HINGE-AUDIT.json': 'b038d3311cc7c01f1fd4af63c199e3377b98763d4a20b71be761293101bb81a1', 'balanced_price.py': '1b1accfc375229f3fb95ae651d72289052d2b6c00cb436f4a9bc911b0cac8e43', 'BALANCED-PRICE.json': 'de5e75d1dfdc6b75f573b6d49fdf4b704f0cb0cffddee8eb5f0f8a4c4d6065ae', 'counterfactual_invoice.py': 'fb6fe39dac2d5b156c62acced9618f38815f2f18cdf72e1c251b78246b21e408', 'INVOICE.json': 'ec96c828760da4ff0b269e76debc431d2916fc050e96658b6d81d409f3a9d3ae', 'second_slot.py': '848210b31fc3d2a8e89248b7662fde8489700b8a3b2b3654a8d3b47545b04a84', 'slot_solver.py': 'd9c2ad85cf10a625ef5f6c111ae5a0b2536aa7300bcf9437644e15e2962aea5a', 'sponsor_solver.py': '0c152479dd271fbdb92c1261f56f34067bcda7fa616725fe8029d4939f0da358', 'gf2.py': '23347c0ad08f0680f8e9ed60fbf63c05213309ac9f27029daceda50f55292130', 'pinned/strong-bit.json.gz': '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326', 'pinned/EFREE-CALLER.json.gz': '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b', 'pinned/ONE-RESIDUAL.json.gz': '7fa5589301124788237a569c3c0bbc0783f70efd840b15238300b8a2d5ab1cd7', 'pinned/price_audit.py': 'ca650d573f605bf51a8806a772903b6775cd036dfbfe7f043eccd3e51bc9977b', 'invoice_engine/OVERLAY.json': '73aaf56a8a199cf3b7fc6c87316ca50298f47561e4b7c227edec6230f12a8403', 'invoice_engine/PREDECESSOR-SOURCES.json': '3634f7a15b8ca6f1832e48bdd4e83bd764509f804196d956149a9a82e7512a64', 'invoice_engine/RESULT.json': 'e1ccc49a75e17fab4f5aa03697db58a0a6c3ad335cd7b8bba156c9bc3d419179', 'invoice_engine/check_profile.py': '83561f0c2da467b9b657380e043b069de1e2f139d5231cccd0abcce665bd6352', 'invoice_engine/outer_budget.py': 'ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02', 'invoice_engine/predecessor-8030.tar.gz': '769d5a05cc1373fa22ed5956af636992fcd19d7e5c1753a32033a73c358cd31c', 'invoice_engine/restore_machine.py': '0d88742495d10d044b2fe2a63e2220646230b8695b0094a970e254a71bc81d8e', 'invoice_engine/verify_funding.py': 'b9596574f4ded80c2bee2d44fef4d1d4aff859f53eadacb089130f34bed6779e', 'SECOND-SLOT.txt': '5657fbf01c95236af56802240f5c70370f0bd84d47bffbd73153a13ba994ddf9'}

def require(condition,message):
    if not condition:raise AssertionError(message)

def blob_hash(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    require(not sys.flags.optimize,'run without optimized assertions')
    for name,digest in FROZEN.items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,'changed replay input: '+name)
    for name,blob in [('pinned/strong-bit.json.gz','16f8cafb1c4d139a99a62e46eb40c118e6176c34'),('pinned/EFREE-CALLER.json.gz','f022272a8d51ede841778dec76e2bfb24b614d04'),('pinned/price_audit.py','829966dd450bdc33409ef0a214ee5a184f89a564'),('invoice_engine/predecessor-8030.tar.gz','e00a6bfe8328b4c982bf0689c4d55c8207515514')]:
        require(blob_hash((HERE/name).read_bytes())==blob,'Git blob mismatch: '+name)
    graph=HERE/'pinned/strong-bit.json.gz';candidate=HERE/'pinned/ONE-RESIDUAL.json.gz'
    with tempfile.TemporaryDirectory(prefix='p104-balanced-replay-') as tmp:
        temp=Path(tmp)
        def run(script,*args,parse=True,check=True,cwd=None):
            cache=temp/('cache-'+str(run.count));run.count+=1
            command=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(script),*map(str,args)]
            proc=subprocess.run(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=550)
            if not check:
                require(proc.returncode!=0,'negative control accepted: '+str(script));return None
            require(proc.returncode==0,str(script)+' failed: '+proc.stderr[-5000:])
            return json.loads(proc.stdout) if parse else proc.stdout
        run.count=0
        def equal(data,name):
            require(data==json.loads((HERE/name).read_text()),'receipt mismatch: '+name)
        rebuilt=temp/'rebuilt.json.gz'
        equal(run(HERE/'candidate.py',graph,rebuilt),'ONE-RESIDUAL-RESULT.json')
        require(gzip.decompress(rebuilt.read_bytes())==gzip.decompress(candidate.read_bytes()),'rebuilt graph differs')
        equal(run(HERE/'verify_candidate.py',graph,candidate),'CANDIDATE-AUDIT.json')
        equal(run(HERE/'constant_composition.py'),'constant_composition.json')
        equal(run(HERE/'caller_dual_check.py'),'caller_dual_check.json')
        equal(run(HERE/'composition_controls.py'),'COMPOSITION-CONTROLS.json')
        equal(run(HERE/'hinge_screen.py',graph),'HINGE.json')
        equal(run(HERE/'hinge_audit.py'),'HINGE-AUDIT.json')
        equal(run(HERE/'balanced_price.py',HERE/'pinned'),'BALANCED-PRICE.json')
        # The second-slot checker launches two more interpreters. Copy its
        # authenticated source to a fresh private directory, so no old pyc can
        # be imported by those children even under -I -B.
        second=temp/'second';second.mkdir();(second/'pinned').mkdir()
        for name in ('second_slot.py','slot_solver.py','sponsor_solver.py','gf2.py'):
            shutil.copyfile(HERE/name,second/name)
        shutil.copyfile(candidate,second/'pinned/ONE-RESIDUAL.json.gz')
        require(run(second/'second_slot.py',parse=False)==(HERE/'SECOND-SLOT.txt').read_text(),'second-slot receipt mismatch')
        # Restore a committed offline predecessor and its exact public overlay.
        module=HERE/'invoice_engine/restore_machine.py'
        spec=importlib.util.spec_from_file_location('p104_invoice_restore',module)
        restore=importlib.util.module_from_spec(spec);spec.loader.exec_module(restore)
        machine=temp/'machine';machine.mkdir();restore.restore(machine);restore.apply_overlay(machine)
        invoice=temp/'invoice.json'
        run(HERE/'counterfactual_invoice.py',machine,invoice,parse=False)
        require(json.loads(invoice.read_text())==json.loads((HERE/'INVOICE.json').read_text()),'counterfactual invoice mismatch')
        bad=temp/'bad-source.gz';buf=bytearray(graph.read_bytes());buf[-1]^=1;bad.write_bytes(buf)
        run(HERE/'candidate.py',bad,temp/'bad-out.gz',check=False)
    print('PASS_BALANCED_RESIDUAL local_rows=630 caller_placements=36 hinge=4096 conditional_invoice=268,285')

if __name__=='__main__':main()
