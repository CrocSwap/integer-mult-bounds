#!/usr/bin/env python3
"""Fresh admission of PR304's stronger complex supplier through the source-bound adapter vendored by PR309.

The archive vendor/complex304.zip (PR309, Dugongue) is pinned by SHA-256; every member must match
vendor/complex304-inventory.json exactly. It is extracted to a fresh directory and its own verify-complex.py runs:
gx.check1 scalar replay of the actual PR304 gcert/1 program, label/child counts, scalar expansions, splice
chronology and controls, cover/router/precision/row bills and two rational moment engines (rejecting 7636/10^7).
Usage: complex304_admit.py OUTPUT_DIR --cxx CXX [--boost-include DIR]"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
import argparse,hashlib,json,os,subprocess,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
ZIP_SHA='0412e86f9c58cb6e3d93129c7a8bb7bb0fef6323f95a55d695f1d2dfa674a22d'
def sha(b):return hashlib.sha256(b).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--cxx',default='c++');ap.add_argument('--boost-include',type=Path);a=ap.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);src=out/'source';src.mkdir()
ar=ROOT/'vendor/complex304.zip';assert sha(ar.read_bytes())==ZIP_SHA,'archive hash'
inv=json.loads((ROOT/'vendor/complex304-inventory.json').read_text())['files']
with zipfile.ZipFile(ar) as z:
    names=z.namelist();assert len(names)==len(inv) and set(names)==set(inv),'archive membership'
    for info in z.infolist():
        p=PurePosixPath(info.filename);assert not p.is_absolute() and '..' not in p.parts and '\\' not in info.filename and ':' not in info.filename
        data=z.read(info);assert sha(data)==inv[info.filename],info.filename
        dest=src.joinpath(*p.parts);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
cmd=[sys.executable,'-B',str(src/'verify-complex.py'),'--output',str(out/'replay'),'--cxx',a.cxx]
if a.boost_include:cmd+=['--boost-include',str(a.boost_include.resolve())]
subprocess.run(cmd,check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
cert=json.loads((out/'replay/CERTIFICATE.json').read_text());native=json.loads((out/'replay/NATIVE.json').read_text())
assert cert['status']=='PASS_FRESH_SOURCE_BOUND_STRONGER_COMPLEX_ADMISSION' and native['status']=='PASS_NATIVE_ACTUAL_COMPLEX_LEDGER_TWO_MOMENTS_AND_OPERATION_GUARDS'
assert cert['program_compressed_sha256']==native['program_compressed_sha256']=='aa7973b6f95fb8834f4b83e5f8c6a6f87158835e3e7bced93097f11d2c40102a'
assert cert['tensor_saving']=='7635001/10000000000' and native['rejected_saving']=='7636/10000000'
assert int(native['physical_row_coefficient'])<cert['retained_row_coefficient']==20161
res={'status':'PASS_FRESH_PR304_COMPLEX_SUPPLIER','archive_sha256':ZIP_SHA,'tensor_saving':cert['tensor_saving'],'priced_complex_saving':'7635/10000000',
     'physical_row_coefficient':native['physical_row_coefficient'],'retained_row_coefficient':20161,'certificate_sha256':sha((out/'replay/CERTIFICATE.json').read_bytes()),
     'native_sha256':sha((out/'replay/NATIVE.json').read_bytes())}
(out/'COMPLEX304.json').write_text(json.dumps(res,sort_keys=True,indent=2)+'\n');print('PASS PR304 complex supplier',res['tensor_saving'],flush=True)
