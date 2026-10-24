"""Source-bound bit execution, original consumer and independent stable oracle.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
All symbol decoding, key sorting and integer arithmetic below are observer-only.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok: raise ValueError(message)


def load(name, path):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(path.read_bytes(), str(path), 'exec'), m.__dict__)
    return m


def modules():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input': continue
        raw = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 drift')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'source Git blob drift')
    old = load('radix_predecessor_observer', ROOT/'research/crt-binary-key-port/verify.py')
    mod = old.modules()
    mod['old'] = old; mod['radix'] = load('radix_program', P/'radix.py')
    return mod


class SymbolTape:
    def __init__(self, symbols): self.cells = dict(enumerate(symbols)); self.head = 0
    def read(self): return self.cells.get(self.head, '_')
    def write(self, value): self.cells[self.head] = value
    def move(self, direction): self.head += direction


def symbols(rows): return ['<', *[x for value, key in rows for x in [('R', value), *key]], '>']


def canonical_cells(cells): return {k:v for k,v in cells.items() if v}


def bit_expected(old, stream): return canonical_cells(dict(enumerate(old.packet(stream))))


def run(mod, rows, *, audit=False, fault=None, repeated=1, malformed=None):
    old, b = mod['old'], mod['binary']
    source = mod['radix'].assemble(mod['query'], fault)
    program, starts, regs = b.compile_program(source, 'short_move' if fault == 'short_move' else 'keep_control' if fault == 'keep_control' else None, lifecycle=True)
    incoming = symbols(rows) if malformed is None else malformed
    tapes = {'bad':b.BitTape(old.packet(incoming)), 'b0':b.BitTape(old.packet(['<'])), 'b1':b.BitTape(old.packet(['<']))}
    originals = [SymbolTape(incoming), SymbolTape(['<']), SymbolTape(['<'])]
    want = list(rows); lengths = [len(key) for _,key in rows]
    d = sum(1+length for length in lengths)
    totals = Counter(); source_steps = backward = 0
    for invocation in range(repeated):
        machine = b.Machine(program, len(regs), tapes); machine.registers[:] = [1]*len(regs)
        before_steps, before_backward = source_steps, backward
        if audit:
            state = (0, {}, {role:dict(enumerate(incoming if role == 'bad' else ['<'])) for role in tapes}, dict.fromkeys(tapes,0))
            for _ in range(starts[0]): machine.step()
            while machine.status is None:
                pc = state[0]; op,*args = source[pc]
                need(machine.pc == starts[pc], 'relocated source control boundary')
                state = old.source_step(source, state)
                for _ in range(starts[pc+1]-starts[pc]): machine.step()
                source_steps += 1; backward += int(state[0] <= pc)
                if op != 'halt': need(machine.pc == starts[state[0]], 'source next PC')
                for role in tapes: need(tapes[role].head == 13*state[3][role], 'unit-move head scaling')
                if op in ('write', 'write_reg'):
                    role = args[0]; cell = state[3][role]
                    need(old.physical_word(tapes[role],cell) == old.encode(state[2][role][cell]), 'complete dirty word write')
                dest = args[1] if op in ('read','copy') else args[0] if op == 'set' else args[2] if op in ('eq','eq_reg') else None
                if dest is not None: need(old.observe_register(machine,regs,dest) == old.encode_value(state[1][dest]), 'independent register semantics')
        else:
            # A failed movement mutant may not terminate; the observer watchdog is not machine work.
            for _ in range(2_000_000):
                if machine.status is not None: break
                machine.step()
            need(machine.status is not None, 'observer watchdog; no accepted execution')
        need(not any(machine.registers), 'finite control is explicitly erased')
        need(all(t.head == 0 for t in tapes.values()), 'all heads returned')
        if malformed is not None:
            need(machine.status == 'reject', 'malformed framing rejected')
            need(tapes['bad'].cells == bit_expected(old,incoming), 'rejection preserves borrowed input')
            need(all(tapes[r].cells == bit_expected(old,['<']) for r in ('b0','b1')), 'rejection preserves empty buckets')
            return dict(status='reject', actions=sum(machine.census.values()))
        need(machine.status == 'accept', 'accept legal stream')
        # Independent mathematical oracle; stable sort is observer-only.
        want = [(v,k[-1]+k[:-1]) for v,k in sorted(want,key=lambda row:row[1][-1])]
        mod['bridge'].one_pass(*originals, frozenset())
        need(tapes['bad'].cells == bit_expected(old,symbols(want)), 'independent stable rotation endpoint')
        for role, tape in zip(('bad','b0','b1'), originals):
            expected = {i:v for i,v in enumerate(old.packet([tape.cells.get(j,'_') for j in range(max(tape.cells)+1)])) if v}
            need(tapes[role].cells == expected and tapes[role].head == 13*tape.head, 'literal original one_pass endpoint')
        need(all(tapes[r].cells == bit_expected(old,['<']) for r in ('b0','b1')), 'owned bucket contents erased')
        actions = sum(machine.census.values()); totals.update(machine.census)
        need(actions <= 43*len(source)*(8*len(rows)+12*sum(lengths)+10)+2*len(regs), 'proved full binary envelope')
        if audit:
            need(backward-before_backward == 4*sum(lengths)+8*d+9, 'exact proof backward-transfer count')
            need(source_steps-before_steps <= len(source)*(backward-before_backward+1), 'strictly increasing PC segments')
        incoming = symbols(want)
    if repeated and lengths and len(set(lengths)) == 1 and repeated == lengths[0]:
        need(want == sorted(rows,key=lambda row:row[1]), 'complete stable LSD sort, original key orientation')
    return dict(records=len(rows), key_cells=sum(lengths), passes=repeated, actions=sum(totals.values()), audited_source_steps=source_steps, audited_backward_edges=backward)


def actual_caller(mod):
    saved = mod['bridge'].one_pass; rows = []
    source = mod['radix'].assemble(mod['query'])
    program,_,regs = mod['binary'].compile_program(source,lifecycle=True)
    def invoke(bad,b0,b1,flags):
        need(not flags,'actual caller has ordinary flags')
        machine = mod['binary'].Machine(program,len(regs),{'bad':bad.raw,'b0':b0.raw,'b1':b1.raw})
        machine.registers[:] = [1]*len(regs); machine.run()
        need(machine.status == 'accept' and not any(machine.registers), 'same-tape actual binary consumer')
        need(all(t.raw.head == 0 for t in (bad,b0,b1)), 'actual consumer head return')
        need(all(t.raw.cells == bit_expected(mod['old'],['<']) for t in (b0,b1)), 'actual consumer bucket erasure')
        rows.append(dict(binary_actions=sum(machine.census.values()),same_physical_tapes=True))
    mod['bridge'].one_pass = invoke
    try: observed = mod['old'].caller_port(mod)
    finally: mod['bridge'].one_pass = saved
    need(len(rows) == 1, 'actual caller invokes new consumer')
    observed['consumer'] = 'new binary radix pass on same physical tapes of two completed captured pairs'
    observed['radix'] = rows[0]
    return observed


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
    mod=modules(); source=mod['radix'].assemble(mod['query'])
    program,starts,regs=mod['binary'].compile_program(source,lifecycle=True)
    need(max(starts[i+1]-starts[i] for i,x in enumerate(source) if x[0]!='halt')==43,'inherited compiler maximum')
    fixture=[(4095,'101'),(0,'000'),(18,'001'),(234,'001'),(3,'111'),(51,'010'),(1024,'100'),(5,'011')]
    examples=[run(mod,fixture,audit=True),run(mod,[(4095,'1')],audit=True),run(mod,[],audit=True),run(mod,fixture,repeated=3)]
    # All words up to four records for one-bit keys; all two-record keys through width four.
    cases=0
    for n in range(5):
        for keys in itertools.product(('0','1'),repeat=n):
            run(mod,[(4095-i,key) for i,key in enumerate(keys)]);cases+=1
    for width in range(1,5):
        keys=[format(i,f'0{width}b') for i in range(2**width)]
        for k0,k1 in itertools.product(keys,repeat=2):
            run(mod,[(0,k0),(4095,k1)]);cases+=1
    examples.extend([run(mod,[(21,'0'*37),(22,'1'*37)],repeated=37),run(mod,[(1,'1'),(2,'01010'),(3,'00')])])
    malformed=[['<',('R',0),'>'],['<','0','>'],['<',('R',0),'0','_','>'],['<',('R',0),'1',('R',1),'>'],['<','L','>'],['<',('R',0),'R','>'],['<',('R',0),'1','=','>'],['<','_','>']]
    rejects=[run(mod,[],malformed=row) for row in malformed]
    controls=[]
    for fault in ('reverse_buckets','wrong_rotation','keep_buckets','short_move','keep_control'):
        try:run(mod,fixture,fault=fault)
        except (ValueError,KeyError,IndexError):controls.append(fault)
        else:raise ValueError('missed behavioral fault '+fault)
    result=dict(status='PASS_LITERAL_BINARY_RADIX_CONSUMER',source_instructions=len(source),binary_instructions=len(program),bit_registers=len(regs),binary_envelope=f'43*{len(source)}*(8*n+12*K+10)+{2*len(regs)}',complete_bounded_cases=cases,examples=examples,rejections=rejects,behavior_controls=controls,actual_caller=actual_caller(mod),program_sha256=hashlib.sha256((P/'radix.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True),'frozen result drift')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
