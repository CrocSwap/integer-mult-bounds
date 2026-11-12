"""Literal prefix walk reused from the first bounded chart-602 gate."""
from collections import defaultdict
from time import monotonic

EVENTS = 76466


def sweep(word, cohort, selected, earlier, engine, deadline, progress, results):
    n, owned, tape = (word[k] for k in ("public", "owned_fields", "program"))
    assert (n, owned, len(tape)) == (1501, 68, EVENTS)
    assert all((word["initial"][r], word["final"][r]) == (602, 127) for r in cohort)
    frames = word["frames"]
    span = engine["span"]
    low, high = span(frames[602]), span(frames[127])
    assert len(low) == 4 and len(high) == 512 and low < high
    requests = defaultdict(list)
    for cut, chart in selected:
        assert 0 <= cut <= EVENTS and len(frames[chart]) in (5, 6) and low < span(frames[chart]) < high
        requests[cut].append(chart)

    active = word["initial"] + [None] * owned
    vectors = [{r: 1} for r in range(n)] + [None] * owned
    fresh, denoms = set(), set()
    progress.update(events=0, first_unvisited_cut=0)
    for cut in range(EVENTS + 1):
        progress["first_unvisited_cut"] = cut
        if (cut % 128 == 0 or cut in requests) and monotonic() >= deadline:
            break
        for chart in requests.get(cut, ()):
            key = cut, chart
            bank = [r for r in range(n) if active[r] == chart]
            owners = [r for r in range(n, n + owned) if active[r] == chart]
            pivots = sorted(set(bank) & cohort)
            assert pivots and bank == selected[key]["public"] and owners == selected[key]["owned"]
            assert pivots == selected[key]["pivots"]
            if cut:
                last = tape[cut - 1]
                assert chart in (last[2:4] if last[0] == "MOVE" else last[-1:])
            proof = engine["classify"](bank, vectors, cohort)
            primary_columns = earlier[key]["columns"]
            assert len(primary_columns) == len(set(primary_columns)) == len(bank)
            assert cohort.isdisjoint(primary_columns)
            determinant = engine["verify_minor"]([vectors[r] for r in bank], primary_columns)
            results[key] = dict(key=key, chart_rank=len(frames[chart]), public=bank, owned=owners, pivots=pivots,
                independent_minor=proof, primary_minor_axes=primary_columns,
                primary_minor_det_mod_65537=determinant,
                disposition="excluded" if not proof["kernel"] else "modular_rank_drop")
        if cut == EVENTS:
            assert active == word["final"] + [None] * owned and not fresh
            assert len(results) == len(selected)
            progress["first_unvisited_cut"] = None
            break
        engine["apply"](tape[cut], active, vectors, fresh, n, denoms, False)
        progress["events"] += 1
    progress["denominator_units"] = sorted(denoms)
