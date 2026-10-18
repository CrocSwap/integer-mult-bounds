"""Prepare an explicitly adapted U10/T37 finite replay; source packages stay read-only.

Derived from Chafik Boukhalfa's PR890, Hao Yan's PR858, Jeremy Kothe's PR799,
and the retained PR869/870 and PR741/589 lineages. Apache-2.0.
The verification driver creates all outputs outside the source checkout.
"""
import hashlib, io, json, os, re, tokenize
from pathlib import Path
from common import ROOT,P,T21,read,load
OUT=Path(os.environ.get('T37_WORK',ROOT.parent/'t37-work')).resolve()
NUM={21:37,189:333,95256:167832,18816:33152,32424:55832,32938:56346,
     13608:22680,20720:44128,6720:11840,42336:74592,6292:11086}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def numbers(text):
    tokens=[]
    for t in tokenize.generate_tokens(io.StringIO(text).readline):
        if t.type==tokenize.NUMBER and t.string.isdecimal() and int(t.string)in NUM:
            t=t._replace(string=str(NUM[int(t.string)]))
        tokens.append(t)
    return tokenize.untokenize(tokens)
def transform(text):
    text=numbers(text).replace('(8, 8, 5)','(8, 8, 8, 8, 5)').replace('[8, 8, 5]','[8, 8, 8, 8, 5]')
    return text.replace('T21','T37').replace('t21','t37').replace('8+8+5','8+8+8+8+5').replace('8-8-5','8-8-8-8-5')
def replace(text,a,b,count=1):
    assert text.count(a)==count,(a,text.count(a),count)
    return text.replace(a,b)
def expected_adaptations():
    """Derive the complete adapter text from immutable source and fixed edits."""
    receipts={}
    for name in ('build_parent.py','check_parent.py'):
        source=T21/name;text=source.read_text();text=transform(text)
        # Source resolution remains the pinned T21 package; only output parameters change.
        text='import sys\nsys.path.insert(0,'+repr(str(T21))+')\n'+text
        if name=='build_parent.py':
            text=replace(text,'((48, 11086), (3, 1), (1, 3))','((48, 11086), (1, 6))')
            # U10: the frozen plan profile is 333 x the U10 local profile (this package's CLAIM), not U8's.
            text=replace(text,"read(HERE/'data/CLAIM.json')['local_profile']","read("+repr(str(P/'CLAIM.json'))+")['local_profile']")
            text=replace(text,"mode='gauge44-U8-t37-","mode='gauge44-U10-t37-")
            # U10: rebind the inherited U8 provider identities in the T8 plan registry to the frozen U10 values
            # (construction/u10/PROVIDER-U10.json); bind_providers_portable.py re-checks them against fresh U10 locals.
            text=replace(text,"    plan = read(HERE/'vendor/pr870/data/T8/PLAN.json')\n",
                "    plan = read(HERE/'vendor/pr870/data/T8/PLAN.json')\n"
                "    import json as _json\n"
                "    _u10 = read("+repr(str(P/'construction/u10/PROVIDER-U10.json'))+")\n"
                "    _text = _json.dumps(plan)\n"
                "    for _old, _new in _u10['rebind'].items():\n"
                "        require(_text.count(_old) > 0, 'U10 rebind source identity present')\n"
                "        _text = _text.replace(_old, _new)\n"
                "    plan = _json.loads(_text)\n"
                "    plan['provider_registry']['gauge44']['actual_paid_profile'] = _u10['actual_paid_profile']\n")
        receipts[name]=dict(source=source,text=text)
    source=T21/'vendor/pr870/code'
    edit_table=read(T21/'data/ADAPTER-EDITS.json')
    for path in sorted(source.glob('*.py')):
        text=path.read_text();edits=[]
        for before,after,count in edit_table.get(path.name,[]):
            after=re.sub(r'\b(?:21|189|95256|18816|32424|32938|13608|20720|6720|42336|6292)\b',lambda m:str(NUM[int(m[0])]),after)
            after=after.replace('T21','T37').replace('all189','all333').replace('8,8,5','8,8,8,8,5').replace('three bank groups','five bank groups').replace('T16 plus T5 nine-role trade','T21 plus T16 eight-role trade')
            text=replace(text,before,after,count);edits.append([before,after,count])
        extra=[]
        if path.name=='invoice_allcold.py':extra=[('payload=512','payload=1024'),("previous['charged_prefix_bits']==payload","previous['charged_prefix_bits']<=payload")]
        if path.name=='assemble.py':extra=[("invoice['charged_prefix_bits']==512","invoice['charged_prefix_bits']==1024"),("invoice['row_prefix_extra']==1024","invoice['row_prefix_extra']==2048"),('2*stock.bit_length()+9909+252+1024','2*stock.bit_length()+9909+252+2048'),('(4+512)','(4+1024)',2)]
        for item in extra:
            a,b,*cnt=item;count=cnt[0]if cnt else 1;text=replace(text,a,b,count);edits.append([a,b,count])
        receipts['runtime/'+path.name]=dict(source=path,text=text,edits=edits)
    return receipts

def main():
    assert 'T37_WORK' in os.environ and 'T37_BASELINE' in os.environ, 'Run verify.py'
    assert OUT.exists() and not OUT.is_relative_to(ROOT)
    assert Path(os.environ['T37_BASELINE']).is_dir()
    adapted=OUT/'adapted';adapted.mkdir()
    runtime=OUT/'runtime'
    load(T21/'source_adapters.py','source_adapters').materialize(runtime)
    # Preserve the predecessor receipt as explicitly intermediate provenance.
    (runtime/'ADAPTERS.json').rename(runtime/'T21-INTERMEDIATE-ADAPTERS.json')
    receipts={}
    for name, record in expected_adaptations().items():
        dest=runtime/'code'/name.split('/',1)[1] if name.startswith('runtime/') else adapted/name
        dest.write_text(record['text'],encoding='utf-8',newline='\n')
        receipts[name]=dict(source_sha256=sha(record['source']),generated_sha256=sha(dest))
        if 'edits' in record: receipts[name]['edits']=record['edits']
    (OUT/'ADAPTATIONS.json').write_text(json.dumps(receipts,indent=2)+'\n')
    spec=read(T21/'data/SPEC.json');order=read(P/'ORDER.json')
    spec['name']='gauge44-U10-t37-whole-owners';spec['call_order']=order
    spec['dispatch']=[[s,r,'gauge44']for s,r in order]
    spec['expected']={'gain_baseline_kappa':spec['expected']['gain_baseline_kappa']};spec['providers']={}
    spec['pivot_swap']['recipe']=str((T21/spec['pivot_swap']['recipe']).resolve())
    (runtime/'data').mkdir(exist_ok=True)
    (runtime/'data/SPEC.json').write_text(json.dumps(spec,indent=2)+'\n')
    print('PREPARED',OUT)
if __name__=='__main__':main()
