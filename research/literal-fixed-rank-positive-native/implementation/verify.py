"""Source-bound literal uniform-rank Gamma6/HOME numerical replay."""
from pathlib import Path
import atexit
from hashlib import sha256
import importlib.util
import json
import random
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
_cache = tempfile.TemporaryDirectory(prefix='positive-verify-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode = True
sys.pycache_prefix = str(Path(_cache.name) / 'required-absent')
import adapter as A
import join as C
from machine import Program, initial, fields, check_retired, Rejected


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    if n < 1:
        raise ValueError('positive Gamma integer')
    b = bin(n)[2:]
    return '0'*(len(b)-1)+b


def header(shape):
    return ''.join(gamma(n) for n in shape)


def encode(values, width):
    if any(not -(1 << (width-1)) <= x < 1 << (width-1) for z in values for x in z):
        raise ValueError('oracle signed width')
    return ''.join(format(x % (1 << width), '0'+str(width)+'b') for z in values for x in z)


def direct(values, rank, *, f=1, omit_last=False):
    """Independent natural-address C butterflies on the complete array.

    This oracle indexes every actual active slot bit directly, without
    conjugating the first-slot helper or simulating CNOT swaps.
    """
    out = list(values)
    count = rank-1 if omit_last else rank
    for slot in range(count):
        for column in range(f):
            mask = 1 << (9*f-1-(slot*f+column))
            for i in range(len(out)):
                if i & mask:
                    continue
                ar, ai = out[i]; br, bi = out[i | mask]
                rows = (ar-ai+br+bi, ar+ai-br+bi,
                        ar+ai+br-bi, -ar+ai+br+bi)
                need(all(x % 2 == 0 for x in rows), 'independent oracle parity')
                out[i], out[i | mask] = (rows[0]//2,rows[1]//2),(rows[2]//2,rows[3]//2)
    return out


def guard_checks():
    from controller_reference import Machine, Tape
    records = []
    for rank in range(1,10):
        code, _ = C.compile_guard(rank)
        cases = [(f, rank*f+delta) for f in (1,2,3,5,16,65,129)
                 for delta in (-1,0,1) if rank*f+delta > 0]
        cases += [(5, 1 << bits) for bits in (63,257,512,1024,4096)]
        for f, cutoff in cases:
            text = header((f,2,3,2,5,cutoff))
            origins = [11*t-139 for t in range(29)]
            tapes = [Tape({o-5:'0',o+1000000:'1'},o) for o in origins]
            tapes[0].cells.update({origins[0]+i:b for i,b in enumerate(text)})
            before = [t.cells.copy() for t in tapes]
            machine = Machine(code,tapes)
            try:
                machine.run(5000000); accepted = True
            except ValueError as exc:
                need(str(exc) == 'invalid scanned symbol', 'unexpected guard rejection')
                accepted = False
            need(accepted == (rank*f <= cutoff), 'literal rank-times-f cutoff')
            need(tapes[0].cells == before[0], 'guard changed header')
            if accepted:
                need([t.head for t in tapes] == origins and [t.cells for t in tapes] == before,
                     'guard private/head retirement')
            records.append({'rank':rank,'f':f,'cutoff_bits':cutoff.bit_length(),
                            'accepted':accepted,'steps':machine.steps})
    weak, _ = C.compile_guard(3,weak=True)
    ts = [Tape({},0) for _ in range(29)]
    ts[0] = Tape(dict(enumerate(header((1,1,1,1,8,2)))),0)
    Machine(weak,ts).run()
    return records


def tables():
    result=[]
    for rank in range(1,10):
        code, alphabet, entries = C.compile_join(rank)
        need(alphabet == ('_','0','1','|'), 'core alphabet')
        need(not any(op == 'write' and args[0] == C.DATA
                     for op,*args in code[:entries['commit']]), 'early public core write')
        for op,*args in code:
            if op in ('read','write','move'):
                need(0 <= args[0] < C.TAPES, 'fixed port bound')
            if op == 'read':
                need(all(0 <= p < len(code) for p in args[1].values()), 'fixed read target')
            if op == 'goto':
                need(0 <= args[0] < len(code), 'fixed jump target')
            if op == 'move':
                need(args[1] in (-1,1), 'unit core move')
        result.append({'rank':rank,'locations':len(code),'commit':entries['commit'],
                       'sha256':sha256(repr(code).encode()).hexdigest()})
    return result


def corruption_control():
    with tempfile.TemporaryDirectory(prefix='positive-source-control-') as tmp:
        dst = Path(tmp)
        for name in ('join.py','SOURCES.json'):
            shutil.copy2(HERE/name,dst/name)
        for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
            q=dst/pin['local'];q.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(HERE/pin['local'],q)
        q=dst/'reference/rank2/reference/leaf/leaf.py'
        q.write_bytes(q.read_bytes()+b'\n# changed actual helper byte\n')
        launch=('import sys,tempfile;from pathlib import Path;'
                'd=tempfile.TemporaryDirectory();sys.dont_write_bytecode=True;'
                'sys.pycache_prefix=str(Path(d.name)/"absent");'
                'sys.path.insert(0,'+repr(str(dst))+');import join')
        r=subprocess.run([sys.executable,'-I','-B','-c',launch],capture_output=True,text=True)
        need(r.returncode != 0 and 'frozen source drift' in r.stderr, 'actual helper drift accepted')


def run():
    guard_records = guard_checks()
    table_records = tables()
    graph, stages = A.compile_home(3)
    program = Program(graph)
    rng = random.Random(130003)
    shape = (1,1,1,1,8,3)
    values = [(8*rng.randrange(-1,2),8*rng.randrange(-1,2)) for _ in range(512)]
    h = header(shape); data = encode(values,8); bits = h+data
    answer = direct(values,3)
    expected = h+encode(answer,8)
    need(expected != bits and direct(values,2) != answer, 'nontrivial rank-three tensor oracle')
    parked = ''.join(str(rng.randrange(2)) for _ in bits)
    state = initial((parked,bits),A.TAPES,old_history=3*len(bits))
    old_highs = state.highs.copy()
    program.run(state,stop=stages['core_return'])
    need(fields(state) == (parked,bits) and state.writes[0] == 0, 'early HOME write before core return')
    core_steps = state.steps
    program.run(state,start=stages['core_return'],stop=stages['primitive_return'])
    need(fields(state) == (parked,bits) and state.writes[0] == 0, 'early HOME write before scatter')
    program.run(state,start=stages['primitive_return'])
    need(fields(state) == (parked,expected), 'complete literal rank-three output')
    need(state.writes[0] == len(bits), 'sole complete owned HOME commit')
    check_retired(state)
    need(all(x >= y for x,y in zip(state.highs,old_highs)), 'old history refunded')
    increment = sum((hi-lo)-(ehi-elo) for lo,hi,elo,ehi in
                    zip(state.lows,state.highs,state.entry_lows,state.entry_highs))
    need(increment <= 2112*(len(bits)+1), 'complete historical-backing increment')
    need(state.steps <= (1 << 24)*(len(data)+len(h)+1)+128*(len(bits)+1), 'complete time bound')
    first = {'shape':shape,'E':len(h),'V':len(data),'F':len(bits),'steps':state.steps,
             'core_return_steps':core_steps,'HOME_writes':state.writes[0],
             'visited_increment':increment,'retained_old_guide_high':state.highs[-1],
             'output_sha256':sha256(expected.encode()).hexdigest()}
    # Legal packet, wrong joint cutoff: f<=2 but 3*f>2. Public HOME unchanged.
    bad = header((1,1,1,1,8,2))+data
    rejected = initial(('0'*len(bad),bad),A.TAPES)
    before = bytes(rejected.tapes[0])
    try:
        program.run(rejected)
    except Rejected:
        pass
    else:
        raise ValueError('rank-three joint cutoff accepted')
    need(rejected.writes[0] == 0 and bytes(rejected.tapes[0]) == before, 'cutoff changed public HOME')
    # Actually execute omitted-third-C mutant; same ABI returns a different tensor.
    wrong_graph,_ = A.compile_home(3,mutation='omit_last_C')
    wrong = initial((parked,bits),A.TAPES)
    Program(wrong_graph).run(wrong)
    need(fields(wrong) == (parked,h+encode(direct(values,2),8)) and fields(wrong)[1] != expected,
         'omitted third active slot control')
    check_retired(wrong)
    corruption_control()
    return {'marker':'PASS_LITERAL_GENERIC_POSITIVE_HOME','tapes':A.TAPES,'core_tapes':C.TAPES,
            'rank_three':first,'tables':table_records,'guard_cases':guard_records,
            'cutoff_rejection_steps':rejected.steps,'omitted_child_steps':wrong.steps,
            'controls':['joint cutoff versus weak f cutoff','actual omitted third C',
                        'actual retained source corruption','no early original-owner write'],
            'scope':'fixed-rank positive central direct leaf only; no surrounding monomials/caller/nonleaf rate'}


if __name__ == '__main__':
    start = time.monotonic()
    result = run()
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    elif (HERE/'RESULT.json').exists():
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(json.dumps(result)), 'receipt changed')
    print(json.dumps(result,sort_keys=True))
    print('elapsed_seconds',round(time.monotonic()-start,3))
