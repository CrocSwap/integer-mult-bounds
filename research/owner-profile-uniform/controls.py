"""Focused rejection controls and exact boundary controls."""
import copy
from contextlib import contextmanager
import independent as independent
import verify as primary


@contextmanager
def replace(module, name, value):
    old=getattr(module,name)
    setattr(module,name,value)
    try:
        yield
    finally:
        setattr(module,name,old)


def rejected(name, action):
    try:
        action()
    except ValueError:
        return name
    raise ValueError('control unexpectedly passed: '+name)


def main():
    controls=[]
    with replace(primary,'PRICES',dict(primary.PRICES, **{})):
        primary.PRICES[5] += 1
        controls.append(rejected('helper-price',primary.dual))
    with replace(primary,'CAPS',{8:49,16:32,32:32,48:32}):
        controls.append(rejected('capacity-count',primary.dual))
    with replace(primary,'LOCAL',{**primary.LOCAL,1:primary.LOCAL[1]+1}):
        controls.append(rejected('local-paid-profile',primary.bind_selected))
    with replace(primary,'WIDTHS',{**primary.WIDTHS,4:79}):
        controls.append(rejected('helper-inventory',primary.bind_selected))
    original_read=primary.read
    def duplicate_owner(path):
        value=original_read(path)
        if path.name=='OWNERS.json.gz':
            value=copy.deepcopy(value);value[1]=copy.deepcopy(value[0])
        return value
    with replace(primary,'read',duplicate_owner):
        controls.append(rejected('duplicate-owner',primary.bind_selected))
    original_cases=primary.cases
    def bad_mass():
        cases=original_cases(); cases[0][1][1]-=1;return cases
    with replace(primary,'cases',bad_mass):
        controls.append(rejected('lost-mass',primary.algebraic))
    # The formerly used no44 relaxation is below I* before b=1/3.
    old_relaxation={43:1,5:1,44:-1,3:-1,1:-1}
    with replace(primary,'cases',lambda:[('old-relaxation',old_relaxation)]+original_cases()[1:]):
        controls.append(rejected('old-relaxation-algebraic',primary.algebraic))
    controls.append(rejected('old-relaxation-Bernstein',lambda:independent.bernstein(old_relaxation)))
    t2=original_cases()[1][1]
    controls.append(rejected('interval-overreach',lambda:independent.bernstein(t2,independent.F(1,2))))
    # Genuine neutral boundaries: every mass-balanced difference vanishes at b=0.
    for _,c in original_cases():
        primary.need(sum(r*n for r,n in c.items())==0,'b=0 boundary')
    primary.need(sum(original_cases()[-1][1].values())==0,'t12 b=1 boundary')
    # Independent generators must cover precisely the same mathematical cases.
    other=independent.intervals()
    primary.need([c for _,c in original_cases()]==[r['coefficients'] for r in other], 'independent case coverage')
    primary.need(len(controls)==9,'control coverage')
    print('PASS_UNIFORM_OWNER_CONTROLS rejected=9 neutral_boundaries=2 case_models=12')

if __name__=='__main__':
    main()
