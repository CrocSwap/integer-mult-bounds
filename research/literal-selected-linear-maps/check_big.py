"""Complete actual f=2 matrices on a dense interpreter of the emitted graph.

The C4 test interpreter is retained with its fixed inventory changed 29->27
and a larger external watchdog. This is author cross-interpreter evidence,
not root's independently implemented review.
"""
from pathlib import Path
import hashlib
import json
import random
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check as c


def table_text(code):
    symbols = {'_':0,'0':1,'1':2,'|':3}
    rows = [str(len(code))]
    for op,*a in code:
        tape = value = 0
        branches = [-1]*4
        if op == 'read':
            tag,tape = 0,a[0]
            for s,pc in a[1].items():branches[symbols[s]]=pc
        elif op == 'write':tag,tape,value=1,a[0],symbols[a[1]]
        elif op == 'move':tag,tape,value=2,a[0],a[1]
        elif op == 'goto':tag,value=3,a[0]
        elif op == 'halt':tag=4
        else:raise ValueError('unrecognized literal instruction')
        rows.append(' '.join(map(str,(tag,tape,value,*branches))))
    return '\n'.join(rows)+'\n'


def invoke(tmp, executable, shape, payload, code):
    program,packet,output=(tmp/n for n in ('program.txt','packet.txt','output.txt'))
    program.write_text(table_text(code))
    origins=[64+2*i for i in range(27)]
    packet.write_text(' '.join(map(str,origins))+'\n'+' '.join(map(str,c.caps(shape)))+'\n'+c.header(shape)+'\n'+payload+'\n')
    start=time.monotonic()
    run=subprocess.run([str(executable),str(program),str(packet),str(output)],capture_output=True,text=True,check=True,timeout=180)
    result=json.loads(run.stdout); out=output.read_text()
    c.require(result['accepted'],'dense literal rejection')
    c.require(all(result[x] for x in ('heads_returned','private_blank','header_preserved','exteriors_preserved')),'dense lifecycle boundary')
    c.require(result['data_writes']==len(payload) and result['header_writes']==0,'dense public write census')
    c.require(result['steps'] <= 65536*(shape[0]*len(payload)+len(c.header(shape))+1),'dense time envelope')
    c.require(result['private_history'] <= 64*(len(payload)+len(c.header(shape))+1),'dense history envelope')
    result.update({'shape':list(shape),'input_bits':len(payload),'output_sha256':hashlib.sha256(out.encode()).hexdigest()})
    return out,result,time.monotonic()-start


def capture(side):
    old=c.m.Builder; builder=old();c.m.Builder=lambda:builder
    try:code,alphabet=c.m.compile_linear(side)
    finally:c.m.Builder=old
    return code,alphabet,builder.labels


def main():
    rng=random.Random(2026111205)
    small_shape=(1,1,1,1,1);big_shape=(2,1,1,1,1)
    small=''.join(str(rng.randrange(2)) for _ in range(c.extent(small_shape)))
    big=''.join(str(rng.randrange(2)) for _ in range(c.extent(big_shape)))
    records={}; controls=[]; timings={}
    with tempfile.TemporaryDirectory(prefix='literal-linear-full-') as folder:
        tmp=Path(folder);exe=tmp/'table_cpu'
        subprocess.run(['c++','-std=c++17','-O2',str(HERE/'table_cpu.cpp'),'-o',str(exe)],check=True,capture_output=True,text=True,timeout=60)
        for side in ('right','left'):
            code,alphabet,labels=capture(side)
            out,receipt,elapsed=invoke(tmp,exe,small_shape,small,code)
            c.require(out==c.oracle(small,small_shape,c.m.MATRICES[side]),'dense f1 direct matrix')
            c.require(receipt['steps']==c.execute(side,small_shape,small,code=code),'two literal interpreters count differently')
            records[side+'_f1']=receipt;timings[side+'_f1']=elapsed
            expected=c.oracle(big,big_shape,c.m.MATRICES[side])
            out,receipt,elapsed=invoke(tmp,exe,big_shape,big,code)
            c.require(out==expected,'actual complete f2 direct matrix')
            records[side+'_f2']=receipt;timings[side+'_f2']=elapsed
            print('completed actual '+side+' f2',file=sys.stderr,flush=True)
            if side=='right':
                broken=list(code)
                for label,pc in labels.items():
                    if label.endswith('next_column'):
                        broken[pc]=('goto',labels[label[:-len('next_column')]+'finished'])
                wrong,receipt,elapsed=invoke(tmp,exe,big_shape,big,tuple(broken))
                c.require(wrong!=expected,'first-column-only mutant escaped')
                records['first_column_only']=receipt;timings['first_column_only']=elapsed
                controls.append('all gates retain only the first column; complete lifecycle still succeeds')
                wrong_commit=tuple(('write',c.m.DATA,'0') if i==('write',c.m.DATA,'1') else i for i in code)
                wrong,receipt,elapsed=invoke(tmp,exe,small_shape,small,wrong_commit)
                c.require(wrong!=c.oracle(small,small_shape,c.m.MATRICES[side]),'commit mutant escaped')
                records['commit_bits']=receipt;timings['commit_bits']=elapsed
                controls.append('change one-bits in the final public commit')
        old=c.m.cnot_columns
        c.m.cnot_columns=lambda a,target,control:old(a,control,target)
        try:wrong_direction=c.m.compile_linear('right')[0]
        finally:c.m.cnot_columns=old
        wrong,receipt,elapsed=invoke(tmp,exe,small_shape,small,wrong_direction)
        c.require(wrong!=c.oracle(small,small_shape,c.m.MATRICES['right']),'reversed CNOT-direction mutant escaped')
        records['wrong_control_direction']=receipt;timings['wrong_control_direction']=elapsed
        controls.append('reverse control and target at every compiled gate')
    print(json.dumps({'status':'PASS_ACTUAL_BOTH_SELECTED_LINEAR_F2','source_sha256':hashlib.sha256((HERE/'linear.py').read_bytes()).hexdigest(),
        'interpreter_sha256':hashlib.sha256((HERE/'table_cpu.cpp').read_bytes()).hexdigest(),'compiler_flags':['-std=c++17','-O2'],
        'seed':2026111205,'records':records,'controls':controls,'scope':'Both actual fixed m=9 maps, complete 262144-address f=2 fields; no reduced dimension or address sampling.'},indent=2,sort_keys=True))
    print('Elapsed seconds (observations only): '+json.dumps({k:round(v,3) for k,v in timings.items()},sort_keys=True),file=sys.stderr)


if __name__=='__main__':main()
