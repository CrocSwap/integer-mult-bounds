"""Exhaustive eight-bit fitting check on a finite actual-port witness."""
from collections import Counter, deque
import json
import numpy as np
from geometry import SOURCE, load, profile_labels, require


def solve(domains, edges):
    odd = [label for label in range(256) if label.bit_count() % 2]
    orthogonal = [sum(1 << j for j, other in enumerate(odd)
                      if not ((label & other).bit_count() % 2)) for label in odd]
    neighbors = [[] for _ in domains]
    for first, second in edges:
        neighbors[first].append(second)
        neighbors[second].append(first)
    counts = Counter()
    maximum_depth = 0

    def visit(current, depth):
        nonlocal maximum_depth
        counts['nodes'] += 1
        maximum_depth = max(maximum_depth, depth)
        queue = deque((first, second) for edge in edges for first, second in (edge, edge[::-1]))
        while queue:
            first, second = queue.popleft()
            remaining = revised = current[first]
            while remaining:
                bit = remaining & -remaining
                remaining -= bit
                if not (orthogonal[bit.bit_length()-1] & current[second]):
                    revised -= bit
            if revised == current[first]:
                continue
            counts['domain_reductions'] += 1
            if not revised:
                counts['empty_domains'] += 1
                return None
            current[first] = revised
            queue.extend((neighbor, first) for neighbor in neighbors[first] if neighbor != second)
        sizes = [domain.bit_count() for domain in current]
        if max(sizes) == 1:
            return [odd[domain.bit_length()-1] for domain in current]
        first = min((i for i, size in enumerate(sizes) if size > 1), key=lambda i: sizes[i])
        choices = current[first]
        while choices:
            bit = choices & -choices
            choices -= bit
            child = current.copy()
            child[first] = bit
            result = visit(child, depth+1)
            if result is not None:
                return result
        return None

    result = visit(domains.copy(), 0)
    return result, dict(search_counts=dict(counts), maximum_depth=maximum_depth)


def certify_profile(vectors, profiles):
    certificate = load('PROFILE-H8.json')
    anchors, variables = certificate['anchors'], certificate['vertices']
    indices = anchors+variables
    require(len(anchors) == 7 and len(variables) == 17 and len(set(indices)) == 24,
            'Twenty-four distinct ports with seven anchors')
    require(len(set(map(int, profiles[indices]))) == 1, 'Witness belongs to a single profile')
    selected = vectors[indices].astype(np.int32).reshape(24, 3, 8)
    active = np.logical_and.reduce([selected[:, block] @ selected[:, block].T != 0 for block in range(3)])
    np.fill_diagonal(active, False)
    require(int(active[:7, :7].sum()) == 42, 'Seven actual mutually active anchor ports')
    lookup = {tuple(vector): index for index, vector in enumerate(vectors)}
    rotated = []
    for shift in range(3):
        block_order = [(block-shift) % 3 for block in range(3)]
        shifted = selected[:, block_order].reshape(24, 24)
        ids = [lookup[tuple(vector)] for vector in shifted]
        require(np.all(profiles[ids] == (int(profiles[indices[0]])+shift) % 3),
                'Cyclic witness is present in the expected profile')
        shifted_active = np.logical_and.reduce([
            shifted[:, 8*block:8*(block+1)] @ shifted[:, 8*block:8*(block+1)].T != 0
            for block in range(3)])
        np.fill_diagonal(shifted_active, False)
        require(np.array_equal(shifted_active, active), 'Cyclic witness has the identical actual graph')
        rotated.append(dict(profile=int(profiles[ids[0]]), ports=ids))
    fitting = json.loads((SOURCE/'evidence/TURYN-FITS.json').read_text())
    known, _ = profile_labels(vectors, profiles, fitting['profile_fit_independent_rows'])
    gram = (known[indices] @ known[indices].T) & 1
    require(np.all(np.diag(gram) == 1) and not gram[active].any(),
            'Known nine-dimensional profile labels fit the witness')
    odd = [label for label in range(256) if label.bit_count() % 2]
    domains = []
    for index in range(17):
        mask = sum(1 << j for j in range(7) if active[7+index, j])
        domains.append(sum(1 << j for j, label in enumerate(odd) if not (label & mask)))
    require(all(domains), 'Nonempty initial eight-bit domains')
    edges = [(i, j) for i in range(17) for j in range(i) if active[7+i, 7+j]]
    result, receipt = solve(domains, edges)
    require(result is None, 'No standard-dot eight-bit fitting on the actual-port witness')
    # Removing the variable-to-variable edge constraints must restore a fit.
    control, _ = solve(domains, [])
    require(control is not None and all(label.bit_count() % 2 for label in control),
            'Relaxed fitting positive control')
    for index, label in enumerate(control):
        require(all(not ((label >> j) & 1) for j in range(7) if active[7+index, j]),
                'Relaxed fit respects all anchor constraints')
    return dict(profile=int(profiles[indices[0]]), anchors=anchors, variable_ports=variables,
        variable_edges=len(edges), initial_domain_sizes=[domain.bit_count() for domain in domains],
        result='UNSAT', **receipt, relaxed_control='SAT', known_nine_bit_control='PASS',
        cyclic_profile_witnesses=rotated,
        scope='Each profile has no arbitrary symmetric standard-dot binary labeling of dimension at most 8. This excludes three separate eight-bit profile labels, not a general 25-bit global fit.')
