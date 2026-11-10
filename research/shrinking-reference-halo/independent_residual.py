"""Independent residual certification of the actual Gaussian consumer.

Uses the author's numerical consumer, but no author's verifier or expected
outputs. The mathematical oracle is an exact original-reference residual.
"""
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import sys

PACKAGE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    engine = load('lead_halo_engine', PACKAGE/'engine.py')
    source = load('lead_halo_source', PACKAGE/'source.py')
    raw = source.authenticated_inputs(PACKAGE)
    reference = source.make_reference(raw, (32,8,2,1,8,32))
    reference.require_narrow_gap()
    n = reference.target_size
    H = [[reference.entry('narrow',r,c).value for c in range(n)] for r in range(n)]
    E = [[F(int(r==c))-H[r][c] for c in range(n)] for r in range(n)]
    rho = max(sum(map(abs,row)) for row in E)
    gap = F(int((1-rho)*(1<<16)),1<<16)
    shift = 0
    while (1<<shift)*gap < 1:
        shift += 1
    plan = engine.Plan(n, 2*reference.spec.source_halfwidth+2, 28,4,shift,gap)
    rng = random.Random(2026110874)
    scale = 1<<plan.bits
    x = []
    for r in range(n):
        re = rng.randrange(-scale//2, scale//2)
        im = rng.randrange(-scale//3, scale//3)
        x.append((re,im))
    production = engine.Bill()
    table,_ = engine.prepare_table(plan,lambda r,c:E[r][c],reference.description_hash,production)
    table_digest = engine.tape_digest(table.tape)
    y = []
    all_bits = 0
    for row in range(n):
        bill = engine.Bill()
        lower,length = row-plan.halo, 1+2*plan.halo
        page = engine.extract_page(table,lower,length,bill)
        inp = engine.input_tape(plan,tuple(x[j%n] for j in range(lower,lower+length)),bill)
        inp_digest,page_digest = engine.tape_digest(inp),engine.tape_digest(page.tape)
        output = engine.apply_line(page,inp,row,1,bill)
        value, = engine.consume(output)
        if (engine.tape_digest(inp)!=inp_digest or engine.tape_digest(page.tape)!=page_digest
                or inp.head or page.tape.head or table.tape.head):
            raise AssertionError('borrowed inputs or origin changed')
        y.append(tuple(F(v,scale) for v in value))
        all_bits += bill.reads+bill.writes+bill.moves
    if engine.tape_digest(table.tape)!=table_digest:
        raise AssertionError('reference table changed')
    def residual(values):
        return max(sum(abs(F(x[r][part],scale*(1<<shift))-
                           sum(H[r][c]*values[c][part] for c in range(n)))
                       for part in (0,1)) for r in range(n))
    defect = residual(y)
    certified = defect/gap
    if not certified < F(1,1<<20):
        raise AssertionError(('complete original-reference inverse residual',str(certified)))
    shifted = y[1:]+y[:1]
    wrong_lower_bound = residual(shifted)/(1+rho)
    if wrong_lower_bound <= F(1,1<<20):
        raise AssertionError('wrong canonical return order not detected')
    print('PASS_LEAD_ORIGINAL_REFERENCE_RESIDUAL')
    print(json.dumps({'period':n,'original_entries':n*n,'all_physical_output_rows':len(y),
                      'fixed_source_sha256':reference.description_hash,
                      'engine_sha256':sha256((PACKAGE/'engine.py').read_bytes()).hexdigest(),
                      'source_adapter_sha256':sha256((PACKAGE/'source.py').read_bytes()).hexdigest(),
                      'actual_bit_actions':all_bits,
                      'certified_inverse_error_upper':float(certified),
                      'required_error_upper':float(F(1,1<<20)),
                      'wrong_return_order_error_lower_bound':float(wrong_lower_bound)},sort_keys=True))


if __name__=='__main__':
    main()
