#!/usr/bin/env python3
"""Explicit cleared-temporary lowering of every dyadic scalar coefficient."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compile_add(q):
    q = F(q)
    require(q != 0 and q.denominator & (q.denominator-1) == 0,
            'nonzero dyadic coefficient required')
    magnitude = abs(q.numerator)
    code = [('begin_zero',), ('add_source',)]
    for bit in bin(magnitude)[3:]:
        code.append(('double',))
        if bit == '1':
            code.append(('add_source',))
    code.extend(('half',) for _ in range(q.denominator.bit_length()-1))
    code.extend([('accumulate', 1 if q > 0 else -1), ('clear',)])
    bound = (3 + magnitude.bit_length()-1 + magnitude.bit_count()
             + q.denominator.bit_length()-1)
    require(len(code) == bound, 'Horner primitive count')
    return code


def execute(code):
    # Both ordinary inputs are independent arbitrary columns. The temporary
    # is an owned, initially cleared private stream, not an ordinary dirty role.
    source, target, temporary = [F(1), F(0)], [F(0), F(1)], None
    for event in code:
        tag = event[0]
        if tag == 'begin_zero':
            require(temporary is None, 'coefficient stream already live')
            temporary = [F(0), F(0)]
        elif tag == 'clear':
            require(temporary is not None, 'clear on inactive stream')
            temporary = None
        else:
            require(temporary is not None, 'coefficient stream is inactive')
            if tag == 'add_source':
                temporary = [a+b for a,b in zip(temporary, source)]
            elif tag == 'double':
                temporary = [2*a for a in temporary]
            elif tag == 'half':
                temporary = [a/2 for a in temporary]
            elif tag == 'accumulate':
                target = [a+event[1]*b for a,b in zip(target, temporary)]
            else:
                raise ValueError('unknown coefficient opcode')
    require(temporary is None, 'coefficient stream remains live')
    require(source == [1,0], 'source dirt changed')
    return target


def main():
    k_path = HERE/'k_encoder/RESULT.json'
    k = json.loads(k_path.read_text())
    coefficients = {F(x) for key in ('gather_coefficients','scatter_coefficients')
                    for x in k[key]}
    coefficients.update(F(x) for x in ('1','-1','1/16','-1/16','5/16','-5/16'))
    coefficients |= {-x for x in coefficients}
    records = []
    for q in sorted(coefficients):
        code = compile_add(q)
        require(execute(code) == [q,1], 'weighted scalar addition')
        # The dual weighted macro swaps its two ordinary operands and changes
        # the sign before lowering. It does not dualize noninvertible temp clear.
        require(execute(compile_add(-q)) == [-q,1], 'dual weighted macro')
        records.append({'coefficient': str(q), 'primitives': len(code),
                        'opcodes': code})
    controls = {}
    for label, code in (
        ('missing_clear', compile_add(F(5,16))[:-1]),
        ('missing_initial_zero', compile_add(F(5,16))[1:]),
        ('live_temporary_reuse', compile_add(F(5,16))[:-1]+compile_add(F(1,16)))):
        try:
            execute(code)
        except ValueError as error:
            controls[label] = str(error)
        else:
            raise ValueError('coefficient lifetime mutation accepted '+label)
    wrong = list(compile_add(F(5,16)))
    wrong.remove(('half',))
    require(execute(wrong) != [F(5,16),1], 'missing halving detected')
    controls['missing_halving'] = 'wrong coefficient rejected'
    receipt = {'status':'PASS_ALL_DYADIC_COEFFICIENT_STREAMS',
               'unique_signed_coefficients':len(records), 'records':records,
               'negative_controls':controls,
               'k_receipt_sha256':hashlib.sha256(k_path.read_bytes()).hexdigest(),
               'scope':'Every scalar coefficient in the complete word has an explicit '
                       'same-frame private Horner stream and count, active under -O. '
                       'Temporary starts cleared, ends erased, and no Fourier child '
                       'runs within it. These scalar primitive counts precede real '
                       'component doubling. Common-grid/tape and propagated child '
                       'approximation admission remain separate.'}
    (HERE/'COEFFICIENTS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'], 'coefficients='+str(len(records)), 'controls=4')


if __name__ == '__main__':
    main()
