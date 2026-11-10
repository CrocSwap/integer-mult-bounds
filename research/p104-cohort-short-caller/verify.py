"""Fresh source-bound native/caller composition and complete chart catalogue.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,shutil,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inputs import HERE,sources,read,need
from adapt import adapt
need(__debug__,'Run without optimized Python')
COMMANDS=('emit_odd_type_b.py','emit_odd_type_ab.py','check_odd_caller_exact_grid.py',
          'check_odd_physical_binding.py','check_odd_precision.py','check_odd_partial_admission.py',
          'check_odd_fixed_tape_counts.py')

def run():
    with sources() as (source,root):
        working=root/'working';shutil.copytree(source[7113]/'replay',working)
        folder=working/'supplier7112/short-caller'
        for name in ('WORD.json.gz','RESULT.json'):(folder.parent/name).write_bytes((source[7115]/name).read_bytes())
        for path in folder.glob('SHORT-CATALOGUE-*-*.log'):path.unlink()
        adapter=adapt(folder)
        subprocess.run([sys.executable,'-I','-B',str(HERE/'price.py'),str(source[7115]),str(source[7113]),str(folder)],check=True)
        for name in COMMANDS:
            print('RUN',name,flush=True)
            subprocess.run([sys.executable,'-B',str(folder/name)],cwd=folder,check=True)
        need((folder/'ODD-TYPE-AB-CALLER.json').read_bytes()==(source[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes(),'Whole reconstructed literal caller unchanged')
        price=read(folder/'CURRENT-PRICE.json');partial=read(folder/'ODD-ADMISSION-PARTIAL.json')
        need(price['after']==partial['invoice'],'Complete invoice from two adapters')
        need(price['gate']==partial['compiler_outer'],'Both complete directed compiler gates')
        catalogue=[]
        for start,stop in ((0,1000),(1000,2000),(2000,3047)):
            print('RUN complete catalogue',start,stop,flush=True)
            path=folder/f'SHORT-CATALOGUE-{start}-{stop}.log'
            with path.open('x') as out:subprocess.run([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--start',str(start),'--stop',str(stop)],cwd=folder,stdout=out,check=True)
            text=path.read_text();catalogue.append(json.loads(text[text.index('\n{'):]))
        subprocess.run([sys.executable,'-B',str(folder/'assemble_odd_application.py')],cwd=folder,check=True)
        files=('ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
               'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json','ODD-8X9-APPLICATION-CHECKS.json')
        result=dict(status='PASS_P104_COHORT_SHORT_CALLER',claim=price['gate']['claim'],price=price,
                    caller_sha256=sha256((folder/'ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest(),
                    adapter=adapter,catalogue=catalogue,checks={name:read(folder/name) for name in files})
        return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();result=run()
    if a.out:
        with a.out.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    else:need(result==read(HERE/'RESULT.json'),'Every frozen composition receipt field')
    print(result['status'],result['claim'],flush=True)
if __name__=='__main__':main()
