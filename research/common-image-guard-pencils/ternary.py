"""Exact small certificates in the sharp field-order boundary."""
from fractions import Fraction

from dependency import joint, prefix_count
from finite import Field
from laws import marginal, orbit_size


def four_rows():
    field = Field(3)
    shapes = [[(1,0,0),(1,1,0),(1,2,0),(1,0,1)],
              [(1,0,0),(1,1,0),(1,0,1),(1,1,1)],
              [(1,0,0,0),(1,1,0,0),(1,0,1,0),(1,0,0,1)]]
    t = Fraction(7, 9)
    lower3 = Fraction(2, 3)*(Fraction(35, 81)/t**4)**4*(1 - 4*Fraction(17, 35)**4)
    lower4 = Fraction(2, 3)*(Fraction(113, 243)/t**4)**4*(
        1 - 13*Fraction(43, 113)**4 - 27*Fraction(7, 113)**4)
    if min(lower3, lower4) <= 1 or not 3*t**5 < 1:
        raise ValueError("ternary tail threshold")
    cases = []
    for forms in shapes:
        rank = len(forms[0])
        for m in range(rank, 5):
            counted = prefix_count(field, forms, m)
            value = joint(field, forms, m)
            if counted != value*orbit_size(3, rank, m) or value <= marginal(3, m)**4:
                raise ValueError("ternary quartet comparison")
            cases.append(dict(forms=forms,m=m,joint=str(value),ratio=str(value/marginal(3,m)**4),
                              passing_tuples=counted))
    return dict(lower_bound_at_d4={"rank3":str(lower3),"rank4":str(lower4)},exceptions=cases)
