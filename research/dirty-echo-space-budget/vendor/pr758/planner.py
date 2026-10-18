"""Exact planning within sequential multiway dirty-echo trees.

Koroffstrogov with substantial OpenAI Codex assistance. Apache-2.0.
The echo identity is PR673's; the balanced ternary comparator is PR689's.
This module optimizes contiguous partitions and arities at a fixed space cap.
It does not optimize arbitrary reversible programs. See PROOF.md.
"""

from functools import lru_cache


def need(condition, message):
    if not condition:
        raise ValueError(message)


def invoice(tree, weights):
    """Independently traverse a literal tree; return price, calls, peak, counts."""
    weights = tuple(weights)
    need(weights and all(type(w) is int and w > 0 for w in weights),
         "positive integer leaf weights")

    def walk(node):
        if type(node) is int:
            need(0 <= node < len(weights), "leaf index")
            return [node], 0, {node: 1}
        need(type(node) in (tuple, list) and len(node) >= 2, "tree arity")
        leaves, peak, counts = [], 0, {}
        for j, child in enumerate(node):
            indices, space, occurrences = walk(child)
            leaves.extend(indices)
            peak = max(peak, space)
            multiplier = 2 if j in (0, len(node)-1) else 4
            for i, count in occurrences.items():
                counts[i] = counts.get(i, 0) + multiplier * count
        return leaves, len(node)-1+peak, counts

    leaves, space, counts = walk(tree)
    need(leaves == list(range(len(weights))), "ordered complete factor list")
    profile = [counts[i] for i in range(len(weights))]
    return dict(price=sum(w*c for w, c in zip(weights, profile)),
                calls=sum(profile), scratch=space, occurrences=profile)


def optimize(weights, budget):
    """Return a minimum-price tree, then minimum calls among price ties.

    Leaves are ordered and cannot be deleted/reordered. Each k-child node
    reserves k-1 arrays during every child call; the children share a deeper
    pool sequentially. Infeasibility means only this explicit tree class.
    """
    weights = tuple(weights)
    need(weights and all(type(w) is int and w > 0 for w in weights),
         "positive integer leaf weights")
    need(type(budget) is int and budget >= 0, "nonnegative integer space cap")
    budget = min(budget, len(weights)-1)

    @lru_cache(maxsize=None)
    def best(lo, hi, space):
        if hi-lo == 1:
            return weights[lo], 1, lo
        if space == 0 or hi-lo > 2**space:
            return None
        winner = None
        for arity in range(2, min(space+1, hi-lo)+1):
            remaining = space-arity+1
            # Partition DP: j complete consecutive children ending at a cut.
            states = {lo: (0, 0, ())}
            for j in range(arity):
                next_states = {}
                multiplier = 2 if j in (0, arity-1) else 4
                for cut, (cost, calls, children) in states.items():
                    stop = min(hi-(arity-j-1), cut+2**remaining)
                    for end in range(cut+1, stop+1):
                        child = best(cut, end, remaining)
                        if child is None:
                            continue
                        candidate = (cost+multiplier*child[0],
                                     calls+multiplier*child[1], children+(child[2],))
                        old = next_states.get(end)
                        if old is None or candidate[:2] < old[:2]:
                            next_states[end] = candidate
                states = next_states
            candidate = states.get(hi)
            if candidate is not None and (winner is None or candidate[:2] < winner[:2]):
                winner = candidate
        return winner

    answer = best(0, len(weights), budget)
    need(answer is not None, "no tree fits space cap")
    result = invoice(answer[2], weights)
    need((result['price'], result['calls']) == answer[:2], "planner invoice")
    need(result['scratch'] <= budget, "planner space")
    return dict(tree=answer[2], **result)


def word(tree, sign=1):
    """Stream (factor, source, target, sign), with source 0 and target 1."""
    need(type(sign) is int and sign in (-1, 1), "sign")

    def leaf_count(node):
        if type(node) is int:
            return 1
        need(type(node) in (tuple, list) and len(node) >= 2, "tree arity")
        return sum(leaf_count(c) for c in node)

    invoice(tree, [1]*leaf_count(tree))

    def emit(node, source, target, first_scratch, direction):
        if type(node) is int:
            yield node, source, target, direction
            return
        k = len(node)
        chain = [(node[j], source if j == 0 else first_scratch+j-1,
                  first_scratch+j, 1) for j in range(k-1)]
        last = (node[-1], first_scratch+k-2, target, 1)

        def inverse(commands):
            return [(t, s, d, -q) for t, s, d, q in reversed(commands)]

        commands = chain+[last]+inverse(chain)+chain[1:]+inverse([last])+inverse(chain[1:])
        if direction == -1:
            commands = inverse(commands)
        for child, src, dst, child_sign in commands:
            yield from emit(child, src, dst, first_scratch+k-1, child_sign)

    yield from emit(tree, 0, 1, 2, sign)


def compose(tree, source, target, factors, scratch, leaf, sign=1, read_only=()):
    """Execute with a deterministic source-restoring additive leaf callback.

    leaf(source, target, factor, sign) must obey PROOF.md's contract. Ordinary
    list identity aliases are checked before mutation, including declared
    read-only arrays. Overlapping views/hidden callback state are not supported.
    """
    bill = invoice(tree, [1]*len(factors))
    need(type(sign) is int and sign in (-1, 1), "sign")
    need(len(scratch) >= bill['scratch'], "insufficient scratch")
    arrays = [source, target, *scratch]
    need(len({id(a) for a in arrays}) == len(arrays), "mutable arrays alias")
    need(not any(ro is a for ro in read_only for a in arrays), "read-only alias")
    need(len(source) > 0 and all(len(a) == len(source) for a in arrays),
         "equal positive array lengths")
    for factor, src, dst, direction in word(tree, sign):
        leaf(arrays[src], arrays[dst], factors[factor], direction)
