"""Compile bounded inherited recipes before any numerical input."""
import scalar_sources
lower = scalar_sources.activate()
from fractions import Fraction
from words import need


class Recipe:
    def __init__(self,kind,numerator,denominator,policy):
        need(kind in ("add","scale") and type(numerator) is int and type(denominator) is int and
             abs(numerator) <= 4096 and 0 < abs(denominator) <= 4096,
             "fixed scalar literal vocabulary")
        self.key = kind,numerator,denominator,policy
        self.kind,self.coefficient = kind,Fraction(numerator,denominator)
        self.program = tuple(tuple(row) for row in lower.certify(kind,numerator,denominator,policy=policy))
        need(len(self.program) <= 32, "bounded compiled scalar recipe")
        rows = ((Fraction(1),Fraction(0)),(Fraction(0),Fraction(1)),(Fraction(0),Fraction(0)))
        for instruction in self.program:
            if instruction[0] == "copy":
                need(rows[instruction[1]] == (0,0), "literal COPY destination starts zero")
            rows = lower.execute((instruction,),rows)
        self.source_writes = any(instruction[1] == 1 for instruction in self.program)
        self.uses_scratch = any(instruction[1] == 2 for instruction in self.program)
