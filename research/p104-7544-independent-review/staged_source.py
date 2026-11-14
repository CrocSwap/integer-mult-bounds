# SPDX-License-Identifier: Apache-2.0
"""Stateless factoring of #7544's complete replay into its two bounded kernels.

No mathematical engine, adapter, assertion or expected mathematical field is
changed. The native command regenerates and compares the entire native receipt.
The signed command consumes the authenticated, mathematically identical frozen
native receipt in its own fresh root. Both commands are required for package
success; running signed alone is not a fresh native verification.
"""
import argparse, gzip, importlib.util, json, os, shutil, subprocess, sys
from hashlib import sha256
from pathlib import Path


def load(path):
    spec=importlib.util.spec_from_file_location('unchanged7544_replay',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def mathematical_native(path):
    obj=json.loads(path.read_text());obj.pop('timings')
    return sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('root',type=Path)
    p.add_argument('--stage',choices=('native','signed'),required=True);a=p.parse_args()
    s=a.source.resolve();r=a.root.resolve();r.mkdir(parents=True,exist_ok=True)
    original=load(s/'replay.py');original.authenticate()
    (r/'isolated').mkdir();frozen=r/'frozen-composition';engine=s/'engines'
    original.contained(r,s/'compose/compose.py',s/'bench/inputs',frozen,timeout=32)
    original.compare(frozen/'COMPOSITION.json',s/'expected/COMPOSITION.json',('gzip_sha256',))
    emitted=frozen/'COMPOSED-WORD.json.gz';retained=s/'expected/COMPOSED-WORD.json.gz'
    assert gzip.decompress(emitted.read_bytes())==gzip.decompress(retained.read_bytes())
    shutil.copyfile(retained,emitted);shutil.copyfile(s/'expected/COMPOSITION.json',frozen/'COMPOSITION.json')
    shutil.copytree(s/'upstream/inputs',r/'inputs')
    for name,source in (
        ('7481-WORD.json.gz',s/'bench/inputs/7481-WORD.json.gz'),
        ('7481-NATIVE.json',s/'bench/7481-NATIVE.json'),
        ('7481-SIGNED.json',s/'bench/7481-SIGNED-RESULT.json'),
    ):shutil.copyfile(source,frozen/name)
    for name in ('reroute','validation_native','validation_signed'):(r/'producer54'/name).mkdir(parents=True)
    shutil.copyfile(frozen/'COMPOSED-WORD.json.gz',r/'producer54/reroute/WORD.json.gz')
    shutil.copyfile(engine/'7481-EMISSION.json',r/'producer54/reroute/RESULT.json')
    (r/'receipts').mkdir()
    original.contained(r,engine/'adapt_native.py',r,engine/'native.py',timeout=5)
    signed=r/'producer54/validation_signed/composed_run.py'
    signed_adapter=original.contained(r,engine/'adapt_signed.py',r,engine/'signed.py',signed,timeout=5,capture=True)
    (r/'receipts/SIGNED-ADAPTER.json').write_bytes(signed_adapter)
    native=r/'producer54/validation_native/NATIVE-RESULT.json'
    if a.stage=='native':
        original.contained(r,r/'producer54/validation_native/run.py',timeout=470)
        original.compare(native,s/'expected/NATIVE.json',('timings',))
        report=dict(stage='native',fresh_native_sha256=sha256(native.read_bytes()).hexdigest(),
                    fresh_native_math_sha256=mathematical_native(native),
                    frozen_native_sha256=sha256((s/'expected/NATIVE.json').read_bytes()).hexdigest(),
                    frozen_native_math_sha256=mathematical_native(s/'expected/NATIVE.json'),
                    mathematical_equivalence=True)
        print('PASS_STATELESS7544_FRESH_NATIVE_RECEIPT',flush=True)
    else:
        # This exact committed receipt is required to equal a fresh native
        # result in the companion required command. It is not a substitute
        # for running that command. Its timing fields have no scientific use.
        shutil.copyfile(s/'expected/NATIVE.json',native)
        original.contained(r,signed,timeout=475)
        original.compare(r/'producer54/validation_signed/RESULT.json',s/'expected/SIGNED.json',('timings','elapsed_seconds'))
        receipt=r/'final.json'
        receipt.write_bytes(original.contained(r,engine/'check_final.py',r,engine/'interval_gate.py',timeout=20,capture=True))
        original.compare(receipt,s/'expected/FINAL.json',('native_result_sha256','signed_result_sha256'))
        final=json.loads(receipt.read_text());signed_receipt=r/'producer54/validation_signed/RESULT.json'
        assert final['native_result_sha256']==sha256(native.read_bytes()).hexdigest()
        assert final['signed_result_sha256']==sha256(signed_receipt.read_bytes()).hexdigest()
        report=dict(stage='signed',consumed_native_sha256=final['native_result_sha256'],
                    consumed_native_math_sha256=mathematical_native(native),
                    fresh_signed_sha256=final['signed_result_sha256'],
                    fresh_final_sha256=sha256(receipt.read_bytes()).hexdigest(),
                    final_receipt=final,native_receipt_origin='authenticated frozen source receipt, mathematically equal to required fresh native command')
        print('PASS_STATELESS7544_FRESH_SIGNED_AND_FINAL',flush=True)
    report['native_adapter']=json.loads((r/'receipts/NATIVE-ADAPTER.json').read_text())
    report['signed_adapter']=json.loads(signed_adapter)
    report['adapted_native_sha256']=sha256((r/'producer54/validation_native/run.py').read_bytes()).hexdigest()
    report['adapted_signed_sha256']=sha256(signed.read_bytes()).hexdigest()
    (r/'REPLAY-STAGE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    original.authenticate()


if __name__=='__main__':
    assert __debug__ and sys.version_info[:2]==(3,12)
    main()
