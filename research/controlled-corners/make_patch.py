"""Integrate controlled-corner batching while retaining preceding proofs."""
from pathlib import Path
import argparse
import difflib
import importlib.util
import re
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from witness import certificate
# Preload the upstream patch modules before loading the earlier wrapper.
import make_batched_patch


def files():
    path=ROOT/'research/batched-followup/make_patch.py'
    spec=importlib.util.spec_from_file_location('dimension30_patch',path)
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    prior.certificate=certificate
    def redirect(text):
        return text.replace('lem:dimension30-chunk-swap','lem:controlled-corner-chunk-swap').replace(
            'prop:dimension30-simultaneous-layer','prop:controlled-corner-simultaneous-layer')
    result=[]
    for name,old,text in prior.files():
        if name.endswith(('main.tex','00-introduction.tex')):
            assert '12649/100000000000' in text
            text=text.replace('12649/100000000000','20156/100000000000')
            if name.endswith('main.tex'):
                marker='It changes the bit producer dimension and reuses the complex network.'
                assert marker in text
                text=text.replace(marker,marker+'\nThe present continuation additionally batches two controlled\n'
                    'corner profiles on three edge classes, with the same producer and complex network.')
        elif name.endswith('04-swap.tex'):
            text+='\n'+(HERE/'proof.tex').read_text()
        elif name.endswith('05-layers.tex'):
            marker=r'\begin{proposition}[Layer using dimension-thirty bit interchange]'
            assert text.count(marker)==1
            active=text[text.index(marker):]
            active=redirect(active).replace('1-253/10^9','1-40315/10^{11}')
            active=active.replace('[Layer using dimension-thirty bit interchange]',
                                  '[Layer using controlled-corner interchange]')
            text+='\n\\subsection{Consuming the controlled-corner exponent}\n'+active
        elif name.endswith(('06-transforms.tex','07-resampling.tex')):
            text=redirect(text)
        elif name.endswith('08-assembly.tex'):
            text=redirect(text)
            replacements={
                r'\frac{253}{10^9}':r'\frac{40315}{10^{11}}',
                r'd^{100000000}\le b^{49999993}':r'd^{200000000}\le b^{99999979}',
                '49999993/100000000':'99999979/200000000',
                '50000007/200000000':'100000021/400000000',
                '50000007/100000000':'100000021/200000000',
                r'p^{7/50000000}':r'p^{21/100000000}',
            }
            for before,after in replacements.items():
                assert before in text,before
                text=text.replace(before,after)
        result.append((name,old,text))
    all_files={str(p.relative_to(ROOT/'upstream')):p.read_text() for p in (ROOT/'upstream').rglob('*.tex')}
    all_files.update({name:text for name,_,text in result})
    text='\n'.join(all_files.values())
    labels=re.findall(r'\\label\{([^}]+)\}',text)
    assert len(labels)==len(set(labels))
    assert not set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',text))-set(labels)
    assembly=next(new for name,_,new in result if name.endswith('08-assembly.tex'))
    assert r'\frac{253}{10^9}' not in assembly and '49999993' not in assembly
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--materialize',type=Path)
    args=parser.parse_args()
    rows=files()
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
             fromfile='a/'+name,tofile='b/'+name)) for name,old,new in rows)
    (ROOT/'patches/controlled-corners.patch').write_text(patch)
    if args.materialize:
        assert args.materialize.resolve() not in (ROOT.resolve(),(ROOT/'upstream').resolve())
        shutil.copytree(ROOT/'upstream',args.materialize,dirs_exist_ok=True)
        for name,_,text in rows:(args.materialize/name).write_text(text)
    print('PASS controlled-corner interfaces, active assembly and source references')


if __name__=='__main__':main()
