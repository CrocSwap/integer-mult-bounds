"""Deletion-free reverse-unit-propagation checker. No SAT solver. Apache-2.0."""
from encoding import require


class RupChecker:
    """Keep two watched literals per nonunit clause; reset assignments per check."""

    def __init__(self, clauses, variables):
        require(type(variables) is int and 1 <= variables <= 10000, "RUP variables")
        require(len(clauses) <= 20000, "RUP input capacity")
        self.variables = variables
        self.clauses = []
        self.watches = {}
        self.units = []
        self.empty = False
        for clause in clauses:
            self.add(clause)

    def validate(self, clause):
        require(len(clause) <= self.variables, "clause length")
        require(all(type(z) is int and 0 < abs(z) <= self.variables for z in clause),
                "literal range")

    def add(self, clause):
        self.validate(clause)
        require(len(self.clauses) + len(self.units) < 25000, "RUP clause capacity")
        clause = list(dict.fromkeys(clause))
        if any(-z in clause for z in clause):
            return  # A tautology cannot propagate.
        if not clause:
            self.empty = True
        elif len(clause) == 1:
            self.units.append(clause[0])
        else:
            index = len(self.clauses)
            self.clauses.append(clause)
            for literal in clause[:2]:
                self.watches.setdefault(literal, []).append(index)

    def propagate_false_watch(self, literal, assigned, queue):
        """Return True on conflict. Every original watcher is visited once."""
        watched = self.watches.get(-literal, [])
        index = 0
        for _ in range(len(watched)):
            clause_id = watched[index]
            clause = self.clauses[clause_id]
            if clause[0] == -literal:
                clause[0], clause[1] = clause[1], clause[0]
            require(clause[1] == -literal, "watch invariant")
            if clause[0] in assigned:
                index += 1
                continue
            replacement = next((k for k in range(2, len(clause))
                                if -clause[k] not in assigned), None)
            if replacement is not None:
                clause[1], clause[replacement] = clause[replacement], clause[1]
                self.watches.setdefault(clause[1], []).append(clause_id)
                watched[index] = watched[-1]
                watched.pop()
            else:
                if -clause[0] in assigned:
                    return True
                queue.append(clause[0])
                index += 1
        return False

    def is_rup(self, clause):
        self.validate(clause)
        if self.empty:
            return True
        queue = self.units + [-z for z in clause]
        # Each nonunit clause can become unit at most once in a propagation.
        bound = len(queue) + 2*len(self.clauses)
        assigned = set()
        for position in range(bound+1):
            require(len(queue) <= bound, "propagation capacity")
            if position == len(queue):
                return False
            literal = queue[position]
            if -literal in assigned:
                return True
            if literal not in assigned:
                assigned.add(literal)
                if self.propagate_false_watch(literal, assigned, queue):
                    return True
        raise ValueError("propagation iteration bound")


def parse_proof(raw, variables):
    require(len(raw) <= 1000000, "proof byte capacity")
    lines = raw.decode("ascii").splitlines()
    require(1 <= len(lines) <= 5000, "proof step capacity")
    proof = []
    for line in lines:
        tokens = line.split()
        require(1 <= len(tokens) <= 129, "proof clause capacity")
        values = [int(token) for token in tokens]
        require(values[-1] == 0 and 0 not in values[:-1], "proof terminator")
        clause = values[:-1]
        require(all(abs(z) <= variables for z in clause), "proof literal range")
        proof.append(clause)
    require(proof[-1] == [] and all(proof[:-1]), "terminal empty clause")
    return proof


def check_refutation(formula, raw):
    proof = parse_proof(raw, formula.variables)
    checker = RupChecker(formula.clauses, formula.variables)
    for index, clause in enumerate(proof):
        require(checker.is_rup(clause), f"non-RUP step {index+1}")
        checker.add(clause)
    require(checker.empty, "missing contradiction")
    return len(proof)
