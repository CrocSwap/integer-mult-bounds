"""Apply a finite difference to a scalar circuit. Compare each old value first."""

from fractions import Fraction

from network import need


def replace_entries(entries, changes):
    """Check each old route or coefficient and install its new value."""
    result = entries.copy()
    keys = [key for key, _, _ in changes]
    need(keys == sorted(set(keys)), "unique ordered edits")
    for key, before, after in changes:
        need(result.get(key) == before and before != after, "edit preimage")
        if after is None:
            del result[key]
        else:
            result[key] = after
    return result


def restore_relays(net, patch):
    """Apply the published paid moves and their local scalar changes."""
    routes = {k: list(pair) for k, pair in net.moves.items()}
    rows = net.forms.copy()
    for key, old in patch["deleted_moves"]:
        need(routes.pop(key) == old, "removed relay route")
        del rows[key]
    for key, old, new in patch.get("relocated_hub_moves", []) + patch.get("rerouted_moves", []):
        need(routes[key] == old, "changed relay route")
        routes[key] = new
    for key, route, terms in patch.get("added_moves", []):
        need(key not in routes, "fresh relay sender")
        routes[key] = route
        rows[key] = {i: Fraction(q) for i, q in terms}
    for key, edits in patch["scalar_form_changes"]:
        old = {i: str(q) for i, q in rows[key].items()}
        rows[key] = {i: Fraction(q) for i, q in replace_entries(old, edits).items()}
    return type(net)(net.first_output, net.initial, net.final, {k: tuple(v) for k, v in routes.items()}, rows)


def rename_senders(net, names):
    """Allocate disjoint private sender numbers for the two journals."""
    need(set(names) <= net.moves.keys() and set(names.values()).isdisjoint(net.forms), "sender allocation")
    need(len(names) == len(set(names.values())) and all(0 <= j < net.first_output for j in names.values()),
         "distinct private labels")
    def key(i):
        return names.get(i, i)
    routes = {key(i): pair for i, pair in net.moves.items()}
    rows = {key(i): {key(j): q for j, q in terms.items()} for i, terms in net.forms.items()}
    return type(net)(net.first_output, net.initial, net.final, routes, rows)


def apply(net, stage):
    """Apply paid route and scalar changes at the given public interface."""
    moves = replace_entries({k: list(route) for k, route in net.moves.items()}, stage["routes"])
    rows = net.forms.copy()
    seen = set()
    for key, changes in stage["rows"]:
        need(key not in seen, "duplicate scalar row edit")
        seen.add(key)
        old = {j: str(q) for j, q in rows.get(key, {}).items()}
        new = replace_entries(old, changes)
        if key not in moves and key < net.first_output:
            need(key in rows and not new, "deleted scalar sender")
            del rows[key]
        else:
            row = {j: Fraction(v) for j, v in new.items()}
            need(all(q and str(q) == new[j] for j, q in row.items()), "canonical rational coefficients")
            rows[key] = row
    n = len(net.initial)
    need(set(rows) == moves.keys() | set(range(net.first_output, net.first_output + n)), "complete scalar graph")
    return type(net)(net.first_output, net.initial, net.final, {k: tuple(v) for k, v in moves.items()}, rows)
