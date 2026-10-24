"""Whole first-range source-array reserve; conservative, not a sharp peak.
JoyboyBrian with OpenAI Codex assistance. Apache-2.0.
"""
def continuation(h,i,r):
    a,b=2*i+4,r+3;t=max(a,b)
    return 2*((h+1)*t+h*b)+t+b+2

def bound(*,old_prefixes,highs,depth,code_bits,residue_bits,index_bits,fibre,
          program_backing,allocated,live,q):
    values=(old_prefixes,highs,code_bits,residue_bits,index_bits,fibre,program_backing,q)
    if any(type(x) is not int or x<=0 for x in values) or type(depth) is not int or depth<0:
        raise ValueError('positive canonical source domain')
    if len(allocated)!=2 or len(live)!=2 or any(type(x) is not int or x<0 for x in (*allocated,*live)) or any(l>h for h,l in zip(allocated,live)):
        raise ValueError('two canonical arena inventories')
    n=old_prefixes*highs;v=n*fibre
    record=code_bits+2+4096*(residue_bits+1)
    prefix=1+(depth+1)*record;old=1+depth*record;directory=1+n*(prefix-1)
    bits=max(1,v.bit_length(),index_bits,residue_bits)
    counts=200*(bits+3)
    numeric=sum((max(h,l+b)-h)*(w+2) for h,l,b,w in zip(allocated,live,(37672,41),(residue_bits,index_bits)))
    callback=max(continuation(depth,index_bits,residue_bits),
                 4+continuation(depth+1,index_bits,residue_bits)+program_backing+84+code_bits+2*index_bits)
    # All borrowed arrays and arena templates are already in K0.
    common=numeric+counts
    action_base=2*n*fibre+3+directory+2*prefix+4
    phases={
      'directory_setup':directory+2*old,
      'frame_validation':directory+prefix+5,
      'packet_copy':(2*n+1)*fibre+4+directory+2*prefix+max(prefix,fibre)+4,
      'add_callback':action_base+fibre+3+callback+1,
      'add_traversal':action_base+2*fibre+3,
      'nonadd':action_base+3*fibre+q*q+3,
    }
    return {'extra':common+max(phases.values()),'common_numeric':numeric,'common_counts':counts,
            'phase_extra':phases,'prefix_count':n,'directory':directory,'prefix':prefix,
            'old_prefix':old,'callback':callback,'volume':v,'count_digit_bound':bits}
