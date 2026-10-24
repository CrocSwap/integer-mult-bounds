"""Exact literal program controls and actual source-geometry caller probe."""
from pathlib import Path
from hashlib import sha256
import json,tarfile,argparse,time,copy,subprocess,tempfile,sys
from unittest.mock import patch
from program import *
from machine import execute,validate
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,why):
    if not ok:raise ValueError(why)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def authenticate():
    spec=json.loads((HERE/'SOURCES.json').read_text())
    for row in spec['files']:
        if row['usage']=='input':need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source bytes')
    p=json.loads((HERE/'PREDECESSOR.json').read_text());archive=HERE/p['archive']
    need(sha256(archive.read_bytes()).hexdigest()==p['sha256'],'predecessor archive')
    with tarfile.open(archive) as t:
        for name,digest in p['members'].items():need(sha256(t.extractfile(name).read()).hexdigest()==digest,'predecessor member')
    return {'archive':p['sha256'],'source_files':len(spec['files'])}
def setup(h,a,g,s,bits=None):
    n=a*4**h*g*s
    if bits is None:bits=[((i*13)^(i//3)^(i//4096))&1 for i in range(n)]
    need(len(bits)==n,'fixture volume')
    tapes={r:bytearray([BLANK]) for r in ROLES};heads={r:0 for r in ROLES}
    tapes['SOURCE']=bytearray([LEFT]+bits)
    for r,v in zip(('H','A','G','S'),(h,a,g,s)):tapes[r]=bytearray([LEFT]+[int(x) for x in reversed(bin(v)[2:])]+[RIGHT])
    for r in BORROWED:heads[r]=1
    return tapes,heads,bits

def oracle(bits,h,a,g,s):
    out=[]
    for prefix in range(a):
        for y in range(2**h):
            for middle in range(g):
                for x in range(2**h):
                    at=((((prefix*2**h+x)*g+middle)*2**h+y)*s);out.extend(bits[at:at+s])
    return bytearray(out)
def empty(tapes,heads,closed=False):
    for r in PRIVATE:
        need(heads[r]==1,'private head')
        need(tapes[r][0]==(BLANK if closed else LEFT),'private marker')
        need(all(v==BLANK for v in tapes[r][1:]),'private body')
def fixture(h,a,g,s,bits=None,program=None,install=False,repeats=1):
    code,entries=assemble() if program is None else program
    factor=validate(code,entries);tapes,heads,bits=setup(h,a,g,s,bits)
    initial={r:bytes(tapes[r]) for r in BORROWED};expected=oracle(bits,h,a,g,s)
    total={k:0 for k in ('steps','reads','writes','moves')};events=[]
    def call(name):
        receipt=execute(code,tapes,heads,entries[name],max_steps=300000000)
        need(receipt['status']=={'init':'initialized','run':'returned','consume':'consumed','close':'closed','install':'installed'}[name],'literal status '+name)
        for k in total:total[k]+=receipt[k]
        events.append(receipt);return receipt
    call('init')
    for _ in range(repeats):
        call('run');need(tapes['OUTPUT'][1:1+len(bits)]==expected,'output permutation')
        need(all(v==BLANK for v in tapes['OUTPUT'][1+len(bits):]),'output tail')
        for r in BORROWED:need(bytes(tapes[r])==initial[r] and heads[r]==1,'borrowed bytes/head')
        need(heads['OUTPUT']==1,'output head')
        call('install' if install else 'consume')
        if install:
            need(tapes['SOURCE'][1:1+len(bits)]==expected and heads['SOURCE']==1,'caller install')
            for r in BORROWED[1:]:need(bytes(tapes[r])==initial[r] and heads[r]==1,'caller descriptors')
        empty(tapes,heads)
    call('close');empty(tapes,heads,True)
    need(total['steps']<=factor*(total['reads']+total['writes']+total['moves']+len(events)),'CFG invoice')
    L=h+sum(max(1,v.bit_length()) for v in (h,a,g,s))+8
    bound=2**20*(h+1)*(len(bits)+1)*(L+1)**2
    need(total['steps']<=repeats*bound,'whole price')
    return {'geometry':[h,a,g,s],'bits':len(bits),'private_roles':len(PRIVATE),'program_length':len(code),'control_factor':factor,'calls':repeats,'install':install,'actions':total,'bound_per_session':bound,'output_sha256':sha256(expected).hexdigest()}

def rejected(thunk):
    try:thunk()
    except (ValueError,FileNotFoundError,KeyError,IndexError):return
    raise ValueError('control accepted')
def controls():
    receipts=[]
    for h in range(6):receipts.append(fixture(h,1,1,1))
    for h,a,g,s in [(0,2,3,2),(1,2,3,2),(2,2,2,3),(3,1,2,1)]:receipts.append(fixture(h,a,g,s))
    for i in range(24):
        bits=[0]*24;bits[i]=1;fixture(1,1,2,3,bits)
    fixture(2,1,2,3,repeats=3)
    code,entries=assemble()
    # Mutate an actual queue read, leaving the rest of the program unchanged.
    changed=list(code)
    pos=next(i for i,row in enumerate(changed) if row[0]=='test' and row[1]=='Q01' and row[2]==ZERO)
    row=list(changed[pos]);row[1]='Q10';changed[pos]=tuple(row)
    rejected(lambda:fixture(1,1,2,3,[0]*3+[1]+[0]*20,(tuple(changed),entries)))
    # Missing phase update violates the full digit input extent.
    old=Builder.double
    def omit(self,role):
        if role!='PRE':old(self,role)
    with patch.object(Builder,'double',omit):bad=assemble()
    rejected(lambda:fixture(2,1,2,3,program=bad))
    old_clear=Builder.clear
    def no_erase(self,role):
        if role!='B0':old_clear(self,role)
    with patch.object(Builder,'clear',no_erase):bad=assemble()
    rejected(lambda:fixture(1,1,2,3,program=bad))
    rejected(lambda:validate((('call',lambda:None),),{'run':0}))
    rejected(lambda:validate((('jump',0),),{'run':0}))
    rejected(lambda:validate((('jump',True),),{'run':0}))
    x={'n':1}
    for v in (True,1.0):need(canonical(x)!=canonical({'n':v}),'typed receipt')
    real=Path.read_bytes
    archive=HERE/'inputs/pr5162.tar.gz'
    def corrupt(p):return b'changed' if p==archive else real(p)
    with patch.object(Path,'read_bytes',corrupt):rejected(authenticate)
    # Real cold process entry failures, before any full scientific work.
    with tempfile.TemporaryDirectory() as tmp:
        target=Path(tmp)/'research'/'literal';target.mkdir(parents=True)
        for name in ('verify.py','program.py','machine.py'):
            (target/name).write_bytes((HERE/name).read_bytes())
        for missing in ('RESULT.json','SOURCES.json'):
            if missing=='SOURCES.json':(target/'RESULT.json').write_text('{}')
            result=subprocess.run([sys.executable,'-B',str(target/'verify.py')],capture_output=True,text=True,timeout=5)
            need(result.returncode!=0 and missing in result.stderr,'missing-file process rejection')
    return {'fixtures':receipts,'independent_columns':24,'repeated_calls':3,'rejections':['wrong_queue_read','missing_prefix_update','missing_owned_erase','host_callback_opcode','zero_cell_cycle','bool_pc','boolean_receipt','float_receipt','source_corruption','missing_RESULT_process','missing_SOURCES_process']}

def run():
    auth=authenticate();light=controls();actual=fixture(2,1,1024,12,install=True)
    return {'status':'PASS_LITERAL_ELEMENTARY_INTERCHANGE','sources':auth,'program_sha256':sha256(canonical(assemble()).encode()).hexdigest(),'code_sha256':{n:sha256((HERE/n).read_bytes()).hexdigest() for n in ('program.py','machine.py')},'controls':light,'actual':actual}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-result',action='store_true');args=p.parse_args()
    # Require the frozen result before scientific work outside authoring mode.
    expected=None if args.write_result else json.loads((HERE/'RESULT.json').read_text())
    start=time.monotonic();result=run()
    if args.write_result:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(canonical(result)==canonical(expected),'complete typed receipt')
    print(json.dumps({'status':result['status'],'seconds':time.monotonic()-start,'actual':result['actual']},indent=2))
