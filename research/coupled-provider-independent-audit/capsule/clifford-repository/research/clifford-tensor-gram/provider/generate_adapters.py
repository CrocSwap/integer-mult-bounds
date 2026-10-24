"""Propose main adapter recipes with the frozen source compiler.

The verifier checks these data with quadratic sums. It does not run this file.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(PACKAGE / "vendor"))
import clifford_exact as source
import provider


def generate():
    _, data = provider.read_inputs()
    model = provider.Provider(data["word"])
    rows = []
    for entrance in (True, False):
        for role in range(224):
            f = model.c["start" if entrance else "final"][role]
            old = model.old_frame(role, entrance)
            circuit = provider.inverse_circuit(9, old) + model.frame(f)
            # Tableau generation is part of proposal generation only.
            op = source.ident(9)
            for gate in circuit:
                kind = gate[0]
                if kind == "P":
                    part = source.perm(9, tuple(gate[1]))
                elif kind == "D":
                    part = source.diag(9, tuple(gate[1]), tuple(gate[2]))
                else:
                    provider.need(kind == "C", "Adapter generator gate")
                    part = source.cgate(9, gate[1], gate[2])
                op = op.then(part)
            recipe, _ = source.lower_child(op)
            provider.need(recipe["rank"] == 0, "Proposed main adapter is monomial")
            rows.append(dict(entrance=entrance, role=role, frame=f, recipe=recipe))
    return rows


if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "MAIN-ADAPTERS.json"
    target.write_text(json.dumps(generate(), sort_keys=True, separators=(",", ":")) + "\n")
    print("PROPOSED_448_MAIN_ADAPTERS_REQUIRES_GRAM_CHECK")
