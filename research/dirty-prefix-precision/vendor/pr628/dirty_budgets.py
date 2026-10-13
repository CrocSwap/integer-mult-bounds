"""Integer-only verification of dirty-commutator precision for all nominated radices."""
from pathlib import Path
import argparse,json,importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('base',P/'check_budgets.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)

def budget(r,p,d):
    b.need(type(d)==int and d>=0,'initial magnitude bits')
    base=b.budgets(r,p+1+d);g=base['g'];n=r-1;N=4*n*n
    A=3*g+b.ceil_log2(13*(r+1));G=g+b.ceil_log2(r+2)
    w=max(A,2*g+1,p+1+b.ceil_log2(N)+A+d+1+(N-1)*G)
    return dict(radix=r,target_bits=p,initial_magnitude_bits=d,n=n,leaf_bound=N,dirty_arrays=(n-1).bit_length(),gap_bits=g,local_error_bits=A,growth_bits=G,working_bits=w,coefficient_target_bits=p+1+d)

def check(x):
    r,p,d=(x[k]for k in('radix','target_bits','initial_magnitude_bits'));base=b.budgets(r,p+1+d);b.check(base);g=base['g'];n=r-1;N=4*n*n;A=x['local_error_bits'];G=x['growth_bits'];w=x['working_bits']
    b.need(x['n']==n and x['leaf_bound']==N and x['dirty_arrays']==(n-1).bit_length(),'commutator resources')
    b.need(x['gap_bits']==g,'inherited root gap')
    b.need(A>=3*g+b.ceil_log2(13*(r+1))and G>=g+b.ceil_log2(r+2),'amplification exponents')
    b.need(w>=A and w>=2*g+1,'local precision')
    b.need(w>=p+1+b.ceil_log2(N)+A+d+1+(N-1)*G,'complete word error')
    b.need(x['coefficient_target_bits']>=p+1+d,'scaled original-input perturbation')
    return True

def main():
    records=[];controls=[]
    for r in range(3,257):
        try:b.prime_power_data(r)
        except ValueError:continue
        for p in(1,32,128,1024,1048576):
            for d in(0,20,1024):
                x=budget(r,p,d);check(x);records.append(x)
    for name,key,value in [('underprecision','working_bits',128),('insufficient_dirty_arrays','dirty_arrays',0),('underestimated_calls','leaf_bound',1),('omitted_dirt_magnitude','initial_magnitude_bits',2048),('omitted_input_scaling','coefficient_target_bits',128)]:
        x=budget(9,128,20);x[key]=value
        try:check(x)
        except ValueError as error:controls.append(dict(name=name,rejected=str(error)))
        else:raise ValueError('accepted corrupt budget '+name)
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.write_text(json.dumps(dict(status='passed',records=records,controls=controls),indent=2)+'\n');print('PASS',len(records),'budgets',len(controls),'controls')
if __name__=='__main__':main()
