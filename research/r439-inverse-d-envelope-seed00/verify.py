"""Replay all 5,563 signed inverse-D prefix bounds. Apache-2.0.
Substantial OpenAI Codex assistance for @woklerx. No native admission.
"""
import argparse,ast,copy,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import envelope
import independent as I
need=I.need
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
INPUTS=(
 'research/r439-helper-stars-seed19/candidate.json.gz',
 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
 'research/e8-bit-p111-tuned/code/xcheck_p.py',
 'research/e8-bit-p111-tuned/tune/EXPECTED.json',
 'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py',
 'research/e8-bit-p111-tuned/code/adapt9p.py')


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)


def loads(raw):
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'duplicate key');out[k]=v
        return out
    def bad(x):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)


def read(path):
    raw=path.read_bytes()
    return loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)


def same(a,b,message):need(canonical(a)==canonical(b),message)


def pins_check(pins):
    need(set(pins)=={'base_commit','files'}and pins['base_commit']==BASE,'frozen base')
    need(set(pins['files'])==set(INPUTS),'exact source inventory')
    for p in INPUTS:need(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pins['files'][p],'source SHA256')


def lowering():
    source=(ROOT/INPUTS[4]).read_text()
    adapter=ast.parse((ROOT/INPUTS[5]).read_text())
    edits=[n.value for n in adapter.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='EDITS'for t in n.targets)]
    need(len(edits)==1,'unique adaptation table')
    pairs=[v for k,v in zip(edits[0].keys,edits[0].values)if ast.literal_eval(k)=='global_k.py']
    need(len(pairs)==1,'unique global adaptation')
    for i,pair in enumerate(pairs[0].elts[1].elts):
        old=ast.literal_eval(pair.elts[0]);need(source.count(old)==1,'adaptation anchor')
        if i==0:
            # Only the first pair formats local import paths; it changes no
            # mathematical statement. Every other exact edit is replayed.
            need(old.startswith('sys.path.insert('),'import-only path edit')
            continue
        source=source.replace(old,ast.literal_eval(pair.elts[1]))
    tree=ast.parse(source)
    expected=ast.parse('[1,x,y,-c if reverse else c,f,int(reverse)]',mode='eval').body
    need(any(isinstance(n,ast.List)and ast.dump(n)==ast.dump(expected)for n in ast.walk(tree)),'actual signed inverse ADD emission')
    norm=ast.parse('norm[x]+=abs(c)*norm[y]').body[0]
    need(any(isinstance(n,ast.AugAssign)and ast.dump(n)==ast.dump(norm)for n in ast.walk(tree)),'existing positive envelope')
    formula=ast.parse('(1<<nb)*cf**(K+1)*cb**K',mode='eval').body
    need(any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='prefix'for t in n.targets)and ast.dump(n.value)==ast.dump(formula)for n in ast.walk(tree)),'prefix formula')
    bridge=ast.parse('nb==6*(K-1)',mode='eval').body
    need(any(isinstance(n,ast.Compare)and ast.dump(n)==ast.dump(bridge)for n in ast.walk(tree)),'bridge count')
    return len(pairs[0].elts[1].elts)-1


def run():
    pins=read(HERE/'SOURCES.json');pins_check(pins);adaptations=lowering()
    word=read(ROOT/INPUTS[0]);original=read(ROOT/INPUTS[1])
    need(word['v']==111 and word['R']==439,'frozen dimensions')
    need(all(type(f)is int and f==0 and 111<=d<661 and len(ss)==len(set(ss))and all(type(s)is int and 111<=s<661 and s!=d for s in ss)for f,d,ss in word['D']),'common frame-zero legal D')
    result=envelope.compute(word);weights,prepeak=I.entry_box(word)
    same(weights,result['entry_weights'],'independent entry weights');need(prepeak==result['pre_D_reverse_peak'],'entry peak')
    bounds,supports=I.columns(word,weights)
    same(bounds,result['prefix_destination_bounds'],'every independent prefix bound')
    need(max(max(weights),max(bounds))==result['weighted_box_D_peak'],'all rows at all prefixes')
    witness=result['attaining_box_witness'];same(I.row_backward(word,witness),witness['coefficients'],'backward output functional')
    need(supports[witness['prefix_length']-1]==len(witness['coefficients']),'peak support')
    I.attain(word,weights,witness)
    need(I.mod_two_boundary(word)==I.mod_two_boundary(original),'inherited semantic D')
    need(result['reverse_D_ADDs']==5563 and result['complete_ADDs']==11783,'unchanged paid ADD bill')
    expected=read(ROOT/INPUTS[3]);need(expected['nine']['bit']['charged_prefix_bits']==192,'retained production allowance')
    spec=importlib.util.spec_from_file_location('pinned_geometry',ROOT/INPUTS[2]);owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
    W,lab,full,H,C,info=owner.check(word)
    need(not H['H2_D_frame0_targets_from_helpers']and not C['K_equals_D'],'semantic interface scope')
    need(all(v for k,v in H.items()if not k.startswith('H2'))and all(v for k,v in C.items()if k!='K_equals_D'),'remaining source interface')
    controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name);return
        raise ValueError('control accepted: '+name)
    reject('unsigned inverse cannot use signed bound',lambda:need(result['old_reverse_positive_peak']<=result['hybrid_reverse_peak'],'unsigned exceedance'))
    altered=copy.deepcopy(witness);altered['weighted_norm']-=1
    reject('one-smaller weighted peak',lambda:I.attain(word,weights,altered))
    altered=copy.deepcopy(witness);altered['coefficients'][0][1]*=-1
    reject('wrong extremizing sign',lambda:I.attain(word,weights,altered))
    altered=copy.deepcopy(witness);altered['prefix_length']-=1
    reject('omitted peak gate',lambda:I.attain(word,weights,altered))
    damaged=list(bounds);damaged[len(damaged)//2]-=1
    reject('interior prefix receipt mutation',lambda:same(damaged,result['prefix_destination_bounds'],'prefix mutation'))
    reject('peak ignores entry weights',lambda:need(sum(abs(c)for r,c in witness['coefficients'])==witness['weighted_norm'],'weighted box'))
    missing=loads(canonical(pins));del missing['files'][INPUTS[4]]
    reject('missing lowering source',lambda:pins_check(missing))
    reject('duplicate JSON',lambda:loads('{"n":1,"n":2}'))
    reject('nonfinite JSON',lambda:loads('{"n":NaN}'))
    reject('Boolean receipt number',lambda:same({'n':1},{'n':True},'typed JSON'))
    return {'format':'r439-inverse-D-envelope/1','status':'PASS_R439_INVERSE_D_ENVELOPE','base_commit':BASE,'seed':0,
        'source_pins':pins,'envelope':result,'independent_columns':661,'independent_prefixes':len(bounds),
        'mathematical_adapter_edits_replayed':adaptations,
        'owning_geometry':lab,'interface_hypotheses':H,'interface_conclusions':C,'controls_rejected':controls,
        'retained_production_prefix_bits':192,'scope':'tight weighted entry-box bound for signed frame-zero D; no physical attainability or native invoice admission claim'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-certificate',action='store_true');a=p.parse_args()
    result=run()
    if a.write_certificate:(HERE/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    else:same(result,read(HERE/'CERTIFICATE.json'),'complete certificate mismatch')
    z=result['envelope']
    print('PASS_R439_INVERSE_D_ENVELOPE B='+str(z['old_reverse_positive_peak'])+'->'+str(z['hybrid_reverse_peak'])+' prefixes=5563 columns=661 controls='+str(len(result['controls_rejected']))+' no_new_kappa')
if __name__=='__main__':main()
