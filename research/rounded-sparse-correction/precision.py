"""Exact error transfers and reversible source-product rounding.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(ok,why):
    if not ok: raise ValueError(why)


def merge(target,source,coefficient):
    for key,value in source.items():
        target[key] = target.get(key,Q(0))+coefficient*value
        if not target[key]: del target[key]


def transfer(program,n=799,noise='fractional'):
    need(noise in ('all','fractional'),'Noise model')
    rows = [{i:Q(1)} for i in range(n)]
    prefix = [];peak_signal = Q(1);peak_error = Q(0)
    for t,e in enumerate(program):
        op,r = e[:2];c = Q(e[-2])
        need(e[-1] == 127 and op in ('ADD','SCALE'),'Literal correction operation')
        if op == 'ADD':
            need(r != e[2],'Distinct fields');merge(rows[r],rows[e[2]],c)
        else: rows[r] = {j:c*v for j,v in rows[r].items()}
        if noise == 'all' or c.denominator > 1: rows[r][n+t] = Q(1)
        signal = sum(abs(v) for j,v in rows[r].items() if j < n)
        error = sum(abs(v) for j,v in rows[r].items() if j >= n)
        prefix.append((r,signal,error));peak_signal = max(peak_signal,signal);peak_error = max(peak_error,error)
    output = [sum(abs(v) for j,v in row.items() if j >= n) for row in rows]
    return rows,prefix,peak_signal,peak_error,max(output)


def reverse_transfer(program,output,n=799,noise='fractional'):
    # This is a backward functional, not a forward row calculation.
    row = {output:Q(1)};errors = {}
    for t in range(len(program)-1,-1,-1):
        e = program[t];r = e[1];c = Q(e[-2]);weight = row.get(r,Q(0))
        if weight and (noise == 'all' or c.denominator > 1): errors[n+t] = weight
        if e[0] == 'SCALE':
            if weight: row[r] = c*weight
        elif weight:
            s = e[2];row[s] = row.get(s,Q(0))+c*weight
            if not row[s]: del row[s]
    return row | errors


def nearest(numerator,denominator):
    need(type(numerator) is int and type(denominator) is int and denominator > 0,'Integer rounding operands')
    quotient,remainder = divmod(numerator,denominator)
    return quotient+int(2*remainder > denominator or (2*remainder == denominator and quotient & 1))


def rounded(program,values,width,reverse=False,trace=None):
    need(type(width) is int and width >= 2 and type(reverse) is bool,'Rounded word format')
    trace = trace if trace is not None else {}
    def word(v):
        need(type(v) is int and -(1 << (width-1)) <= v < (1 << (width-1)),'Signed word overflow')
        trace['peak_integer'] = max(trace.get('peak_integer',0),abs(v))
        return v
    for v in values: word(v)
    events = reversed(program) if reverse else program
    for e in events:
        need(e[0] == 'ADD' and e[-1] == 127 and e[1] != e[2],'Reversible scalar ADD')
        r,s = e[1:3];c = Q(e[3]);a,d = c.numerator,c.denominator
        need(d & (d-1) == 0,'Dyadic product')
        product = word(a*values[s])
        increment = word(nearest(product,d))
        values[r] = word(values[r]-increment if reverse else values[r]+increment)
        trace['product_numerator_evaluations'] = trace.get('product_numerator_evaluations',0)+1
        trace['data_additions'] = trace.get('data_additions',0)+1
        trace['rounded_products'] = trace.get('rounded_products',0)+int(d > 1)
    return values


def exact(program,values,errors=None):
    values = list(map(Q,values));errors = errors or {}
    for t,e in enumerate(program):
        c = Q(e[-2]);r = e[1]
        if e[0] == 'ADD': values[r] += c*values[e[2]]
        else: values[r] *= c
        values[r] += errors.get(t,Q(0))
    return values


def inverse(program):
    out = []
    for e in reversed(program):
        z = list(e);z[-2] = str(-Q(e[-2]) if e[0] == 'ADD' else 1/Q(e[-2]));out.append(z)
    return out
