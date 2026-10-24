#!/usr/bin/env python3
"""Independent arithmetic oracle and exact-source adapter checks; stdlib only."""
import argparse,ast,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
VENDOR=ROOT/'research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor'

def need(ok,why):
    if not ok:raise ValueError(why)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def authenticate():
    rows=json.loads((HERE/'SOURCES.json').read_text())['files']
    for row in rows:
        if row['usage']=='input':need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'source hash '+row['path'])
    return sum(row['usage']=='input' for row in rows)

def run():
    inputs=authenticate()
    sys.path[:0]=[str(HERE),str(VENDOR.parent),str(VENDOR)]
    import binary,adapter,words
    from records import Tape
    from cardinality import Natural
    from cardinal_counts import Count
    from types import SimpleNamespace as NS
    def tape(n):
        t=Tape();t.cells=bytearray([words.LEFT]+[int(b)for b in bin(n)[:1:-1]]+[words.RIGHT]);return t
    def value(t):return sum(b<<i for i,b in enumerate(t.cells[1:t.cells.index(words.RIGHT)]))
    def erased(t):return t.head==1 and all(c==words.BLANK for c in t.cells[1:])
    def total(ts):return sum(t.meter.reads+t.meter.writes+t.meter.moves for t in ts)
    def divide_bound(n,d):return 1024*(n+1)*(d+2)+1024*(n+d+4)
    digest=hashlib.sha256();cases=0;largest=0
    def case(n,d,implementation=binary):
        a,b,r,w=tape(n),tape(d),Tape(),Tape();borrowed=bytes(b.cells)
        old=Natural(a);expected=old.divide_small(d)
        implementation.divide(a,b,r,w)
        need(value(a)==n//d and value(r)==expected==n%d,'oracle quotient/remainder')
        need(bytes(a.cells)==bytes(old.tape.cells),'exact normalized source Count bytes')
        need(bytes(b.cells)==borrowed and a.head==b.head==r.head==w.head==1,'borrowed divisor and output heads')
        need(erased(w),'denominator erasure')
        need(len(r.cells)<=d.bit_length()+4 and len(w.cells)<=d.bit_length()+4,'fixed remainder backing')
        r.clear();a.clear();old.close()
        observed=total((a,b,r,w));upper=divide_bound(max(1,n.bit_length()),d.bit_length())
        need(observed<=upper,'complete division lane bound')
        return observed
    for n in range(256):
        for d in range(1,32):
            used=case(n,d);largest=max(largest,used);cases+=1
            digest.update(bytes((n//d,n%d)))
    # Beyond byte-sized calibration: arbitrary long carry/borrow and exact equality.
    wide=[]
    for bits in (32,65,127,255):
        for n,d in ((2**bits-1,2**(bits//2)+1),(2**bits+1,2**bits+1),(0,2**bits+1)):
            used=case(n,d);wide.append(dict(n_bits=max(1,n.bit_length()),d_bits=d.bit_length(),actions=used))
    multiplication_cases=0
    for n in range(32):
        for m in range(32):
            left,right,out=tape(n),tape(m),Tape();saved=(bytes(left.cells),bytes(right.cells))
            binary.multiply_into(left,right,out)
            need(value(out)==n*m,'independent full binary multiplication')
            need((bytes(left.cells),bytes(right.cells))==saved and left.head==right.head==out.head==1,'multiply borrowed restoration')
            A,B=max(1,n.bit_length()),max(1,m.bit_length())
            need(len(out.cells)<=A+B+3,'multiplication backing')
            out.clear();need(total((left,right,out))<=1024*(B+1)*(A+B+4),'complete multiplication lane bound')
            multiplication_cases+=1
    powers=[]
    for q in range(2,8):
        for d in range(1,4):
            radix=tape(q);a,b=Tape(),Tape();got,blank=binary.power_into(radix,d,a,b)
            need(value(got)==q**(d*d) and value(radix)==q and radix.head==1,'binary power oracle')
            need(erased(blank),'power spare erasure')
            need(max(len(a.cells),len(b.cells))<=(q**(d*d)).bit_length()+3,'two-role power backing')
            got.clear();used=total((radix,a,b));K=d*d;B=q.bit_length()
            bound=16*(B+2)+sum(1024*(B+1)*(j*B+5)+8*(j*B+3)for j in range(1,K+1))
            need(used<=bound,'complete power lane bound')
            powers.append(dict(q=q,dimension=d,actions=used,upper=bound))
    source=ROOT/'research/r437-batched-high-quotient/adapter.py'
    spec=importlib.util.spec_from_file_location('original_batched_quotient',source);original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    q=3;dimension=2;families=5;low_size=48
    radix,family,low=tape(q),tape(families),tape(low_size)
    borrowed=[(t,bytes(t.cells),t.head)for t in (radix,family,low)]
    lowered,workspace,body=adapter.compile_body(source,q,dimension,families,low_size,radix,family,low)
    old,_=original.compile_quotient(q,dimension)
    ast_source=ast.parse(source.read_text());outer=next(n for n in ast_source.body if isinstance(n,ast.FunctionDef)and n.name=='compile_quotient')
    expected_body=next(n for n in outer.body if isinstance(n,ast.FunctionDef)and n.name=='quotient')
    need(body==ast.dump(expected_body,include_attributes=False),'unchanged runtime quotient AST')
    real=[]
    for exponent in (1,2,3):
        arena=words.Arena((q**exponent).bit_length()+1,32);modulus=arena.literal(q**exponent);ring=words.Ring(modulus)
        context=NS(q=q,dimension=dimension,codes=NS(size=low_size),ring=ring)
        for residual in (1,7,19):
            amount=families*low_size*q**((exponent-1)*dimension*dimension)*residual
            fresh=Count.literal(amount);before=(bytes(fresh.tape.cells),fresh.tape.head);live=set(arena.live)
            calls=[];division=binary.divide
            def observed(n,d,r,w):
                calls.append('high'if d is workspace[0]else'families'if d is family else'low')
                return division(n,d,r,w)
            binary.divide=observed
            try:out=lowered(fresh,context,families)
            finally:binary.divide=division
            baseline=old(fresh,context,families)
            need(bytes(out.tape.cells)==bytes(baseline.tape.cells) and value(out.tape)==residual,'actual batched quotient source equivalence')
            need(calls==['families','low']+['high']*(exponent-1),'unchanged complete quotient call word')
            need((bytes(fresh.tape.cells),fresh.tape.head)==before and set(arena.live)==live,'actual fresh/radix ownership restored')
            need(all(erased(t)for t in workspace[1:]),'actual adapter scratch retirement')
            real.append(dict(w=exponent,residual=residual,call_word=calls))
            out.close();baseline.close();fresh.close()
        # Failure at each named factor; fresh remains borrowed on every rejection.
        for amount,message in ((1,'family'),(families,'GL'),(families*low_size,'high')):
            if message=='high' and exponent==1:continue
            fresh=Count.literal(amount);saved=bytes(fresh.tape.cells);live=set(arena.live)
            try:lowered(fresh,context,families)
            except ValueError as error:need(message in str(error),'actual factor failure reason')
            else:raise ValueError('inexact factor accepted')
            need(bytes(fresh.tape.cells)==saved and fresh.tape.head==1 and set(arena.live)==live,'rejected input restoration')
            need(all(erased(t)for t in workspace[1:]),'rejection scratch cleanup');fresh.close()
        ring.close();arena.free(modulus);need(not arena.live,'source ring disposal')
    for t in workspace:t.clear()
    need(all(erased(t)for t in workspace),'complete adapter workspace disposal')
    need(all(bytes(t.cells)==raw and t.head==head for t,raw,head in borrowed),'all borrowed compiled divisor roles restored')
    mutations=[('wrong equality comparison','if comparison>=0:','if comparison>0:',1,1),
               ('lost incoming bit','carry=numerator.read()','carry=ZERO',1,2),
               ('omitted subtraction write','remainder.write(difference&1);borrow=','remainder.write(ZERO);borrow=',5,3),
               ('missing quotient normalization','view(numerator).normalize();view(remainder).normalize()','view(remainder).normalize()',2,2),
               ('missing owned erasure',';denominator.clear()','',1,1)]
    rejected=[];text=(HERE/'binary.py').read_text()
    for label,before,after,n,d in mutations:
        need(before in text,'mutation anchor');ns={'__name__':'mutated_binary'};exec(compile(text.replace(before,after),label,'exec'),ns)
        try:case(n,d,NS(**ns))
        except ValueError:rejected.append(label)
        else:raise ValueError('mutant accepted '+label)
    # Validation cannot manufacture a write on an invalid zero divisor.
    a,b,r,w=tape(19),tape(0),Tape(),Tape();saved=bytes(a.cells)
    try:binary.divide(a,b,r,w)
    except ValueError as e:need(str(e)=='positive binary divisor','zero divisor guard')
    else:raise ValueError('zero divisor accepted')
    need(bytes(a.cells)==saved and erased(r)and erased(w),'zero divisor pre-mutation rejection')
    for cells in ([words.LEFT,1,9,words.RIGHT],[words.LEFT,1,0,words.RIGHT],[words.LEFT,words.RIGHT]):
        a,b,r,w=tape(19),Tape(),Tape(),Tape();b.cells=bytearray(cells);saved=(bytes(a.cells),bytes(b.cells))
        try:binary.divide(a,b,r,w)
        except ValueError:pass
        else:raise ValueError('malformed divisor accepted')
        need((bytes(a.cells),bytes(b.cells))==saved and a.head==b.head==1 and erased(r)and erased(w),'malformed validation heads and bytes')
    for alias in ('radix-first','radix-second','first-second'):
        radix_alias,a,b=tape(3),Tape(),Tape()
        if alias=='radix-first':a=radix_alias
        elif alias=='radix-second':b=radix_alias
        else:b=a
        saved=[(t,bytes(t.cells),t.head)for t in(radix_alias,a,b)]
        try:binary.power_into(radix_alias,2,a,b)
        except ValueError as e:need(str(e)=='distinct power roles','power alias guard')
        else:raise ValueError('power role alias accepted')
        need(all(bytes(t.cells)==raw and t.head==head for t,raw,head in saved),'power alias rejects before mutation')
    N,D,B,K=1040413,520192,127,4096
    return dict(status='PASS_R437_BINARY_DIVISOR_REALIZATION',live_inputs=inputs,
        exhaustive=dict(cases=cases,sha256=digest.hexdigest(),max_record_actions=largest),wide=wide,multiplication_cases=multiplication_cases,powers=powers,
        actual_source=dict(q=q,dimension=dimension,low_size=low_size,families=families,cases=real,runtime_ast_sha256=sha(body.encode())),
        rejected_mutations=rejected,guard_controls=['zero divisor','invalid digit','noncanonical zero padding','empty number','three power role aliases'],admitted_parameter_invoice=dict(numerator_bits=N,high_divisor_bits=D,
        division_upper=divide_bound(N,D),power_upper=16*(B+2)+sum(1024*(B+1)*(j*B+5)+8*(j*B+3)for j in range(1,K+1)),
        execution='not executed; formula instantiation only'),scope='Uniform binary quotient/power realization and small real-adapter source composition; all Context/codebook, inherited radix Word, complete caller and payload costs remain separate.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();result=run()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])
if __name__=='__main__':main()
