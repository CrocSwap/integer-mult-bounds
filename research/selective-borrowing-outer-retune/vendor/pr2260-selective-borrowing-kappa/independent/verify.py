#!/usr/bin/env python3
"""Read-only package replay. Generated results are written to a fresh work directory."""
import argparse,hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
from types import SimpleNamespace
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def replay(work):
    for relative,pin in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8')).items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()!=pin:
            raise ValueError('frozen package source differs: '+relative)
    spec=importlib.util.spec_from_file_location('selective_borrowing_independent_audit',HERE/'audit.py')
    audit=importlib.util.module_from_spec(spec);sys.modules[spec.name]=audit;spec.loader.exec_module(audit)
    args=SimpleNamespace(
        parent=HERE/'inputs/T8-PARENT.json.gz',
        parent_sha256='025448abdf2012d327e50a009084e1501690d05e650300d2982836aa0350ae00',
        phases=ROOT/'owners/inputs/DATA-PHASES.json',plan=ROOT/'owners/inputs/PLAN.json',
        owners=ROOT/'owners/OWNERS.json.gz',
        forward_trace=ROOT/'local/data/forward.json',backward_trace=ROOT/'local/data/backward.json',
        forward_native=ROOT/'local/data/native-forward.json.gz',backward_native=ROOT/'local/data/native-backward.json.gz',
        forward_wrapper=ROOT/'local/data/wrappers-forward.json',backward_wrapper=ROOT/'local/data/wrappers-backward.json',
        engine=ROOT/'local/vendor/native_verify.py',out=work/'actual-family')
    audit.audit(args)
    actual=json.loads((args.out/'RESULT.json').read_text(encoding='utf-8'))
    expected=json.loads((HERE/'EXPECTED.json').read_text(encoding='utf-8'))
    for key,value in expected.items():
        if actual.get(key)!=value:raise ValueError('frozen independent receipt differs: '+key)
    print('PASS: actual family tags, local Gaussian ABI, literal charts, untouched windows, factor partition, translations and mutation controls')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,help='a nonexistent output directory; source package remains read-only')
    args=parser.parse_args()
    if args.work is None:
        with tempfile.TemporaryDirectory(prefix='selective-borrowing-independent-') as directory:replay(Path(directory))
    else:
        if args.work.resolve().is_relative_to(ROOT):raise ValueError('work directory must be outside the source package')
        args.work.mkdir(parents=True,exist_ok=False);replay(args.work)

if __name__=='__main__':main()
