#!/usr/bin/env python3
"""Replay the attributed transfer controls; never re-run unchanged large producers."""
from pathlib import Path
from hashlib import sha256
import argparse,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
CODE=ROOT/'references/rad20/code'
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);args=p.parse_args()
 out=args.output_dir or Path(tempfile.mkdtemp(prefix='semantic-bulk-controls-'))
 out.mkdir(parents=True,exist_ok=True)
 for name,short in [('review_arbitrary_routing.py','router'),('review_bulk_resampling.py','bulk'),('review_bulk_boundary_negatives.py','bulk-negative'),('review_balanced_transform.py','balanced'),('review_phase_inverse.py','phase'),('review_banded_inverse.py','banded')]:
  subprocess.run([sys.executable,str(CODE/name),'--output',str(out/(short+'.json'))],check=True)
 sys.path.insert(0,str(CODE))
 import review_semantic_guard as s
 import review_whole_complex_transfer as w
 x=dict(status='PASS imported semantic fixed-grid controls and nested product-row controls',
  semantic=s.controls(),recurrences=s.recurrences(),nested_rows=w.nested_rows(),
  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in [CODE/'review_semantic_guard.py',CODE/'review_whole_complex_transfer.py']},
  scope='Pure imported controls; historical CLI reference is not claimed as a new-reference test. See the written PR21-specific transfer.')
 (out/'semantic.json').write_text(json.dumps(x,indent=2)+'\n');print('PASS transfer controls:',out)
if __name__=='__main__':main()
