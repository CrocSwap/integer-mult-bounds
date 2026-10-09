"""Optional routing discovery; emitted paths are checked without an SMT solver.

This module is not required to replay a positive routing certificate. Solver
timeouts/unknown are kept distinct from unsatisfiability and from a checked
positive routing. No rank conclusion is drawn from an unsuccessful search.
"""
from itertools import permutations

from certify import require
from finite_bit_contract import scalar_permutation, check_routing_paths


def paths_from_port_choices(W, gates, choices):
    require(len(choices) == len(gates), 'One port choice per gate is required')
    paths = [[] for _ in range(W)]; tokens = list(range(W)); edge = 0
    for gate, choice in zip(gates,choices):
        ports = tuple(gate['roles']); choice = tuple(choice)
        require(sorted(choice) == sorted(ports), 'Port choice is not a bijection')
        for role in ports:
            paths[tokens[role]].append(edge); edge += 1
        old = list(tokens)
        for out,source in zip(ports,choice): tokens[out] = old[source]
    for role in range(W):
        paths[tokens[role]].append(edge); edge += 1
    check_routing_paths(W,gates,paths)
    return paths


def discover_routing(W, gates, timeout_ms=10000):
    import z3
    rho = scalar_permutation(W,gates)
    solver = z3.Solver(); solver.set(timeout=timeout_ms,random_seed=0)
    two_port = all(len(g['roles']) == 2 for g in gates)
    bits = (W-1).bit_length()
    last = [z3.BitVecVal(w,bits) if two_port else z3.IntVal(w) for w in range(W)]
    choices = []; options = []
    for j,gate in enumerate(gates):
        roles = tuple(gate['roles'])
        require(len(roles) <= 4, 'Bounded discovery supports at most four ports')
        perms = list(permutations(roles)); options.append(perms)
        if two_port:
            choice = z3.Bool(f'route_{j}'); choices.append(choice)
            new = [z3.BitVec(f'wire_{j}_{r}',bits) for r in roles]
            solver.add(new[0] == z3.If(choice,last[roles[1]],last[roles[0]]))
            solver.add(new[1] == z3.If(choice,last[roles[0]],last[roles[1]]))
            for r,x in zip(roles,new): last[r] = x
            continue
        choice = z3.Int(f'route_{j}'); choices.append(choice)
        solver.add(choice >= 0,choice < len(perms))
        new = [z3.Int(f'wire_{j}_{r}') for r in roles]
        for k,perm in enumerate(perms):
            solver.add(z3.Implies(choice == k,z3.And(*[x == last[s] for x,s in zip(new,perm)])))
        for r,x in zip(roles,new): last[r] = x
    for w,out in enumerate(rho): solver.add(last[out] == w)
    answer = solver.check()
    if answer != z3.sat:
        return dict(status=str(answer),reason=solver.reason_unknown() if answer == z3.unknown else
                    'Solver reports no routing; no independently checked negative certificate emitted.',
                    solver_version=z3.get_version_string())
    model = solver.model()
    selected = [list(opts[int(z3.is_true(model.eval(c,model_completion=True))) if two_port else model.eval(c).as_long()])
                for opts,c in zip(options,choices)]
    paths = paths_from_port_choices(W,gates,selected)
    return dict(status='checked routing',port_choices=selected,paths=paths,
                solver_version=z3.get_version_string(),check=check_routing_paths(W,gates,paths))
