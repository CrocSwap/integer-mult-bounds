"""Construct two-rate causal precision bounds for an authenticated word.

The signed-row method and directed grid follow the retained causal.py.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F


def require(ok, message):
    if not ok:
        raise ValueError(message)


def prepare(word, weights, source):
    count, scale, ops = source.setup(word)
    values = [w[0]*(1 << 96) for w in weights]
    require(all(v.denominator == 1 for v in values), 'exact ideal weights on grid')
    return count, scale, ops, list(map(int, values))


def multiply(value, coefficient):
    product = value*coefficient.numerator
    require(product % coefficient.denominator == 0, 'exact signed row division')
    return product//coefficient.denominator


def bound(prepared, guards, details=False):
    count, scale, ops, weights = prepared
    require(type(guards) is tuple and len(guards) == 2 and
            all(g is None or type(g) is int and 0 <= g <= 32 for g in guards),
            'two guards in 0..32 or exact classes')
    rows = [{} for _ in range(count)]
    scores = [0]*count
    deltas = [0]*len(ops)
    peak = 0
    for j, (op, r, q, s) in enumerate(ops):
        noisy = op in ('MOVE', 'ADD', 'SCALE')
        if noisy:
            feedback = scores[r]
            if op == 'ADD':
                product = abs(q.numerator)*scores[s]
                require(product % q.denominator == 0, 'exact feedback division')
                feedback += product//q.denominator
            elif op == 'SCALE':
                product = abs(q.numerator)*feedback
                require(product % q.denominator == 0, 'exact scale feedback')
                feedback = product//q.denominator
            guard = guards[0 if op == 'MOVE' else 1]
            divisor = scale if guard is None else scale << guard
            delta = 0 if guard is None else -(-(weights[j]*scale+feedback)//divisor)
        else:
            delta = 0
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
            scores[r] = 0
        elif op == 'COPY':
            rows[r] = {i:multiply(v, q) for i, v in rows[s].items()}
            scores[r] = multiply(scores[s], abs(q))
        elif op == 'SCALE':
            rows[r] = {i:multiply(v, q) for i, v in rows[r].items()}
            scores[r] = multiply(scores[r], abs(q))
        elif op == 'ADD':
            for i, value in rows[s].items():
                old = rows[r].get(i, 0)
                updated = old+multiply(value, q)
                scores[r] += (abs(updated)-abs(old))*deltas[i]
                if updated:
                    rows[r][i] = updated
                else:
                    rows[r].pop(i, None)
        if noisy:
            deltas[j] = delta
            rows[r][j] = scale
            scores[r] += scale*delta
        peak = max(peak, scores[r])
    result = dict(final=[F(v, scale << 96) for v in scores], peak=F(peak, scale << 96))
    if details:
        result['deltas'] = deltas
    return result


def search(prepared, public):
    """Find the complete upper-closed feasible region by monotone search."""
    tested = {}
    def trial(native, scalar):
        key = (native, scalar)
        if key not in tested:
            result = bound(prepared, key)
            maximum = max(result['final'][:public])
            tested[key] = dict(guards=list(key), maximum=str(maximum), peak=str(result['peak']),
                               feasible=maximum < 1)
        return tested[key]['feasible']
    low, high = 0, 33
    while low < high:
        middle = (low+high)//2
        if middle <= 32 and trial(middle, 32):
            high = middle
        else:
            low = middle+1
    require(low <= 32, 'nonempty finite guard domain')
    first = low
    scalar = 32
    frontier = []
    for native in range(first, 33):
        while scalar > 0 and trial(native, scalar-1):
            scalar -= 1
        require(trial(native, scalar), 'monotone passing boundary')
        frontier.append([native, scalar])
    native_count = sum(op[0] == 'MOVE' for op in prepared[2])
    scalar_count = sum(op[0] in ('ADD', 'SCALE') for op in prepared[2])
    objective = lambda pair: native_count*pair[0]+scalar_count*pair[1]
    best = min(frontier, key=lambda pair:(objective(pair), pair))
    uniform = next(g for g in range(33) if any(n <= g and s <= g for n, s in frontier))
    return dict(domain=[0, 32], first_native=first, frontier=frontier,
                optimum=best, optimum_cost=objective(best),
                uniform_guard=uniform, uniform_cost=(native_count+scalar_count)*uniform,
                native_sites=native_count, scalar_sites=scalar_count,
                tested=[tested[key] for key in sorted(tested)])


def check_certificate(prepared, public, certificate):
    """Check only the corners that prove the complete monotone boundary."""
    first = certificate['first_native']
    frontier = certificate['frontier']
    require(type(first) is int and 0 <= first <= 32, 'first native guard')
    require(type(frontier) is list and len(frontier) == 33-first, 'complete guard rows')
    previous = 33
    blocks = []
    for native, pair in enumerate(frontier, first):
        require(type(pair) is list and len(pair) == 2 and pair[0] == native and
                type(pair[1]) is int and 0 <= pair[1] <= previous, 'monotone guard boundary')
        if pair[1] != previous:
            blocks.append([native, native, pair[1]])
        else:
            blocks[-1][1] = native
        previous = pair[1]
    corners = []
    requests = [] if first == 0 else [(first-1, 32, False)]
    for left, right, scalar in blocks:
        requests.append((left, scalar, True))
        if scalar:
            requests.append((right, scalar-1, False))
    for native, scalar, feasible in requests:
        result = bound(prepared, (native, scalar))
        maximum = max(result['final'][:public])
        require((maximum < 1) == feasible, 'guard corner feasibility')
        corners.append(dict(guards=[native, scalar], feasible=feasible,
                            maximum=str(maximum), peak=str(result['peak'])))
    native_count = sum(op[0] == 'MOVE' for op in prepared[2])
    scalar_count = sum(op[0] in ('ADD', 'SCALE') for op in prepared[2])
    objective = lambda pair: native_count*pair[0]+scalar_count*pair[1]
    best = min(frontier, key=lambda pair:(objective(pair), pair))
    uniform = next(g for g in range(33) if any(n <= g and s <= g for n, s in frontier))
    expected = dict(domain=[0, 32], first_native=first, frontier=frontier,
                    optimum=best, optimum_cost=objective(best), uniform_guard=uniform,
                    uniform_cost=(native_count+scalar_count)*uniform,
                    native_sites=native_count, scalar_sites=scalar_count)
    require(certificate == expected, 'complete guard certificate fields')
    return corners
