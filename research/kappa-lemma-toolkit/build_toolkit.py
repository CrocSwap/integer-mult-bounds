"""Assemble a standalone Mathlib-only source; no source-package imports remain."""
from pathlib import Path
import argparse,hashlib,re
HERE=Path(__file__).resolve().parent
PARTS=[HERE.parent/'selective-borrowing-kappa/lean/Factors.lean',HERE.parent/'selective-borrowing-kappa/lean/Feedback.lean',HERE/'NativeAlgebra.lean',HERE/'Recursion.lean',HERE/'MomentTransfer.lean']
def source():
    imports=[];blocks=[]
    for path in PARTS:
        raw=path.read_text(encoding='utf-8-sig');body=[]
        for line in raw.splitlines():
            if line.startswith('import '):
                if not line.startswith('import Mathlib'):raise ValueError('non-Mathlib import: '+line)
                if line not in imports:imports.append(line)
            elif not line.startswith('#print axioms '):body.append(line)
        blocks.append('/- Source part: '+path.name+'; SHA256 '+hashlib.sha256(path.read_bytes()).hexdigest()+' -/\n'+'\n'.join(body).strip())
    return '\n'.join(imports)+'\n\n/-! Standalone exact native, recursion and moment lemmas. Apache-2.0.\nSee NOTICE.md for retained sources and scope. Eighty-seven named theorem APIs;\nhelper facts and extended retained algebra are counted as APIs, not discoveries. -/\n\n'+'\n\n'.join(blocks)+'\n'
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);parser.add_argument('--check',action='store_true');a=parser.parse_args();text=source()
    if a.check:
        if (HERE/'Toolkit.lean').read_text(encoding='utf-8')!=text:raise ValueError('standalone source differs from parts')
        print('PASS_STANDALONE_MATHLIB_ONLY_SOURCE_ASSEMBLY')
    elif a.out:
        if a.out.resolve().is_relative_to(HERE.parent):raise ValueError('write regenerated source outside the source packages')
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(text,encoding='utf-8')
    else:parser.error('use --check or --out')
