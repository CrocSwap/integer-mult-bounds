"""Every source chart and inverse, with exact independent matrix semantics."""
from fractions import Fraction as F
from hashlib import sha256
import json
from unittest.mock import patch
from collections import Counter

import bindings
from frames import price, inverse, need, optimize_registry, setup_coefficient
from check_algebra import equal


def run():
    _source, retained, data = bindings.activate()
    names = (retained.GEOMETRY, retained.TEMPLATE, retained.GLOBAL,
             retained.WORD, retained.EXPECTED, retained.ASSEMBLY)
    routes, source_receipt = retained.compile_catalog({n:data[n] for n in names})
    from catalogue import Catalogue
    from compile_routes import selected_registry, matrix_key
    catalogue = Catalogue(3)
    # Same bounded cache treatment as main's PR2915 catalogue check.
    matrix = type(catalogue).chart_matrix.__wrapped__
    with patch.object(catalogue, "chart_matrix", lambda chart: matrix(catalogue, chart)):
        registry, binding_receipt = selected_registry(catalogue)
    optimized = optimize_registry(registry)
    from routes import Route
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    low_digest = sha256()
    def direct_bill(operations):
        return Counter((op[0], op[3] if op[0] == "add" else op[2] if op[0] == "translate" else None)
                       for op in operations if op[0] != "swap")
    for chart in sorted(registry.words, key=repr):
        target = tuple(tuple(v.numerator*pow(v.denominator,-1,3) % 3 for v in row)
                       for row in chart)
        route = Route(3,64,identity,target,chart)
        original_ops = registry.compile(route)
        scheduled_ops = optimized.compile(route)
        need(direct_bill(original_ops) == direct_bill(scheduled_ops),
             "complete specialized scalar/carry bill")
        for ops, word in ((original_ops,registry.words[chart]),
                          (scheduled_ops,optimized.words[chart])):
            observed_calls = sum(1 if op[0] == "swap" else
                                 2 if op[0] == "add" and op[2] > op[1] else 0 for op in ops)
            need(observed_calls == 64*price(word), "actual compiled native-call bill")
        low_digest.update(json.dumps(scheduled_ops,separators=(",", ":")).encode())
        registry.compiled.clear()
        optimized.compiled.clear()
    totals = {f:dict(types=0, occurrences=0, before=0, after=0, improved=0)
              for f in ("data", "hosted")}
    entries = []
    digest = sha256()
    for key, row in sorted(routes.items()):
        source_word = tuple((k,t,c,F(v)) for k,t,c,v in row["word"])
        key_matrix = matrix_key(retained.replay(source_word, 64))
        inverse_matrix = matrix_key(retained.replay(inverse(source_word), 64))
        word = registry.words[key_matrix]
        inverse_word = registry.words[inverse_matrix]
        chosen = optimized.words[key_matrix]
        chosen_inverse = optimized.words[inverse_matrix]
        need(equal(word, chosen, 64), "independent exact chart: " + key)
        need(equal(inverse_word, chosen_inverse, 64), "independent inverse chart: " + key)
        before, after = 64*price(word), 64*price(chosen)
        before_inverse, after_inverse = 64*price(inverse_word), 64*price(chosen_inverse)
        need(64*price(source_word) == row["bill"]["ordinary"], "retained physical row count")
        family = "data" if row["family"] == "data" else "hosted"
        total = totals[family]
        total["types"] += 1
        total["occurrences"] += row["occurrences"]
        total["before"] += (before+before_inverse)*row["occurrences"]
        total["after"] += (after+after_inverse)*row["occurrences"]
        total["improved"] += before+before_inverse > after+after_inverse
        encoded = [(k,t,c,str(v)) for k,t,c,v in chosen]
        inverse_encoded = [(k,t,c,str(v)) for k,t,c,v in chosen_inverse]
        digest.update(json.dumps([key, encoded, inverse_encoded], separators=(",", ":")).encode())
        deltas = [64*(sum(k == "swap" for k,t,c,v in new)-
                      sum(k == "swap" for k,t,c,v in old))
                  for old,new in ((word,chosen),(inverse_word,chosen_inverse))]
        beta = setup_coefficient(64)
        setup_and_adapter_delta = [beta*ds + 100000*(a-b)
                                   for ds,a,b in zip(deltas,[after,after_inverse],
                                                    [before,before_inverse])]
        need(all(delta <= 0 for delta in setup_and_adapter_delta),
             "every oriented chart retains its complete paid bound")
        entries.append(dict(key=key, occurrences=row["occurrences"],
                            before_per_row=[before//64,before_inverse//64],
                            after_per_row=[after//64,after_inverse//64],
                            original_catalogue_per_row=price(source_word),
                            delta_high_operations=deltas,
                            setup_and_adapter_delta_per_V=setup_and_adapter_delta))
    before = sum(t["before"] for t in totals.values())
    after = sum(t["after"] for t in totals.values())
    raw_before = 2*(source_receipt["data_occurrence_total"]["ordinary"] +
                    source_receipt["hosted_occurrence_total"]["ordinary"])
    need(before <= raw_before, "registry baseline improves or retains raw catalogue")
    need(after < before, "strict selected-catalogue improvement")
    return dict(types=len(routes), registry_matrices=len(registry.words),
                bound_source_types=binding_receipt["source_types"],
                raw_catalogue_before=raw_before,
                low_carry_checks=len(registry.words), low_carry_sha256=low_digest.hexdigest(),
                oriented_checks=2*len(routes), totals=totals,
                weighted_before=before, weighted_after=after,
                saved=before-after, reduction=str(F(before-after,before)),
                selected_word_sha256=digest.hexdigest(), entries=entries,
                source_catalogue_sha256=source_receipt["catalogue_sha256"])
