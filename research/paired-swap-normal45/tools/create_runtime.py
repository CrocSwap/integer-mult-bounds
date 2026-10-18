#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Create a fresh isolated replay venv with deterministic LF source writing.
Does not install dependencies or alter the caller's Python/Git configuration.
"""
from pathlib import Path
import argparse,json,os,venv
LF = """# Task-local deterministic text serialization for inherited source generators.
from pathlib import Path
_original_write_text = Path.write_text
def _lf_write_text(self, data, encoding=None, errors=None, newline=None):
    return _original_write_text(self, data, encoding=encoding, errors=errors,
                                newline='\\n' if newline is None else newline)
Path.write_text = _lf_write_text
"""
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve()
 if out.exists():raise ValueError('requires a fresh runtime path')
 venv.EnvBuilder(with_pip=True).create(out)
 if os.name=='nt':site=out/'Lib/site-packages';python=out/'Scripts/python.exe'
 else:
  sites=list((out/'lib').glob('python*/site-packages'))
  if len(sites)!=1:raise ValueError('unique isolated site-packages required')
  site=sites[0];python=out/'bin/python'
 target=site/'sitecustomize.py'
 if target.exists():raise ValueError('refusing to overwrite a site customization')
 target.write_text(LF,encoding='utf-8',newline='\n')
 (out/'REPLAY-RUNTIME.json').write_text(json.dumps({'scope':'Fresh task-local virtual environment only. Dependencies not installed. No global configuration change.','python':str(python),'lf_source_serialization':True},indent=2)+'\n',encoding='utf-8',newline='\n')
 print(python)
if __name__=='__main__':main()
