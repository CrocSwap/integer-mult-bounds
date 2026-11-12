"""Execute the actual m=9 table at f=2 with a separate dense C++ interpreter.

The fixture and exact tensor oracle are outside the executing controller.
No reduced native dimension is substituted for the claimed table.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check as c


def table_text(code):
    numbers = {'_':0, '0':1, '1':2, '|':3}
    rows = [str(len(code))]
    for op, *a in code:
        tape = value = 0
        targets = [-1]*4
        if op == 'read':
            tag, tape = 0, a[0]
            for symbol, target in a[1].items():
                targets[numbers[symbol]] = target
        elif op == 'write':
            tag, tape, value = 1, a[0], numbers[a[1]]
        elif op == 'move':
            tag, tape, value = 2, a[0], a[1]
        elif op == 'goto':
            tag, value = 3, a[0]
        elif op == 'halt':
            tag = 4
        else:
            raise ValueError('unknown instruction')
        rows.append(' '.join(map(str, (tag, tape, value, *targets))))
    return '\n'.join(rows)+'\n'


def invoke(tmp, executable, shape, values, code=c.CODE, accept=True):
    word = c.encode(values, shape[4])
    program, packet, output = (tmp/n for n in ('program.txt','packet.txt','output.txt'))
    program.write_text(table_text(code))
    origins = [64+2*i for i in range(29)]
    packet.write_text(' '.join(map(str, origins))+'\n'+
                      ' '.join(map(str, c.caps(*shape)))+'\n'+c.header(*shape)+'\n'+word+'\n')
    started = time.monotonic()
    result = subprocess.run([str(executable),str(program),str(packet),str(output)],
                             check=True,timeout=120,capture_output=True,text=True)
    record = json.loads(result.stdout)
    result_word = output.read_text()
    c.require(record['accepted'] == accept, 'dense acceptance boundary')
    for field in ('header_preserved','exteriors_preserved'):
        c.require(record[field], 'dense CPU '+field)
    if accept:
        c.require(record['heads_returned'] and record['private_blank'], 'dense normal retirement')
        c.require(record['data_writes']==len(word), 'dense complete public commit')
    else:
        c.require(record['data_writes']==0 and result_word==word, 'dense rejection changed DATA')
    c.require(record['header_writes']==0, 'dense public header writes')
    f = shape[0]
    e = len(c.header(*shape))
    c.require(record['steps'] <= 65536*(f*len(word)+e+1), 'dense complete cost envelope')
    c.require(record['private_history'] <= 27+64*(len(word)+e+1), 'dense private history envelope')
    record['shape'] = list(shape)
    record['input_bits'] = len(word)
    record['output_sha256'] = hashlib.sha256(result_word.encode()).hexdigest()
    # Wall times are metadata, not counted machine work or a complexity claim.
    elapsed = time.monotonic()-started
    return result_word, record, elapsed


def main():
    c.authenticate()
    with tempfile.TemporaryDirectory(prefix='literal-C-full-') as directory:
        tmp = Path(directory)
        executable = tmp/'table_cpu'
        subprocess.run(['c++','-std=c++17','-O2',str(HERE/'table_cpu.cpp'),'-o',str(executable)],
                       check=True,timeout=60,capture_output=True,text=True)
        small_shape = (1,1,1,1,3,1)
        small_values = [(3,3)]*512
        small, small_record, small_time = invoke(tmp,executable,small_shape,small_values)
        c.require(small == c.oracle(small_values,*small_shape[:5]), 'dense f1 exact oracle')
        python_steps = c.run_case(small_shape,small_values)
        c.require(small_record['steps']==python_steps, 'two interpreters disagree on literal count')
        shape = (2,1,1,1,5,2)
        values = [(4*((17*i+(i>>8))%3-1), 4*((7*i+(i>>16))%3-1))
                  for i in range(1 << 18)]
        expected = c.oracle(values,*shape[:5])
        result, full, full_time = invoke(tmp,executable,shape,values)
        c.require(result==expected, 'actual full m9 f2 tensor differs')
        # This semantically complete mutant retains owner/cleanup behavior but
        # implements only the first axis, exposing rank-one/f=1 conflation.
        builder = c.m.Builder()
        old = c.m.Builder
        c.m.Builder = lambda: builder
        try:
            code, alphabet = c.m.compile_leaf()
        finally:
            c.m.Builder = old
        c.require(code==c.CODE and alphabet==c.ALPHABET, 'label-capture graph drift')
        broken = list(code)
        broken[builder.labels['next_axis']] = ('goto',builder.labels['finish'])
        wrong, mutant, mutant_time = invoke(tmp,executable,shape,values,tuple(broken))
        c.require(wrong != expected, 'skipped tensor-axis mutant survived')
        endpoint_values = [(1 if i >> 16 in (0,3) else 0,0) for i in range(1 << 18)]
        endpoint_shape = (2,1,1,1,2,2)
        endpoint_expected = c.oracle(endpoint_values,*endpoint_shape[:5])
        c.require(endpoint_expected == c.encode([(1 if i >> 16 in (1,2) else 0,0)
                                                for i in range(1 << 18)],2),
                  'endpoint-only admission witness formula')
        _, endpoint, endpoint_time = invoke(tmp,executable,endpoint_shape,endpoint_values,accept=False)
        print(json.dumps({'status':'PASS_ACTUAL_M9_F2_LITERAL_C','program_sha256':
              hashlib.sha256((HERE/'leaf.py').read_bytes()).hexdigest(),
              'table_sha256':hashlib.sha256(json.dumps([c.CODE,c.ALPHABET],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
              'interpreter_sha256':hashlib.sha256((HERE/'table_cpu.cpp').read_bytes()).hexdigest(),
              'compiler_flags':['-std=c++17','-O2'],'f1_cross_interpreter':small_record,
              'actual_f2':full,'f2_one_axis_mutant':mutant,'f2_endpoint_only_reject':endpoint,
              'controls':['skip every axis after the first while preserving data length, owner, heads and private retirement'],
              'scope':'Actual fixed m=9 table, complete 262144-address f=2 array; no reduced dimension or record subsampling.'},
              indent=2,sort_keys=True))
        print('Wall seconds f1/full-f2/mutant/endpoint-reject:',
              *[round(t,3) for t in (small_time,full_time,mutant_time,endpoint_time)],file=sys.stderr)


if __name__ == '__main__':
    main()
