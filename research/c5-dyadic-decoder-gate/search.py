"""Complete integer search in one finite E8 menu; not a theorem about all decoders."""
from algebra import roots_e8


def exclude(costs, anchor, cap=19):
    roots = roots_e8()
    supports = [tuple(i for i, x in enumerate(r) if x) for r in roots]
    orthogonal = [sum(1 << j for j, v in enumerate(roots)
                      if sum(x*y for x, y in zip(u, v)) == 0) for u in roots]
    # Plane orthogonality is exactly the cycle edges; same-plane ports are constrained.
    neighbors = [sum(1 << j for j in range(10) if i != j and
                     ((i//2 - j//2) % 5 not in (1, 4))) for i in range(10)]
    nodes = prunes = 0

    def visit(domains, masks, todo, current_cost):
        nonlocal nodes, prunes
        nodes += 1
        if not todo:
            return []
        best, slot = 121, -1
        domains = list(domains)
        for i in range(10):
            if not (todo >> i & 1):
                continue
            keep, domain, plane = 0, domains[i], 1 << (i//2)
            while domain:
                bit = domain & -domain
                r = bit.bit_length() - 1
                domain -= bit
                delta = sum(costs[masks[k] | plane] - costs[masks[k]] for k in supports[r])
                if current_cost + delta <= cap:
                    keep |= bit
            domains[i] = keep
            count = keep.bit_count()
            if not count:
                prunes += 1
                return None
            if count < best:
                slot, best = i, count
        domain, plane = domains[slot], 1 << (slot//2)
        while domain:
            bit = domain & -domain
            r = bit.bit_length() - 1
            domain -= bit
            child, new_masks = list(domains), list(masks)
            for k in supports[r]:
                new_masks[k] |= plane
            remaining, ok = todo & ~(1 << slot), True
            for j in range(10):
                if not (remaining >> j & 1):
                    continue
                if neighbors[slot] >> j & 1:
                    child[j] &= orthogonal[r]
                if j == (slot ^ 1):
                    child[j] &= (~((1 << (r+1))-1) if slot % 2 == 0 else (1 << r)-1)
                if not child[j]:
                    ok = False
                    break
            if ok:
                witness = visit(child, new_masks, remaining, sum(costs[m] for m in new_masks))
                if witness is not None:
                    return [(slot, r)] + witness
        return None

    domains = [(1 << 120)-1] * 10
    domains[0] = 1 << anchor
    witness = visit(domains, [0]*8, 1023, 0)
    return {'anchor': anchor, 'cap': cap, 'found': witness is not None,
            'nodes': nodes, 'prunes': prunes, 'witness': witness}
