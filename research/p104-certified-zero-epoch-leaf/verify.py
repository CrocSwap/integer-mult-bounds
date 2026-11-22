#!/usr/bin/env python3
"""Cold replay of the source-bound, exploratory zero-loan controls."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import os,shutil,subprocess,sys,tarfile

HERE=Path(__file__).resolve().parent
ARCHIVE='predecessor-8030.tar.gz'
PINS={ARCHIVE:'769d5a05cc1373fa22ed5956af636992fcd19d7e5c1753a32033a73c358cd31c',
      'pinned/strong-bit.json.gz':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326',
      'pinned/EFREE-CALLER.json.gz':'757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b',
      'pinned/price_audit.py':'ca650d573f605bf51a8806a772903b6775cd036dfbfe7f043eccd3e51bc9977b'}
for name,digest in PINS.items():
    if sha256((HERE/name).read_bytes()).hexdigest()!=digest:raise ValueError('Pinned input differs: '+name)
checks=[
 ('constant_nested_witness.py','PASS_ACTUAL_RETAINED_CONSTANT_SUBDOMAIN_COUNTEREXAMPLES'),
 ('paired_constant_witness.py','PASS_RETAINED_PAIRED_KERNELS'),
 ('clean_slice.py','PASS_PREEXISTING_CLEAN_ROOT_SLICE_LOCAL_ONLY'),
 ('single_source_scan.py','PASS_NO_PAID_TAINT_SINGLE_SOURCE_SCAN'),
 ('native_scheduler_control.py','PASS_ACTUAL_POWERED_ITERATOR_TOY_PREFIX_CONTROL'),
 ('physical_zero_v1.py','PASS_PHYSICAL_V1_ZERO_SKIP_AND_INVOLUTION'),
 ('bounded_epoch_control.py','PASS_BOUNDED_CERTIFIED_EPOCH_AND_UNSAFE_CONTROL'),
 ('economics_zero_family.py','PASS_ZERO_FAMILY_STILL_INSUFFICIENT_AT_TRIAL'),
]
with TemporaryDirectory(prefix='zero-epoch-cold-') as temporary:
    root=Path(temporary)
    with tarfile.open(HERE/ARCHIVE,'r:gz') as packet:
        for member in packet:
            path=Path(member.name)
            if path.is_absolute() or '..' in path.parts or not member.isfile():
                raise ValueError('Unexpected predecessor archive member')
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True)
            with packet.extractfile(member) as inp, dest.open('wb') as out:shutil.copyfileobj(inp,out)
    for path in HERE.glob('*.py'):
        if path.name!='verify.py':shutil.copy2(path,root/path.name)
    shutil.copytree(HERE/'pinned',root/'pinned')
    for script,marker in checks:
        completed=subprocess.run([sys.executable,'-I','-B',str(root/script)],cwd=root,
                                 capture_output=True,text=True,timeout=180)
        if completed.returncode or marker not in completed.stdout:
            print(completed.stdout);print(completed.stderr,file=sys.stderr)
            raise RuntimeError('Failed check '+script)
        print(marker,flush=True)
print('PASS_CERTIFIED_ZERO_EPOCH_EXPLORATORY_COLD_REPLAY')
