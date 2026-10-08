"""Self-contained upstream patch retaining and attributing each prior argument."""
from pathlib import Path
import argparse,difflib,importlib.util,re,shutil,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from witness import certificate
import make_batched_patch


def files():
    path=ROOT/'research/batched-followup/make_patch.py'
    spec=importlib.util.spec_from_file_location('h30_integration',path)
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    prior.certificate=lambda roles:certificate()
    def redirect(text):
        return text.replace('lem:dimension30-chunk-swap','lem:source-corner-chunk-swap').replace(
            'prop:dimension30-simultaneous-layer','prop:source-corner-simultaneous-layer')
    rows=[]
    for name,old,text in prior.files():
        if name.endswith(('main.tex','00-introduction.tex')):
            assert '12649/100000000000' in text
            text=text.replace('12649/100000000000','90799/100000000000')
            if name.endswith('main.tex'):
                marker='It changes the bit producer dimension and reuses the complex network.'
                assert marker in text
                text=text.replace(marker,marker+'\nThe present combination uses auxiliary source frames and a third complex\n'
                    'class contributed by eumemic with Claude (Anthropic) assistance in PR 13,\n'
                    'plus two additional data-corner blocks developed by Rohan Arun\n'
                    'with substantial OpenAI Codex assistance.')
        elif name.endswith('04-swap.tex'):
            text+='\n'+(HERE/'pr13/notes/source-frame-bit.tex').read_text()
            text+='\n'+(ROOT/'research/controlled-corners/proof.tex').read_text()
            text+='\n'+(HERE/'proof.tex').read_text()
        elif name.endswith('05-layers.tex'):
            marker=r'\begin{proposition}[Layer using dimension-thirty bit interchange]'
            assert text.count(marker)==1
            active=redirect(text[text.index(marker):])
            active=active.replace('[Layer using dimension-thirty bit interchange]',
                                  '[Layer using source frames and data corners]')
            replacements={
                '1-253/10^9':'1-1816/10^9','1-7/10^7':'1-18179/10^{10}',
                'replaces the two selected classes':'replaces the three selected classes',
                'sec:batched-complex-parameters':'sec:source-corner-complex',
                'widths $f$, $21896f$, or $21168f$':'widths $f$, $21896f$, $21168f$, or $21141f$',
            }
            for before,after in replacements.items():
                assert before in active,before
                active=active.replace(before,after)
            text+='\n'+(HERE/'pr13/notes/source-frame-complex.tex').read_text()
            text+='\n'+(HERE/'complex.tex').read_text()+'\n'+active
        elif name.endswith(('06-transforms.tex','07-resampling.tex')):text=redirect(text)
        elif name.endswith('08-assembly.tex'):
            text=redirect(text)
            replacements={
                r'\frac{253}{10^9}':r'\frac{1816}{10^9}',
                r'\frac7{10^7}':r'\frac{18179}{10^{10}}',
                r'\frac{12649}{100000000000}':r'\frac{90799}{100000000000}',
                '1-6993/10^{10}':'1-18160821/10^{13}',
                r'd^{100000000}\le b^{49999993}':r'd^{1000000}\le b^{499999}',
                '49999993/100000000':'499999/1000000',
                '50000007/200000000':'500001/2000000',
                '50000007/100000000':'500001/1000000',
                r'p^{7/50000000}':r'p^{1/500000}',
            }
            for before,after in replacements.items():
                # The kappa display already comes from the overridden certificate.
                if before==r'\frac{12649}{100000000000}' and before not in text:continue
                assert before in text,before
                text=text.replace(before,after)
        rows.append((name,old,text))
    allfiles={str(p.relative_to(ROOT/'upstream')):p.read_text() for p in (ROOT/'upstream').rglob('*.tex')}
    allfiles.update({name:text for name,_,text in rows});alltext='\n'.join(allfiles.values())
    labels=re.findall(r'\\label\{([^}]+)\}',alltext)
    assert len(labels)==len(set(labels))
    assert not set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',alltext))-set(labels)
    assembly=next(s for n,_,s in rows if n.endswith('08-assembly.tex'))
    assert '49999993' not in assembly and r'\frac{253}{10^9}' not in assembly
    assert r'd^{1000000}\le b^{499999}' in assembly
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--materialize',type=Path);args=p.parse_args()
    rows=files()
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
        fromfile='a/'+name,tofile='b/'+name)) for name,old,new in rows)
    (ROOT/'patches/source-frame-corners.patch').write_text(patch)
    if args.materialize:
        assert args.materialize.resolve() not in (ROOT.resolve(),(ROOT/'upstream').resolve())
        shutil.copytree(ROOT/'upstream',args.materialize,dirs_exist_ok=True)
        for name,_,text in rows:(args.materialize/name).write_text(text)
    print('PASS integrated bit and three-class complex interfaces, assembly and all references')


if __name__=='__main__':main()
