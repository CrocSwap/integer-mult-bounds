"""Integration controls for the reusable source-format separator. Apache-2.0."""
import copy,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok: raise ValueError(msg)
def invoke(path,*args,success=True):
    r=subprocess.run([sys.executable,'-I','-O','-B',str(path),*map(str,args)],capture_output=True,text=True)
    need((r.returncode==0)==success,'unexpected process result: '+r.stdout[-400:]+r.stderr[-800:])
    return r
def digest(tree):
    return {p.relative_to(tree).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in tree.rglob('*') if p.is_file()}
def main():
    with tempfile.TemporaryDirectory(prefix='t16-cuts-') as name:
        root=Path(name);pkg=root/'research'/HERE.name;shutil.copytree(HERE,pkg)
        manifest=json.loads((HERE/'SOURCES.json').read_text())
        for row in manifest['files']:
            if row.get('usage')=='input':
                dest=root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],dest)
        before=digest(root);invoke(pkg/'verify.py');need(digest(root)==before,'default verification rewrites files')
        source=pkg/'inputs/pr2169/search/glob.py';raw=source.read_bytes();source.write_bytes(raw+b'\n# corruption\n')
        invoke(pkg/'verify.py',success=False);source.write_bytes(raw)
        receipt=pkg/'RESULT.json';raw=receipt.read_bytes();d=json.loads(raw);d['strictness']['source_hall_and_gr']=1
        receipt.write_text(json.dumps(d),encoding='utf-8');invoke(pkg/'verify.py',success=False);receipt.write_bytes(raw)
        spec=importlib.util.spec_from_file_location('v',pkg/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
        classes,bins=v.geometry();ps,fs=v.aggregate(v.read(root/v.SELECTED),classes,bins)
        data=v.export_stage1(ps,fs);data.update(changed=[],bound=123.5)
        candidate=root/'candidate.json';candidate.write_text(json.dumps(data),encoding='utf-8');out=root/'cuts.json'
        invoke(pkg/'verify.py','--stage1',candidate,'--output',out)
        need(json.loads(out.read_text())['cuts']==[],'concrete map CLI positive')
        saved=out.read_bytes();invoke(pkg/'verify.py','--stage1',candidate,'--output',out,success=False)
        need(out.read_bytes()==saved,'exclusive output modified existing result')
        # Embed the new impossible local fixture while leaving all other classes valid.
        bad=copy.deepcopy(data);bad['x']=[r for r in bad['x'] if r[0]!=9]
        bad['x'] += [[9,[2,0,0,1,0],1],[9,[0,0,0,1,0],1],[9,[0]*5,222]]
        bad['y']=[r for r in bad['y'] if r[0]!=9]+[[9,t,w,1] for t in [0,1] for w in [4,8]]
        candidate.write_text(json.dumps(bad),encoding='utf-8');badout=root/'bad-cuts.json'
        invoke(pkg/'verify.py','--stage1',candidate,'--output',badout)
        need(any(c['class']==9 and c['widths']==[4,8] and c['calls']==[0,1] and c['deficit']==1 for c in json.loads(badout.read_text())['cuts']),'CLI lost actual witness')
        for label,mutate in [('bool',lambda d:d['x'][0].__setitem__(2,True)),
                              ('duplicate',lambda d:d['y'].append(d['y'][0])),
                              ('unbalanced',lambda d:d['y'][0].__setitem__(3,d['y'][0][3]+1))]:
            broken=copy.deepcopy(data);mutate(broken);candidate.write_text(json.dumps(broken),encoding='utf-8')
            target=root/(label+'.json');invoke(pkg/'verify.py','--stage1',candidate,'--output',target,success=False)
            need(not target.exists(),'invalid input produced result')
        receipt.unlink();invoke(pkg/'verify.py','--write-result');need(receipt.read_bytes()==raw,'regeneration mismatch')
        invoke(pkg/'verify.py','--write-result',success=False)
    print('PASS_T16_CUT_INTEGRITY optimized_git_free source_receipt_rejections source_schema_cli strict_witness parser_controls exclusive_outputs exact_regeneration')
if __name__=='__main__':main()
