#!/usr/bin/env python3
"""Actual Count high-factor quotient refinement; no default-backend change."""
import argparse,ast,hashlib,importlib,json,math,sys
from pathlib import Path
from types import SimpleNamespace as NS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PREFIX='research/selected-bit-recursive-caller/predecessor'

def need(ok,message):
    if not ok:raise ValueError(message)

def sha(data):return hashlib.sha256(data).hexdigest()
def receipt(x):return dict(bits=x.bit_length(),sha256=sha(x.to_bytes(max(1,(x.bit_length()+7)//8),'big')))
def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']!='input':continue
        path=ROOT/row['path'];need(path.is_file() and not path.is_symlink() and sha(path.read_bytes())==row['sha256'],'source hash '+row['path'])
    return sum(r['usage']=='input' for r in manifest['files'])

def run():
    inputs=authenticate();sys.path[:0]=[str(HERE),str(ROOT/PREFIX),str(ROOT/PREFIX/'vendor')]
    import cardinal_counts,cardinality,fresh_rows,words,records,directory
    from adapter import compile_quotient
    Count=cardinal_counts.Count
    for name in ('fresh_rows','cardinal_counts','cardinality','counts','words','records','directory','stream','oracle','matrices','bitstream','routes'):
        module=importlib.import_module(name);need(str(Path(module.__file__).resolve()).startswith(str(ROOT/PREFIX)),'bound module '+name)
    tree=ast.parse((ROOT/'research/selected-bit-physical-caller/macro_machine.py').read_text())
    machine=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Machine')
    node=next(x for x in machine.body if isinstance(x,ast.FunctionDef) and x.name=='node')
    start=next(i for i,x in enumerate(node.body) if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='unused')
    block=node.body[start:start+4]
    need([type(x).__name__ for x in block]==['Assign','Expr','Assign','Try'],'literal NODE stock guard shape')
    save=next(x for x in machine.body if isinstance(x,ast.FunctionDef) and x.name=='save_count')
    commit=next(x for x in machine.body if isinstance(x,ast.FunctionDef) and x.name=='commit')
    env=dict(directory=directory,append_tape=directory.append_tape,Lease=(),Count=Count,need=words.need)
    exec(compile(ast.Module(body=[save,commit],type_ignores=[]),'<literal save_count>','exec'),env)
    code=compile(ast.Module(body=block,type_ignores=[]),'<literal NODE quotient guard>','exec')
    def value(count):
        cells=count.tape.cells[1:];at=cells.index(words.RIGHT)
        need(all(x in (0,1) for x in cells[:at]),'binary observer')
        return sum(x<<i for i,x in enumerate(cells[:at]))
    def actions(m):return {k:getattr(m,k) for k in ('reads','writes','moves')}
    def total(tapes):return {k:sum(getattr(t.meter,k) for t in tapes) for k in ('reads','writes','moves')}
    def sub(a,b):return {k:a[k]-b[k] for k in a}
    def case(d,w,q=3,families=28416,stock_multiple=9475,baseline=True,full_guard=True,rows_override=None,modulus_override=None):
        low=math.prod(q**d-q**i for i in range(d));factor=families*low*q**(d*d*(w-1));rows=stock_multiple*factor**2 if rows_override is None else rows_override
        adapted,constant=compile_quotient(q,d)
        versions=[('original',fresh_rows.quotient),('batched',adapted)] if baseline else [('batched',adapted)]
        results=[]
        for label,quotient in versions:
            tapes=[];old_init=records.Tape.__init__
            def register(t):old_init(t);tapes.append(t)
            records.Tape.__init__=register
            arena=words.Arena((q**w).bit_length()+1);modulus=arena.literal(q**w if modulus_override is None else modulus_override);ring=words.Ring(modulus)
            context=NS(q=q,dimension=d,codes=NS(size=low),ring=ring)
            original=Count.literal(rows);roles={'rows':original.tape,'unused':records.Tape()}
            def view(label):obj=object.__new__(Count);obj.tape=roles[label];return obj
            runtime=NS(context=context,topology=NS(families=families),binding=NS(stock_multiple=stock_multiple),tape=lambda name:roles[name],count=view)
            runtime.commit=lambda value,label:env['commit'](runtime,value,label)
            runtime.save_count=lambda value,label:env['save_count'](runtime,value,label)
            before_bytes=(bytes(original.tape.cells),original.tape.head);before_live=set(arena.live);existing=set(map(id,tapes))
            pre=total(tapes);numpre=actions(arena.meter);out=None;error=None
            divisions=[];old_divide=Count.divide_small
            def billed_divide(count,divisor):
                # Observer only: operands still reach the unchanged source algorithm.
                width=count.tape.cells[1:].index(words.RIGHT)
                divisions.append(dict(input_bits=width,divisor_bits=divisor.bit_length(),
                                      remainder_states=receipt(divisor),
                                      linear_bit_proxy=width*(4*divisor.bit_length()+8)))
                return old_divide(count,divisor)
            Count.divide_small=billed_divide
            old_inspect=words.Word.inspect;words.Word.inspect=lambda _:(_ for _ in ()).throw(ValueError('runtime decoding forbidden'))
            try:
                if full_guard:exec(code,dict(env,self=runtime,fresh_rows=NS(quotient=quotient)))
                else:
                    out=quotient(original,context,families);directory.append_tape(out.tape,roles['unused']);roles['unused'].rewind();out.close();out=None
            except ValueError as e:error=str(e)
            finally:words.Word.inspect=old_inspect;Count.divide_small=old_divide
            observed=None if error else value(view('unused'))
            if error is None:need(observed==rows//factor,'independent host quotient')
            need(before_bytes==(bytes(original.tape.cells),original.tape.head),'borrowed Count preserved')
            leaked=set(arena.live)-before_live
            if modulus_override is None:need(not leaked,'quotient numerical live set restored')
            else:
                need(error=='cardinality prime-power context','invalid context outside quotient theorem')
                arena.rollback(before_live)  # harness cleanup of the unchanged radix iterator's invalid-context exit
            # Returned unused tape is intentionally retained; all other temporary records erased.
            temporary=[t for t in tapes if id(t) not in existing and t is not roles['unused']]
            need(all(t.head==1 and all(v==words.BLANK for v in t.cells[1:]) for t in temporary),'temporary Count backing erased')
            entry=dict(version=label,error=error,quotient=None if observed is None else receipt(observed),record=sub(total(tapes),pre),residue=sub(actions(arena.meter),numpre),borrowed_preserved=True,numeric_restored=not leaked,invalid_context_leaked_slots=len(leaked),temporary_backing_erased=True,divisions=divisions,division_linear_bit_proxy=sum(x['linear_bit_proxy'] for x in divisions))
            results.append(entry)
            original.close();roles['unused'].clear();ring.close();arena.free(modulus);need(not arena.live,'terminal arena cleanup');records.Tape.__init__=old_init
        if baseline:need([(r['error'],r['quotient']) for r in results[:1]]==[(r['error'],r['quotient']) for r in results[1:]],'matched accepted domain and quotient/error')
        return dict(dimension=d,w=w,q=q,construction=adapted.construction,rows=receipt(rows),high_factor_bits=constant.bit_length(),high_remainder_bits=(constant-1).bit_length(),old_q_remainder_bits=(q-1).bit_length(),source_count_high_passes=d*d*(w-1),candidate_count_high_passes=w-1,source_radix_traversals=d*d,candidate_radix_traversals=1,results=results)
    cases=[case(2,1,families=4,stock_multiple=5),case(2,2,families=4,stock_multiple=5),case(2,3,families=4,stock_multiple=5),case(4,2,families=4,stock_multiple=5),case(64,1),case(64,2,baseline=False)]
    errors=[];d,w,q,F,Q=2,2,3,4,5;low=math.prod(q**d-q**i for i in range(d));A=F*low*q**(d*d*(w-1));good=Q*A*A
    for name,R in [('zero',0),('family',good+1),('GL',F*(low-1)*q**4),('high',F*low*(q**4-1)),('local_stock',A),('missing_9475',A*A)]:
        r=case(d,w,q,F,Q,rows_override=R);need(all(x['error'] for x in r['results']),'reject '+name);errors.append(dict(name=name,error=r['results'][0]['error']))
    malformed=case(2,2,families=4,stock_multiple=5,modulus_override=8);need(all(r['error']=='cardinality prime-power context' for r in malformed['results']),'malformed modulus rejection');errors.append(dict(name='non_power_modulus',error='cardinality prime-power context',outside_theorem=True,harness_rollback=True,results=malformed['results']))
    for c in cases:
        if len(c['results'])==2:
            a,b=c['results'];need(all(b['record'][k]<=a['record'][k] and b['residue'][k]<a['residue'][k] for k in ('reads','writes','moves')),'matched tape invoice')
    return dict(status='PASS_R437_BATCHED_HIGH_QUOTIENT',live_inputs=inputs,node_guard_ast_sha256=sha(ast.dump(ast.Module(body=block,type_ignores=[])).encode()),cases=cases,rejections=errors,scope='Fixed-context binary Count refinement and lane invoice; enlarged finite control charged separately; no uniform time or supplier admission.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();result=run();encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(encoded)
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])
if __name__=='__main__':main()
