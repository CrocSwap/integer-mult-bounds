"""Construct well-conditioned counterexamples for dirty linear programs.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged compiler in vendor is prepared for zxv; see NOTICE.md.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from linear_words import Span, compile_problem, digest, need


def top_coefficient(problem):
    """Keep a separate reachable space for each exact word length."""
    need(problem.get('field', 'Q') in ('Q', 'Qi'), 'ordered witness requires Q or Qi')
    machine = compile_problem(problem)
    alphabet = sorted(machine.edges)
    candidates = [(row, output, []) for output, row in enumerate(machine.initial)]
    last = None
    widths = []
    for degree in range(machine.states):
        span = Span()
        paths = []
        for row, output, word in candidates:
            if span.insert(row):
                paths.append((output, word))
                terminal = machine.terminal(row)
                if terminal:
                    source = min(terminal)
                    last = {'output': output, 'input': source, 'word': word,
                            'coefficient': str(terminal[source])}
        widths.append(len(paths))
        if not paths:
            break
        candidates = [(machine.step(row, symbol), output, word + [symbol])
                      for row, (output, word) in zip(span.rows, paths)
                      for symbol in alphabet]
    need(all(not row for row, _, _ in candidates) or widths[-1] == 0,
         'coefficient machine is not acyclic')
    return last, {'states': machine.states, 'layer_dimensions': widths,
                  'alphabet': alphabet}


def produce(problem, epsilon=Q(1, 4)):
    epsilon = Q(epsilon)
    need(0 < epsilon <= Q(1, 4), 'epsilon must be in (0,1/4]')
    top, stats = top_coefficient(problem)
    result = {'schema': 'spd-dirty-witness/v1', 'problem_sha256': digest(problem),
              'equivalent': top is None, 'statistics': stats}
    if top is not None:
        result.update(top)
        result.update({'epsilon': str(epsilon), 'dimension': len(top['word']) + 1,
                       'spectral_interval': [str(1-2*epsilon), '1']})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem', type=Path)
    parser.add_argument('--epsilon', default='1/4')
    args = parser.parse_args()
    print(json.dumps(produce(json.loads(args.problem.read_text()), Q(args.epsilon)), indent=2))


if __name__ == '__main__':
    main()
