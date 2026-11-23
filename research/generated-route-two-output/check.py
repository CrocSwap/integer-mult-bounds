"""Exact dense arithmetic checks and deliberately broken producer controls.

The oracle never uses the producer's comparators or carry-register recurrence.
Finite tests corroborate the all-size argument in PROOF.md.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256, sha1
import argparse
import json
import random
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import transducer as t

def need(ok, message):
    if not ok: raise ValueError(message)

def authenticate():
    files = json.loads((HERE / 'ORIGINS.json').read_text())['files']
    for entry in files:
        data = (HERE / entry['path']).read_bytes()
        need(sha256(data).hexdigest() == entry['sha256'], 'source hash '+entry['path'])
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == entry['git_blob'], 'source blob '+entry['path'])
    return len(files)

def residue(x, modulus):
    return 0 if modulus == 1 else x.numerator*pow(x.denominator,-1,modulus)%modulus

def direct_column(column, values, q):
    numerator = sum(a*x for a,x in zip(column.numerators,values))
    low = numerator*pow(column.denominator,-1,q)%q
    return low, (numerator-column.denominator*low)//q

def dense(word, n):
    matrix=[]
    for basis in range(n):
        row=[F(j==basis) for j in range(n)]
        for op in word:
            if op[0]=='swap':
                i,j=op[1:];row[i],row[j]=row[j],row[i]
            elif op[0]=='add':row[op[1]]+=F(op[3])*row[op[2]]
            elif op[0]=='scale':row[op[1]]*=F(op[2])
            else:raise ValueError('oracle opcode')
        matrix.append(row)
    return matrix

def multiply(row, matrix):
    return [sum((x*matrix[i][j] for i,x in enumerate(row) if x),F(0)) for j in range(len(row))]

def carries(result):
    return [F(x,1<<result['denominator_exponent']) for x in result['carry_numerators']]

def check_column(column, values, q):
    bits,carry,obs=t.produce(column,t.integer_rows(values,q))
    need((t.from_bits(bits),carry)==direct_column(column,values,q),'two-output column mismatch')
    b=q.bit_length()
    need(len(bits)==b and obs.first_rows==obs.second_rows==b,'two-pass width')
    need(obs.flush_rows==column.denominator_exponent,'flush charge')
    need(obs.input_symbols==2*b*(len(values)+1),'input symbol charge')
    need(obs.quotient_updates==b*len(column.thresholds),'comparator charge')
    need(obs.output_symbols==b,'output symbol charge')
    return obs

def columns_from_source():
    alphabet=json.loads((HERE/'retained/ALPHABET.json').read_text());columns=[]
    for value in alphabet['addition_coefficients']:
        x=F(value);d=x.denominator
        columns.append(('add/'+value,t.Column((d,x.numerator),d.bit_length()-1)))
    for value in alphabet['scale_coefficients']:
        x=F(value);d=x.denominator
        columns.append(('scale/'+value,t.Column((x.numerator,),d.bit_length()-1)))
    return columns,alphabet

def mutant(name, before, after):
    source=(HERE/'transducer.py').read_text();need(source.count(before)==1,'mutation anchor')
    module=types.ModuleType('mutant_'+name);sys.modules[module.__name__]=module
    exec(compile(source.replace(before,after),name,'exec'),module.__dict__)
    return module

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    sources=authenticate();columns,alphabet=columns_from_source()
    scalar_cases=peak_state=long_cases=0
    for label,column in columns:
        for q in (3,5,7,9):
            inputs=((x,y) for x in range(q) for y in range(q)) if len(column.numerators)==2 else ((x,) for x in range(q))
            for values in inputs:
                obs=check_column(column,values,q);scalar_cases+=1
                peak_state=max(peak_state,obs.largest_signed_state)
        for q in (11,15,17,31,65):
            for values in [(0,)*len(column.numerators),(q-1,)*len(column.numerators),tuple((q//2+i)%q for i in range(len(column.numerators)))]:
                obs=check_column(column,values,q);scalar_cases+=1
                peak_state=max(peak_state,obs.largest_signed_state)
        if label in ('add/23/32','add/-23/32','add/15','add/-15','scale/1/16','scale/16','scale/-8','scale/-1/8'):
            for width in (13,64,257,1025,4097):
                q=(1<<(width-1))+1;values=tuple(q-1-j*(q//3) for j in range(len(column.numerators)))
                check_column(column,values,q);long_cases+=1

    rng=random.Random(20261123);cases=json.loads((HERE/'retained/CASES.json').read_text())
    source_maps=source_rows=high_checks=inverse_checks=fractional=max_work_bits=0
    for case in cases:
        n,word=case['n'],case['word']
        for op in word:
            if op[0]=='add':need(str(F(op[3])) in alphabet['addition_coefficients'],'addition alphabet')
            elif op[0]=='scale':need(str(F(op[2])) in alphabet['scale_coefficients'],'scale alphabet')
        matrix=dense(word,n);inverse=t.invert_word(word);inverse_matrix=dense(inverse,n)
        for q in (3,5,9,17):
            for _ in range(3):
                low=[rng.randrange(q) for _ in range(n)];old=list(low)
                result=t.evaluate_row(word,low,q);need(low==old,'borrowed low input changed')
                exact=multiply(low,matrix);expected_low=[residue(x,q) for x in exact];carry=carries(result)
                need(result['low']==expected_low,'whole-word low')
                need(carry==[(x-y)/q for x,y in zip(exact,expected_low)],'whole-word carry')
                need(all(abs(x)<2*result['envelope']['product_bound'] for x in result['carry_numerators']),'numerator envelope')
                max_work_bits=max(max_work_bits,result['envelope']['signed_work_bits'])
                fractional+=sum(x.denominator>1 for x in carry)
                returned=t.evaluate_row(inverse,result['low'],q)
                need(returned['low']==low,'inverse low')
                need(carries(returned)==[-x for x in multiply(carry,inverse_matrix)],'inverse carry law');inverse_checks+=1
                for w in (1,2,3):
                    modulus=q**(w-1);high=[rng.randrange(modulus) for _ in range(n)]
                    hh=[residue(x+c,modulus) for x,c in zip(multiply(high,matrix),carry)]
                    direct=[residue(x,q**w) for x in multiply([l+q*h for l,h in zip(low,high)],matrix)]
                    need([l+q*h for l,h in zip(result['low'],hh)]==direct,'full-width reconstruction');high_checks+=1
                source_rows+=1
            source_maps+=1

    # Actual stage-one port, complete dimension 134, all spectators retained.
    port=next(c for c in cases if c['label']=='actual_port/17');n=134;word=port['word'];matrix=dense(word,n)
    complete_rows=complete_coordinates=0
    for q in (3,5):
        for i in range(n):
            low=[int(j==i) for j in range(n)];low[(i+1)%n]=(low[(i+1)%n]+1)%q
            result=t.evaluate_row(word,low,q);exact=multiply(low,matrix)
            need(result['low']==[residue(x,q) for x in exact],'complete-stage low')
            need(carries(result)==[(x-y)/q for x,y in zip(exact,result['low'])],'complete-stage carry')
            need(result['low'][15:]==low[15:] and not any(result['carry_numerators'][15:]),'spectator mutation')
            complete_rows+=1;complete_coordinates+=n

    controls=[]
    def rejected(label,fn):
        try:fn()
        except ValueError:controls.append(label)
        else:raise ValueError('control accepted '+label)
    column=t.Column((2,1),1)
    rejected('even_radix',lambda:t.produce(column,t.integer_rows((1,2),4)))
    rejected('out_of_range_low',lambda:t.produce(column,t.integer_rows((3,0),3)))
    rejected('noncanonical_radix',lambda:t.produce(column,lambda:iter([(1,0,1),(0,0,1),(0,0,0)])))
    rejected('nonunit_scale',lambda:t.word_envelope([('scale',0,'3')]))
    rejected('nondyadic_coefficient',lambda:t.word_envelope([('add',0,1,'1/3')]))
    noflush=mutant('no_flush','for _ in range(column.denominator_exponent):','for _ in range(0):')
    def reject_flush():
        bits,c,_=noflush.produce(noflush.Column((1,),4),noflush.integer_rows((16,),17))
        need((noflush.from_bits(bits),c,len(bits))==(1,0,5),'missing-flush output')
    rejected('missing_denominator_flush',reject_flush)
    badfloor=mutant('truncation','states[index] = (states[index] + digit - j * radix) // 2','states[index] = int((states[index] + digit - j * radix) / 2)')
    def reject_floor():
        for q in (3,5,7):
            col=badfloor.Column((1,-1),0)
            for x in range(q):
                for y in range(q):
                    bits,c,_=badfloor.produce(col,badfloor.integer_rows((x,y),q))
                    need((badfloor.from_bits(bits),c)==direct_column(col,(x,y),q),'truncated negative state')
    rejected('signed_floor_replaced_by_truncation',reject_floor)
    badscale=mutant('denominator','updated = [x << s for x in numerators]','updated = list(numerators)')
    def reject_scale():
        word=[('scale',0,'1/2'),('scale',1,'1/2')]
        r=badscale.evaluate_row(word,[1,1],3)
        need(carries(r)==[F(-1,2),F(-1,2)],'unscaled old numerator')
    rejected('unscaled_fused_carry_register',reject_scale)
    word=[('add',0,1,'1/2'),('scale',0,'2')];low=[0,1];q=3
    a=t.evaluate_row(word,low,q);b=t.evaluate_row(list(reversed(word)),low,q)
    need((a['low'],carries(a))!=(b['low'],carries(b)),'wrong-order witness');controls.append('wrong_word_order')
    a=t.evaluate_row([('scale',0,'1/2')],[1],3)
    need(carries(a)==[F(-1,2)],'fractional carry witness');controls.append('ordinary_integer_carry')
    stale=t.evaluate_row([('scale',0,'2')],[1],3);fresh=t.evaluate_row([('scale',0,'2')],a['low'],3)
    need(stale['low']!=fresh['low'],'stale inverse witness');controls.append('stale_inverse_low')
    a=t.evaluate_row([('add',0,1,'3')],[0,1],3)
    need(a['low']==[0,1] and carries(a)==[F(1),F(0)],'low-invisible shear');controls.append('dropped_low_zero_shear')

    # Independent finite corroboration of the append-only LSB-output state cut.
    latency_radices=latency_prefixes=0
    for q in range(5,256,2):
        width=q.bit_length();k=1<<(width-2);a,r=divmod(q,k)
        outputs=[]
        for prefix in range(k):
            highs=(2,2) if a==3 else ((2,1) if prefix<r else (1,1))
            x,y=prefix+highs[0]*k,highs[1]*k
            need(0<=x<q and 0<=y<q,'latency witness leaves canonical domain')
            need(x%k==prefix and y%k==0,'latency witness changed read prefix')
            need(q<=x+y<2*q,'latency overflow completion')
            low0=prefix;low1=(x+y)%q
            need((low0^low1)&1,'latency first-output ambiguity')
            outputs.append(low0);latency_prefixes+=1
        need(len(set(outputs))==k,'common completion fails to distinguish states')
        latency_radices+=1
    need(((0+(2+2)*2-6)%6)&1==0,'even-radix scope control')
    controls.append('one_pass_odd_radix_scope')
    summary=dict(status='PASS_GENERATED_TWO_OUTPUT_CARRY',source_files=sources,fixed_columns=len(columns),
        addition_coefficients=len(alphabet['addition_coefficients']),scale_coefficients=len(alphabet['scale_coefficients']),
        scalar_cases=scalar_cases,long_stream_cases=long_cases,longest_input_bits=4097,
        max_product_state_bits=max(c.state_bits() for _,c in columns),max_threshold_comparators=max(len(c.thresholds) for _,c in columns),
        observed_max_abs_bounded_state=peak_state,source_constructor_maps=source_maps,source_rows=source_rows,
        full_width_reconstructions=high_checks,inverse_cocycle_checks=inverse_checks,fractional_carry_coordinates=fractional,
        max_case_signed_work_bits=max_work_bits,complete_stage_rows=complete_rows,complete_stage_coordinates=complete_coordinates,
        one_pass_cut_radices=latency_radices,one_pass_cut_prefixes=latency_prefixes,
        negative_controls=controls,note='Finite corroboration; no literal payload tape execution, canonical assumption removal or new kappa.')
    raw=json.dumps(summary,indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(raw)
    print(raw,end='')

if __name__=='__main__':main()
