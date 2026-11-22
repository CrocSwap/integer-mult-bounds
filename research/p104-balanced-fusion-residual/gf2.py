"""Exact binary-mask row span, with the most significant bit as pivot."""

def bits(x):
    while x:
        bit=x&-x
        yield bit.bit_length()-1
        x^=bit

class Echelon:
    def __init__(self,rows=()):
        self.rows={}
        for x in rows:self.add(x)

    def add(self,x):
        while x:
            p=x.bit_length()-1
            if p not in self.rows:
                self.rows[p]=x
                return
            x^=self.rows[p]

    def residue(self,x):
        for p in sorted(self.rows,reverse=True):
            if x>>p&1:x^=self.rows[p]
        return x
