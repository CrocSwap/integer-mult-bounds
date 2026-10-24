"""Conservative completed transport bounds; formulas, never runtime decoding."""
def invoice(q, dimension, word_bits, old_prefixes, low_classes, highs,
            fibre_bits, literal_bits, numerical_capacity=65536):
    values=(q,dimension,word_bits,old_prefixes,low_classes,highs,fibre_bits,literal_bits,numerical_capacity)
    if any(type(x) is not int or x<1 for x in values):
        raise ValueError('positive integer invoice parameters')
    if q<3 or dimension>64 or word_bits<2:
        raise ValueError('source transport parameter domain')
    d,b,O,L,H,F,t,R=dimension,word_bits,old_prefixes,low_classes,highs,fibre_bits,literal_bits,numerical_capacity
    k=d*d;u=b+2
    n=4+O.bit_length()+F.bit_length()+L.bit_length()+k*b
    K=k*(b+1);P=O*H*F;V=L*P;D=H*(K+F);A=q*q+128
    # Each bound includes its complete output; commit is added separately.
    G=4096*(k+1)*u**3*(n+t+2)+4096*(O+1)*(L+1)*(H+1)*(F+1)*(n+2)
    route=16384*(O+1)*((k+1)*(t+u)*u**3+(H+1)*(d+1)**3*u**2+(k*b+1)*(H+1)*(K+F+1)*(n+2))
    actions=2*G+2*route+128*(V+P+n+1)+8*A
    backing=(A+8)*(V+D+P+n+8)+(R+1)*(b+2)
    return dict(count_digit_bound=n,key_symbols=K,packet_bits=P,family_bits=V,
        decorated_symbols=D,scratch_roles=A,gather_or_scatter_actions=G,
        route_packet_actions=route,completed_roundtrip_actions=actions,
        retained_cells=backing,maximum_live_scratch_leases=32,
        semantics='unit tape reads+writes+moves; fixed compiled source control; supplied valid Context')
