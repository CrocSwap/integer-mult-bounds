"""Opt-in integer-row port for the pinned emitted local checker.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
Shared-denominator representation follows prior PR367/824/1137/1156 work;
the checker itself remains attributed to icekylinx and its retained lineage.
"""
from fractions import Fraction

class Row:
    """Sparse integer numerators divided by 2**exponent."""
    def __init__(self, values=None):
        self.values={};self.exponent=0
        if values:
            self.values={k:int(v) for k,v in values.items()}
            if any(Fraction(v).denominator!=1 for v in values.values()):
                raise ValueError('initial Row must be integral')

    def clone(self):
        result=Row();result.values=self.values.copy();result.exponent=self.exponent
        return result

    def scale(self,q):
        a,b=q.numerator,q.denominator
        if b&(b-1):raise ValueError('non-dyadic row scale')
        result=self.clone();result.exponent+=b.bit_length()-1
        # Retain explicit zero entries exactly as the original SCALE dictionary.
        result.values={k:a*v for k,v in self.values.items()}
        return result

    def add_scaled(self,other,q):
        a,b=q.numerator,q.denominator
        if b&(b-1):raise ValueError('non-dyadic row addition')
        source_exp=other.exponent+b.bit_length()-1
        exponent=max(self.exponent,source_exp)
        left_shift=exponent-self.exponent;right_shift=exponent-source_exp
        if left_shift:self.values={k:v<<left_shift for k,v in self.values.items()}
        for k,v in other.values.items():
            total=self.values.get(k,0)+((a*v)<<right_shift)
            if total:self.values[k]=total
            else:self.values.pop(k,None)
        self.exponent=exponent

    def __bool__(self):return bool(self.values)

    def __eq__(self,other):
        if isinstance(other,Row):
            exponent=max(self.exponent,other.exponent)
            return ({k:v<<(exponent-self.exponent) for k,v in self.values.items()}==
                    {k:v<<(exponent-other.exponent) for k,v in other.values.items()})
        if isinstance(other,dict):
            if set(self.values)!=set(other):return False
            return all(v*Fraction(other[k]).denominator==Fraction(other[k]).numerator*(1<<self.exponent) for k,v in self.values.items())
        return NotImplemented

REWRITES=[
    ("rows={('L',r):{r:Q(1)} for r in range(n)}", "rows={('L',r):Row({r:1}) for r in range(n)}"),
    ("rows[target]={};norm[target]=Q(0)", "rows[target]=Row();norm[target]=Q(0)"),
    ("rows[target]=dict(rows[source]);norm[target]=norm[source]", "rows[target]=rows[source].clone();norm[target]=norm[source]"),
    ("rows[target]={j:q*x for j,x in rows[target].items()};norm[target]*=abs(q)", "rows[target]=rows[target].scale(q);norm[target]*=abs(q)"),
    ("row=rows.setdefault(target,{})\n                for j,x in list(rows[source].items()):\n                    z=row.get(j,Q(0))+q*x\n                    if z:row[j]=z\n                    else:row.pop(j,None)", "row=rows.setdefault(target,Row())\n                row.add_scaled(rows[source],q)"),
    ("controls=[]\nfor name,mut in [", "controls=[]\n_encoded_program=json.dumps(ir['local_programs']['forward'])\nfor name,mut in ["),
    ("es=copy.deepcopy(ir['local_programs']['forward']);mut(es)", "es=json.loads(_encoded_program);mut(es)")
]

def transform(source):
    for before,after in REWRITES:
        if source.count(before)!=1:raise ValueError('pinned row rewrite count mismatch')
        source=source.replace(before,after)
    return source
