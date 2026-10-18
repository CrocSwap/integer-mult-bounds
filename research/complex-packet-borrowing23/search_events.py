"""Optional discovery model: positive unit additions with disjoint supports.

Requires z3-solver; --engine cvc5 also requires cvc5. Neither dependency is
needed by verify.py. UNSAT applies only to the domain described in README.md.
Apache-2.0. NeoKazuya, with substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
import z3


def build(n, helpers, timeout=180000, max_adds=None, frames_on=True, mixed=True):
    full = (1 << n) - 1
    target_start = n + helpers
    total = 2*n + helpers
    # Sources are immutable. Helpers may read sources/helpers; targets may
    # additionally read targets. Every directed pair has at most one event.
    specs = [(t, s) for t in range(n, total) for s in range(total)
             if s != t and (t >= target_start or s < target_start)
             and not (t >= target_start and s == t-target_start)]
    size = len(specs)
    solver = z3.Solver()
    solver.set(timeout=timeout, random_seed=23)
    clocks = [z3.Int(f'c{e}') for e in range(size)]
    active = [z3.Bool(f'a{e}') for e in range(size)]
    packets = [z3.BitVecVal(1 << s, n) if s < n else z3.BitVec(f'p{e}', n)
               for e, (t, s) in enumerate(specs)]
    frames = [z3.BitVec(f'f{e}', n) for e in range(size)]
    incoming = {t: [e for e, (d, s) in enumerate(specs) if d == t] for t in range(n, total)}

    def at_most_one(terms):
        for a, b in itertools.combinations(terms, 2):
            solver.add(z3.Or(z3.Not(a), z3.Not(b)))

    for e in range(size):
        solver.add(clocks[e] >= 0, clocks[e] < size)
        solver.add(z3.Implies(z3.Not(active[e]), clocks[e] == 0))
    for t in range(n, total):
        for i in range(n):
            contributors = [z3.And(active[e], (packets[e] & (1 << i)) != 0) for e in incoming[t]]
            at_most_one(contributors)
            if t >= target_start:
                if i != t-target_start:
                    solver.add(z3.Or(contributors))
                else:
                    solver.add(z3.Not(z3.Or(contributors)))
    for e, (t, s) in enumerate(specs):
        if s >= n:
            for i in range(n):
                arrived = z3.Or([z3.And(active[f], clocks[f] < clocks[e], (packets[f] & (1 << i)) != 0)
                                 for f in incoming[s]])
                solver.add(z3.Implies(active[e], ((packets[e] & (1 << i)) != 0) == arrived))
            solver.add(z3.Implies(active[e], packets[e] != 0))
            solver.add(z3.Implies(z3.Not(active[e]), packets[e] == 0))
        if frames_on:
            allowed = full
            if t >= target_start:
                allowed ^= 1 << (t-target_start)
            if s >= target_start:
                allowed &= full ^ (1 << (s-target_start))
            solver.add(z3.Implies(active[e], (frames[e] & ~allowed) == 0))
            solver.add(z3.Implies(active[e], (packets[e] & ~frames[e]) == 0))
            solver.add(z3.Implies(z3.Not(active[e]), frames[e] == 0))
        # An event's common frame includes every earlier frame touching either
        # register, including source-only reads. Disjoint events may commute.
        for f in range(e):
            if not set(specs[e]) & set(specs[f]):
                continue
            both = z3.And(active[e], active[f])
            solver.add(z3.Implies(both, clocks[e] != clocks[f]))
            if frames_on:
                solver.add(z3.Implies(z3.And(both, clocks[e] < clocks[f]), (frames[e] & ~frames[f]) == 0))
                solver.add(z3.Implies(z3.And(both, clocks[f] < clocks[e]), (frames[f] & ~frames[e]) == 0))
        if s >= n and (s, t) in specs:
            reverse = specs.index((s, t))
            if e < reverse:
                solver.add(z3.Or(z3.Not(active[e]), z3.Not(active[reverse])))
    if mixed:
        solver.add(z3.Or([z3.And(active[e], packets[e] & (packets[e]-1) != 0)
                          for e, (t, s) in enumerate(specs) if n <= s < target_start and t >= target_start]))
    if max_adds is not None:
        solver.add(z3.Sum([z3.If(a, 1, 0) for a in active]) <= max_adds)
    return solver, specs, clocks, active, packets


def alternate_solve(path, timeout):
    import cvc5
    alternate = cvc5.Solver()
    alternate.setLogic('ALL')
    alternate.setOption('tlimit-per', str(timeout))
    alternate.setOption('seed', '23')
    parser = cvc5.InputParser(alternate)
    parser.setFileInput(cvc5.InputLanguage.SMT_LIB_2_6, str(path))
    manager = parser.getSymbolManager()
    while True:
        command = parser.nextCommand()
        if command.isNull():
            break
        if command.getCommandName() == 'check-sat':
            continue
        response = command.invoke(alternate, manager)
        if response.strip():
            raise RuntimeError(response)
    answer = str(alternate.checkSat())
    version = alternate.getVersion()
    return answer, version.decode() if isinstance(version, bytes) else version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, default=6)
    parser.add_argument('--helpers', type=int, default=0)
    parser.add_argument('--max-adds', type=int)
    parser.add_argument('--timeout', type=int, default=180000)
    parser.add_argument('--engine', choices=('z3', 'cvc5'), default='z3')
    parser.add_argument('--control', choices=('direct', 'no-frames'))
    parser.add_argument('--export-only', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.n < 3 or args.helpers < 0 or args.timeout <= 0:
        parser.error('require n >= 3, helpers >= 0 and positive timeout')
    if args.control and args.helpers:
        parser.error('controls are for the no-helper model')
    started = time.monotonic()
    solver, specs, clocks, active, packets = build(
        args.n, args.helpers, args.timeout, args.max_adds,
        frames_on=args.control != 'no-frames', mixed=args.helpers > 0)
    if args.helpers == 0:
        if args.control == 'direct':
            for e, (_, source) in enumerate(specs):
                if source >= args.n:
                    solver.add(z3.Not(active[e]))
        else:
            # Relabel any nonempty shared edge and one carried source to 0->1
            # carrying source 2. The simultaneous source/omitted-target
            # permutation preserves the all-but-one demand and frame incidence.
            edge = specs.index((args.n+1, args.n))
            solver.add(active[edge], packets[edge] & 4 != 0)
    args.out.mkdir(parents=True, exist_ok=False)
    formula = solver.to_smt2()
    smt_path = args.out / 'model.smt2'
    smt_path.write_text(formula, encoding='utf-8', newline='\n')
    result = {'n': args.n, 'helpers': args.helpers, 'max_adds': args.max_adds,
              'control': args.control, 'seed': 23, 'timeout_ms': args.timeout,
              'formula_sha256': hashlib.sha256(formula.encode()).hexdigest(),
              'engine': args.engine}
    if args.export_only:
        result.update(result='exported', version=z3.get_version_string())
    elif args.engine == 'cvc5':
        result['result'], result['version'] = alternate_solve(smt_path, args.timeout)
    else:
        status = solver.check()
        result.update(result=str(status), version=z3.get_version_string())
        if status == z3.unknown:
            result['reason'] = solver.reason_unknown()
        elif status == z3.sat:
            model = solver.model()
            order = sorted((model.eval(clocks[e]).as_long(), e) for e in range(len(specs))
                           if z3.is_true(model.eval(active[e])))
            result['operations'] = [list(specs[e]) for _, e in order]
            result['packets'] = [model.eval(packets[e]).as_long() for _, e in order]
    result['seconds'] = time.monotonic()-started
    (args.out / 'result.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
