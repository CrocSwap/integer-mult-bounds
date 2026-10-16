# SPDX-License-Identifier: Apache-2.0
"""Create an isolated replay interpreter with LF-default Path.write_text outputs.
No installed package, source validator or global setting is changed.
"""
import argparse, importlib.metadata as md, json, os, sys, venv
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve();root=Path(__file__).resolve().parents[1]
    if out.exists() or out.is_relative_to(root) or root.is_relative_to(out):raise ValueError('fresh external runtime required')
    paths=set();versions={}
    for name in ['numpy','scipy','sympy','mpmath','psutil','gmpy2']:
        try:
            d=md.distribution(name);versions[name]=d.version;paths.add(str(Path(d.locate_file('')).resolve()))
        except md.PackageNotFoundError:
            versions[name]=None
    if any(versions[n] is None for n in ['numpy','scipy','sympy','mpmath']):raise ValueError('install replay dependencies in the launching environment first')
    venv.EnvBuilder(with_pip=False).create(out)
    site=out/'Lib/site-packages' if os.name=='nt' else out/'lib'/('python'+str(sys.version_info.major)+'.'+str(sys.version_info.minor))/'site-packages'
    (site/'replay-dependencies.pth').write_text('\n'.join(sorted(paths))+'\n',encoding='utf-8',newline='\n')
    patch="from pathlib import Path\n_original_write_text = Path.write_text\ndef _lf_write_text(self, data, encoding=None, errors=None, newline=None):\n    return _original_write_text(self, data, encoding=encoding, errors=errors, newline='\\n' if newline is None else newline)\nPath.write_text = _lf_write_text\n"
    (site/'sitecustomize.py').write_text(patch,encoding='utf-8',newline='\n')
    (out/'REPLAY-RUNTIME.json').write_text(json.dumps(dict(scope='Task-local LF output default; installed dependency locations reused read-only; no validator changes.',versions=versions),indent=2)+'\n',encoding='utf-8',newline='\n')
    exe=out/'Scripts/python.exe' if os.name=='nt' else out/'bin/python'
    print(str(exe))
if __name__=='__main__':main()
