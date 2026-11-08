"""Written-proof annotations, not runtime machine arithmetic."""


def resources(q, dimension, code_bits, fields, width, fibre, repeats=1):
    if min(q,dimension,code_bits,fields,width,fibre,repeats)<1:
        raise ValueError('positive proof parameters')
    ell_w,ell_f=width.bit_length(),fibre.bit_length()
    length=(q**width).bit_length()+1
    field=code_bits+2+dimension*dimension*(length+1)
    record=fields*field
    prefixes=repeats*q**((width-1)*dimension*dimension*fields)
    volume=prefixes*fibre
    owned=2*record+2*length+width+fibre+ell_w+ell_f+max(ell_w,ell_f)+18
    visited=3*volume+2*record+2*length+width+fibre+4*ell_w+4*ell_f+max(ell_w,ell_f)+fields*(code_bits+1)+41
    transitions=10000*(q.bit_length()+1)*(width+1)**2+1000*prefixes*(record+fibre+1)
    return {'word_bits':length,'field_symbols':field,'prefix_symbols':record,'prefixes':prefixes,
            'payload_bits':volume,'owned_visited_exact':owned,'all_visited_exact':visited,
            'transition_upper_bound':transitions}
