"""Bounded source-admission mathematics and actual native-word return seam.
No native expansion Tile, coefficient producer or complete prefix executes.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from source_binding import authenticate,bind_clauses,opened,need,node_at,ROOT
from admission import trunc_div
from check_exact import checks

def decode(text,q):
    width=q+2;result=[]
    for row in text.split('#')[:-1]:
        need(len(row)==2*width,'complete external record')
        pair=[]
        for at in (0,width):
            word=row[at:at+width]
            value=int(word[1:],2)*(-1 if word[0]=='1' else 1)
            need(value or word[0]=='0','canonical signed zero');pair.append(value)
        result.append(tuple(pair))
    return result

def main():
    pins=authenticate();clauses=bind_clauses();mathematics=checks()
    # AST fingerprints bind the reviewed clauses, without projected execution.
    mutations=0
    import ast
    for row in json.loads((HERE/'CLAUSES.json').read_text())['clauses']:
        parsed=ast.parse((ROOT/row['path']).read_text());target=parsed
        for name in row['names']:target=next(n for n in target.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==name)
        number=next((n for n in ast.walk(target) if isinstance(n,ast.Constant) and type(n.value) is int),None)
        if number is None:continue
        number.value+=1
        need(sha256(ast.dump(target,include_attributes=False).encode()).hexdigest()!=row['sha256'],'source clause mutation detected')
        mutations+=1
    with opened() as state:
        from return_codec import ExpansionReturn
        from cardinal_counts import Count
        from records import Tape
        from ring_words import Signed,write_signed
        from router_metadata import owned
        from session import initialize_marker,erase_marker
        from check_support import no_decode
        from words import BLANK
        q,J,T,S=12,3,16,9
        values=[(((-1)**i)*(123+11*i),((-1)**(i//2))*(87+7*i)) for i in range(T)]
        need(all(a*a+b*b<1<<(2*q-4) for a,b in values),'fixture quarter-disk words')
        def native_field(rows):
            tape=Tape();erase_marker(tape);initialize_marker(tape)
            with owned(Count.literal(q+2)) as (width,):
                for pair in rows:
                    for value in pair:
                        with owned(Signed(Count.literal(abs(value)),value<0)) as (word,):write_signed(word,tape,width)
            tape.rewind();return tape
        native=native_field(values);saved=bytes(native.cells)
        volume=Count.literal(T);saved_volume=bytes(volume.tape.cells)
        machine=ExpansionReturn(state,volume,q,J)
        with no_decode():returned=machine.run(native)
        actual=decode(returned.inspect(),q)
        expected=[(trunc_div(a,1<<J),trunc_div(b,1<<J)) for a,b in values]
        need(actual==expected,'actual dimension-changing codec matches independent dyadic oracle')
        error=max(abs(Fraction(a,1<<q)-Fraction(c,1<<(q+J)))+abs(Fraction(b,1<<q)-Fraction(d,1<<(q+J)))
                  for (a,b),(c,d) in zip(actual,values))
        need(error<Fraction(2,1<<q),'paid final scale/drop component error')
        need(bytes(native.cells)==saved and native.head==1,'borrowed native body and origin')
        need(bytes(volume.tape.cells)==saved_volume and volume.tape.head==1,'borrowed encoded target Count')
        try:machine.run(native)
        except ValueError:pass
        else:raise ValueError('missing protected pending return')
        need(decode(returned.inspect(),q)==expected,'protected pending bytes')
        output_hash=sha256(returned.inspect().encode()).hexdigest();machine.consume()
        failures=[]
        for label,rows in (('short_native',values[:-1]),('long_native',values+[(0,0)])):
            bad=native_field(rows);saved_bad=bytes(bad.cells)
            try:
                with no_decode():machine.run(bad)
            except ValueError:failures.append(label)
            else:raise ValueError('missing native volume failure')
            need(machine.closed and not machine.pending and not machine.pool.live,'failure closes adapter')
            need(bytes(bad.cells)==saved_bad and bad.head==1,'failed borrowed volume body and origin')
            bad.clear();erase_marker(bad)
        # Original compact S clock is valid syntax but cannot clock a T return.
        old_clock=state.B.Tape('old compact S source clock','0'*(2*(q+2))+'#')
        state.B.clear(old_clock)
        for _ in range(S):
            for symbol in '0'*(2*(q+2))+'#':state.B.append(old_clock,symbol)
        state.B.home(old_clock)
        wrong=state.codec.Codec(state.B,Tape,BLANK,initialize_marker,erase_marker,state.codec.Format(q+2,q,q+2,q,J))
        try:
            with no_decode():
                wrong.prepare_input(old_clock);wrong.prepare_return(native,old_clock)
        except ValueError as error_message:
            need('extra native output' in str(error_message),'old S-clock failure at complete native extent')
            failures.append('old_S_clock')
        else:raise ValueError('old source clock incorrectly admits enlarged return')
        finally:
            wrong.abort();state.B.clear(old_clock)
            for template in wrong.templates:state.B.clear(template);state.B.home(template)
        # Native input/count/work aliases are rejected before any conversion.
        for alias in (machine.volume.tape,volume.tape,machine.codec.input,machine.pool.tapes[0]):
            try:machine.run(alias)
            except ValueError:failures.append('native_metadata_or_work_alias')
            else:raise ValueError('missing native ownership rejection')
        need(bytes(native.cells)==saved and native.head==1,'borrowed field survives all controls')
        need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in machine.pool.tapes),'native scratch erased at canonical origins')
        need(machine.clock.inspect()==machine.output.inspect()=='' and not machine.codec.active,'external helper fields erased')
        need([(trunc_div(a,1<<(J+2)),trunc_div(b,1<<(J+2))) for a,b in values]!=expected,'double-counted expansion bits control')
        need(values!=expected,'omitted final scale control')
        machine.close()
        # Actual coarse final shift can erase a bounded field: radius is not accuracy.
        eraser=ExpansionReturn(state,volume,q,q+1)
        with no_decode():zero=eraser.run(native)
        need(decode(zero.inspect(),q)==[(0,0)]*T,'actual coarse-grid erasure control')
        eraser.consume();eraser.close();volume.close();native.clear();erase_marker(native)
        receipt=dict(canonical_inputs=pins[0],public_files=pins[1],source_clauses=clauses,source_clause_mutations=mutations,
                     mathematics=mathematics,native_return=dict(T=T,old_S=S,q=q,J=J,output=actual,
                     output_sha256=output_hash,component_l1_projection_error=str(error),
                     failures=failures,actual_coarse_erasure=True,complete_prefix_executed=False,
                     production_Tile_executed=False,production_Fourier_executed=False),
                     claim='fine-family expansion producer/page admission and declared slow-reference interface; no new kappa')
    print('PASS_FINE_EXPANSION_PAGE_ADMISSION')
    print(json.dumps(receipt,sort_keys=True,indent=2))

if __name__=='__main__':main()
