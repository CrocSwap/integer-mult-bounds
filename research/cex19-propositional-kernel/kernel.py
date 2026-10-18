"""Pinned CNF binding and explicit propositional proof generation.

Prepared for ywz65 with OpenAI Codex assistance; Apache-2.0.
The predecessor encoder is a comparison subject, not an independent encoding.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticated(directory=HERE):
    pins = json.loads((directory / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in pins['external_sources']:
        raw = (directory / row['local_path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source drift: ' + row['local_path'])
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source blob: ' + row['local_path'])
    # Execute authenticated bytes, without accepting a cached .pyc.
    raw = (directory / 'source/encoding.py').read_bytes()
    env = {'__name__': 'pinned_cex19_encoding'}
    exec(compile(raw, 'pinned_cex19_encoding.py', 'exec'), env)
    config = json.loads((directory / 'source/configuration.json').read_text())
    formula, _, _ = env['build'](config)
    expected = json.loads((directory / 'source/RESULT.json').read_text())['lower']
    require(hashlib.sha256(formula.dimacs().encode()).hexdigest() == expected['cnf_sha256'],
            'original complete CNF digest')
    require(formula.variables == 2856 and len(formula.clauses) == 9964, 'original dimensions')
    require((directory / 'lower.cnf').read_text() == formula.dimacs(), 'literal CNF binding')
    proof = [list(map(int, line.split())) for line in
             (directory / 'source/lower.rup').read_text().splitlines()]
    require(len(proof) == 1301 and all(p and p[-1] == 0 and 0 not in p[:-1] for p in proof),
            'original proof structure')
    return formula.clauses, [p[:-1] for p in proof]


def check_trace(clauses, proof, actions):
    """Check every antecedent locally; no watched literals or SAT solver."""
    require(len(actions) == len(proof), 'trace length')
    database = [list(c) for c in clauses]
    for offset, (record, expected) in enumerate(zip(actions, proof)):
        index, clause, hints = record
        require(index == len(clauses) + offset + 1 and clause == expected, 'proof binding')
        require(hints and all(type(h) is int and 1 <= h < index for h in hints), 'hint range')
        assigned = {-x for x in clause}
        require(not any(-x in assigned for x in assigned), 'tautological addition')
        conflict = False
        for position, hint in enumerate(hints):
            source = database[hint - 1]
            require(not any(x in assigned for x in source), 'satisfied hint')
            remaining = [x for x in source if -x not in assigned]
            require(len(remaining) <= 1, 'nonunit hint')
            if not remaining:
                require(position == len(hints) - 1, 'trailing hints')
                conflict = True
            else:
                assigned.add(remaining[0])
        require(conflict, 'missing conflict')
        database.append(clause)
    require(proof[-1] == [], 'terminal empty clause')


def core(actions, input_count):
    table = {row[0]: row for row in actions}
    needed = {actions[-1][0]}
    pending = list(needed)
    while pending:
        index = pending.pop()
        if index in table:
            for parent in table[index][2]:
                if parent not in needed:
                    needed.add(parent)
                    pending.append(parent)
    return sorted(i for i in needed if i <= input_count), needed


def literal(value):
    return '(v ' + str(value) + ')' if value > 0 else '(Not (v ' + str(-value) + '))'


def proposition(clause):
    return '(' + ' ∨ '.join([*(literal(x) for x in clause), 'False']) + ')'


def resolve(clause, assigned, target, position, term):
    if position == len(clause):
        return 'False.elim (' + term + ')'
    x = clause[position]
    if x == target:
        branch = 'hx'
    else:
        contradiction = (assigned[-x] + ' hx') if x > 0 else ('hx ' + assigned[-x])
        branch = 'False.elim (' + contradiction + ')'
    return ('Or.elim (' + term + ') (fun hx => ' + branch + ') (fun hr => ' +
            resolve(clause, assigned, target, position + 1, 'hr') + ')')


def render(clauses, actions, first_only=False):
    """Untrusted generator: every output derivation must typecheck in Lean."""
    if first_only:
        actions = actions[:1]
    original, needed = core(actions, len(clauses))
    database = {i + 1: c for i, c in enumerate(clauses)}
    lines = ['import Std', 'set_option maxRecDepth 100000', 'set_option maxHeartbeats 0',
             'namespace Cex19Core', 'structure Satisfies (v : Nat → Prop) : Prop where',
             '\n'.join('  c' + str(i) + ' : ' + proposition(database[i]) for i in original), '']
    for index, clause, hints in actions:
        database[index] = clause
        if index not in needed:
            continue
        lines += ['theorem s' + str(index) + ' (v : Nat → Prop) (H : Satisfies v) : ' +
                  proposition(clause) + ' := by', '  classical',
                  '  apply Classical.byContradiction', '  intro hc']
        assigned = {}
        counter = 0
        for position, x in enumerate(clause):
            name = 'a' + str(counter)
            counter += 1
            injection = 'Or.inl hx'
            for _ in range(position):
                injection = 'Or.inr (' + injection + ')'
            term = '(fun hx => hc (' + injection + '))'
            if x < 0:
                term = 'Classical.byContradiction ' + term
            lines.append('  have ' + name + ' : ' + literal(-x) + ' := ' + term)
            assigned[-x] = name
        for hint in hints:
            source_clause = database[hint]
            remaining = [x for x in source_clause if -x not in assigned]
            require(len(remaining) <= 1 and not any(x in assigned for x in source_clause), 'render hint')
            target = remaining[0] if remaining else None
            source = 'H.c' + str(hint) if hint <= len(clauses) else 's' + str(hint) + ' v H'
            term = resolve(source_clause, assigned, target, 0, source)
            if target is None:
                lines.append('  exact ' + term)
                break
            name = 'a' + str(counter)
            counter += 1
            lines.append('  have ' + name + ' : ' + literal(target) + ' := ' + term)
            assigned[target] = name
    if first_only:
        lines += ['#print axioms s' + str(actions[0][0])]
    else:
        lines += ['theorem core_unsat (v : Nat → Prop) : ¬ Satisfies v := by',
                  '  intro H', '  exact s' + str(actions[-1][0]) + ' v H',
                  '#print axioms core_unsat']
    lines += ['end Cex19Core', '']
    return '\n'.join(lines)


def evidence(directory=HERE):
    clauses, proof = authenticated(directory)
    actions = json.loads((directory / 'trace.json').read_text())
    check_trace(clauses, proof, actions)
    original, needed = core(actions, len(clauses))
    generated = render(clauses, actions)
    require((directory / 'Certificate.lean').read_text(encoding='utf-8') == generated, 'Lean source binding')
    result = {'input_variables': 2856, 'input_clauses': len(clauses), 'original_additions': len(proof),
              'core_input_clauses': len(original), 'core_additions': len(needed) - len(original),
              'core_antecedents': sum(len(h) for i, c, h in actions if i in needed),
              'core_original_clause_ids': original,
              'lean_sha256': hashlib.sha256(generated.encode()).hexdigest()}
    require((len(original), result['core_additions'], result['core_antecedents']) == (2675, 602, 25711),
            'core counts')
    return result, clauses, proof, actions
