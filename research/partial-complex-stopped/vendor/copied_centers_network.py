"""Exact finite_bridge function(s) extracted from icekylinx PR104.
Original: scripts/copied_centers_network.py, commit 948ce1510df750f4c18b96bdaef436a86f8bf834,
SHA-256 409ebfbd8a41c4c4d089aa0949fcf5a949415dc26f57440ffd48b7bd8881e6a9. Apache-2.0; see NOTICE.
"""
from fractions import Fraction as Q
from structured_bulk_assembly import halving
from common import require

def finite_bridge(bit, phase, rows):
    m, W, s, N = (phase[k] for k in ('m', 'W', 'total_rank', 'N'))
    terms = []
    for row in rows:
        h, v, c = (row[k] for k in ('h', 'v', 'c'))
        local = 4*(c+v)+10*v+4*h*v+4*h*h+8*h+8
        terms.append(dict(h=h, v=v, c=c, invocations=N//v,
                          local_group_upper=local, copied_center_extra_groups=2*h))
    G = N+sum(t['invocations']*(t['local_group_upper']+t['copied_center_extra_groups']) for t in terms)
    E = 64*(W+m+G+1)**3
    charge = 2*G*W*W+8*s+4*W+4+32*m
    B, r = s+E, phase['maxchild']
    C0 = 32*m*B*B
    require(charge < E and 2*B*(m-r) >= s+E and 2*B+18 < C0, 'Semantic induction')
    db, dc = halving(bit['m'], bit['maxchild']), halving(m, r)
    wb, wc = bit['W'].bit_length(), W.bit_length()
    coeff = wb*db+wc*dc
    degree = 1000*((coeff*51)//25000+1)
    return dict(bit=dict(m=bit['m'], W=bit['W'], maxchild=bit['maxchild'], halving_degree=db, wire_bits=wb),
        complex=dict(m=m, W=W, s=s, maxchild=r, halving_degree=dc, wire_bits=wc,
                     scalar_terms=terms, scalar_group_upper=G),
        semantic=dict(E=E, literal_charge=charge, strict_literal_gap=E-charge, B=B,
                      C0=C0, C1=1, induction_gap=2*B*(m-r)-s-E),
        rows=dict(coefficient=coeff, degree=degree, suffix_slope=4*degree,
                  degree_gap=Q(degree)-Q(coeff*51,25),
                  contract='W_complex^D_complex * W_bit^D_bit; one preceding prefix and padding; all temporary copies sequential'))
