# SPDX-License-Identifier: Apache-2.0
import sys
if not __debug__ or sys.flags.optimize:raise RuntimeError('Enabled assertions required before owner replay')
from pathlib import Path
import json,hashlib,importlib.util,argparse,os
P=Path(__file__).resolve().parent
def need(x,m):
 if not x:raise ValueError(m)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--price-dir',type=Path,default=P.parent);a=ap.parse_args()
 need(bool(os.environ.get('OWNER_SOURCE_REPO')),'explicit source required')
 for n,h in json.loads((P/'ARTIFACTS.json').read_text()).items():
  f=P/n;need(f.is_file()and not f.is_symlink()and hashlib.sha256(f.read_bytes()).hexdigest()==h,'frozen owner artifact '+n)
 c=load('t450_check',P/'verify_candidate.py');actual=c.check(json.loads((P/'CANDIDATE.json').read_text()),'concatenated')
 sys.modules['price']=load('price',a.price_dir/'price.py');priced=load('verify_price',a.price_dir/'verify_price.py').check(actual['profile'])
 print(json.dumps({'aggregate':actual,'price':priced},sort_keys=True));print('PASS_T450_AGGREGATE_NOT_LITERAL_OR_FULL_ADMISSION')
if __name__=='__main__':main()
