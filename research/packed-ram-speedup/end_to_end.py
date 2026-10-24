"""One fixed 144-state TM, composed packed-codec/tabulator multiplication fixture.
Apache-2.0. Dugongue with substantial OpenAI Codex assistance.
Only the 16-case finite machine constructor and reference oracle use Python MUL.
The runtime target uses no MUL/DIV. This is NOT an all-length multiplier.
"""
from pathlib import Path
import types
import hashlib
import json
from collections import defaultdict


def load(path,name):
    pins=json.loads((Path(__file__).resolve().parent/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pins[path.name]:raise ValueError('Dependency source drift: '+path.name)
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def machine():
    delta={};halt=143
    # Prefix trie states 0,...,14 read exactly four MSB symbols.
    for depth in range(4):
        for prefix in range(1<<depth):
            q=(1<<depth)-1+prefix
            for bit in (0,1):
                word=(prefix<<1)|bit
                nxt=(1<<(depth+1))-1+word if depth<3 else 15+(word<<3)
                delta[q,(1+bit,)]=(nxt,(1+bit,),(1,))
    for word in range(16):
        base=15+(word<<3)
        left,right=word>>2,word&3
        product=left*right  # compile-time finite truth table, not runtime arithmetic.
        for j in range(4):
            for symbol in range(3):
                delta[base+j,(symbol,)]=(base+j+1,(symbol,),(-1,))
        for j in range(4):
            bit=(product>>(3-j))&1
            nxt=halt if j==3 else base+4+j+1
            for symbol in range(3):
                delta[base+4+j,(symbol,)]=(nxt,(1+bit,),(1,))
    return delta

def check():
    here=Path(__file__).resolve().parent
    codec_path=here/'packed_codec.py'
    tab_path=here/'tabulated_tm.py'
    codec_module=load(codec_path,'fixture_codec');tab=load(tab_path,'fixture_tabulator')
    codec=codec_module.Codec(1,2,64)
    sim=tab.Tabulator(1,3,144,machine(),1,64)
    tables=sim.rows;setup=sim.setup_ops+codec.setup_ops
    fixtures=macros=transitions=runtime=0
    for left in range(4):
        for right in range(4):
            # A fresh input/run preserves the already generated immutable table.
            sim.v.mem=defaultdict(int,{a:v for a,v in sim.v.mem.items() if a<sim.database})
            origin=4096+fixtures;heads=[origin];q=0;elapsed_total=0
            inp=(left<<2)|right
            digits=[(inp>>j)&1 for j in range(4)]
            before=sim.v.ops+codec.ops
            coded=codec.input_to_tm(digits,4,'msb')
            # General contiguous-chunk insertion, preserving all neighboring cells.
            mask=sim.v.sub(sim.v.shl(1,sim.r<<sim.flog),1)
            for j,value in enumerate(coded):
                pos=sim.v.add(origin,j<<codec.rlog)
                old=sim.get_window(0,pos)
                merged=sim.v.bor(sim.v.band(old,sim.v.bnot(mask)),value)
                sim.put_window(0,pos,merged)
            for _ in range(32):
                q,heads,halt,elapsed,_=sim.macro(q,heads)
                elapsed_total+=elapsed;macros+=1
                if halt:break
            else:raise ValueError('fixture failed to halt')
            if q!=143 or elapsed_total!=12:raise ValueError('wrong TM terminal state/transition count')
            # Each r-cell chunk comes from a bounded number of packed-word reads.
            chunks=[]
            for j in range(4):
                pos=sim.v.add(origin,j<<codec.rlog)
                chunks.append(sim.v.band(sim.get_window(0,pos),mask))
            out=codec.tm_to_output(chunks,4)
            value=sum(d<<j for j,d in enumerate(out))
            if value!=left*right or len(out)!=4:raise ValueError('composed multiplication mismatch')
            transitions+=elapsed_total;fixtures+=1
            runtime+=sim.v.ops+codec.ops-before
    # A fresh generic all-length model invocation computes its own parameters,
    # polynomial origin and all tables for this single input; no reused setup.
    fresh,receipt=tab.run_packed(1,3,144,machine(),{0:([1,1,1,1],4,'msb')},0,4,codec_module.Codec)
    if fresh!=[1,0,0,1] or receipt['TM_transitions']!=12 or not receipt['all_tables_generated_for_this_input']:
        raise ValueError('generic fresh-table composition failed')
    return dict(uniform_fresh_run=receipt,status='PASS',fixed_TM_states=144,fixed_TM_tapes=1,fixed_TM_alphabet=3,
                input_pairs=fixtures,TM_transitions=transitions,macro_calls=macros,
                precomputed_rows=tables,charged_setup_operations=setup,
                charged_runtime_operations=runtime,packed_contiguous_window_IO=True,
                real_TM_halting=True,runtime_word_multiplication_or_division=False,
                all_length_multiplier=False,emitted_RamStd_program=False,Lean_proof=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
