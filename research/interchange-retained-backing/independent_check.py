"""Checker-only sparse execution of the retained local-symbol instruction word.

No geometry, capacity formula, assembler or source-machine module is imported.
Nonblank symbols, allocated prefix length and visited head span are separate
state: in particular a blank write allocates, while a read or move does not.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


class SparseMachine:
    """An independent interpreter with exact array-allocation observations.

    ``load_borrowed`` replaces only the supplied roles with encoded arrays and
    head 1. ``initialize_private`` sets initially blank backing and head 0.
    ``execute`` returns the same five counters/status as the canonical machine.
    ``snapshot`` reports cumulative head spans and allocation-event counters.
    """

    def __init__(self, code, entries, roles, blank=4):
        self.code, self.entries, self.blank = code, entries, blank
        self.roles = tuple(roles)
        require(len(set(self.roles)) == len(self.roles), "distinct roles")
        self.cells = {role: {} for role in self.roles}
        self.lengths = dict.fromkeys(self.roles, 0)
        self.heads = dict.fromkeys(self.roles, 0)
        self.spans = dict.fromkeys(self.roles, 1)
        self.growth_writes = dict.fromkeys(self.roles, 0)
        self.outside_reads = dict.fromkeys(self.roles, 0)
        self.outside_moves = dict.fromkeys(self.roles, 0)

    def initialize_private(self, lengths):
        for role, length in lengths.items():
            require(role in self.cells and type(length) is int and length >= 0,
                    "nonnegative initial private length")
            self.cells[role] = {}
            self.lengths[role], self.heads[role], self.spans[role] = length, 0, 1

    def load_borrowed(self, encoded, head=1):
        for role, values in encoded.items():
            require(role in self.cells, "known borrowed role")
            values = tuple(values)
            require(type(head) is int and head >= 0, "nonnegative borrowed head")
            self.cells[role] = {i: value for i, value in enumerate(values)
                                if value != self.blank}
            self.lengths[role] = len(values)
            self.heads[role], self.spans[role] = head, head + 1
            self.growth_writes[role] = 0
            self.outside_reads[role] = 0
            self.outside_moves[role] = 0

    def execute(self, entry, max_steps=1000000000):
        pc = self.entries[entry] if isinstance(entry, str) else entry
        counts = dict(steps=0, reads=0, writes=0, moves=0)
        while counts["steps"] < max_steps:
            require(type(pc) is int and 0 <= pc < len(self.code), "program counter")
            op, *args = self.code[pc]
            counts["steps"] += 1
            if op == "halt":
                return dict(status=args[0], **counts)
            if op == "jump":
                pc = args[0]
                continue
            role = args[0]
            require(role in self.cells, "instruction role")
            head = self.heads[role]
            self.spans[role] = max(self.spans[role], head + 1)
            if op == "test":
                _, symbol, yes, no = args
                if head >= self.lengths[role]:
                    self.outside_reads[role] += 1
                value = self.cells[role].get(head, self.blank)
                counts["reads"] += 1
                pc = yes if value == symbol else no
                continue
            if op == "write":
                symbol = args[1]
                if head >= self.lengths[role]:
                    self.lengths[role] = head + 1
                    self.growth_writes[role] += 1
                if symbol == self.blank:
                    self.cells[role].pop(head, None)
                else:
                    self.cells[role][head] = symbol
                counts["writes"] += 1
            elif op == "move":
                target = head + args[1]
                require(target >= 0, "left boundary")
                self.heads[role] = target
                self.spans[role] = max(self.spans[role], target + 1)
                if target >= self.lengths[role]:
                    self.outside_moves[role] += 1
                counts["moves"] += 1
            else:
                raise ValueError("unknown local instruction")
            pc += 1
        raise ValueError("independent observer watchdog")

    def compare_snapshot(self, tapes, heads, roles=None):
        """Compare all allocated cells, including erased retained tails."""
        for role in self.roles if roles is None else roles:
            require(self.lengths[role] == len(tapes[role]),
                    "retained length mismatch: " + role)
            require(self.heads[role] == heads[role], "head mismatch: " + role)
            require(all(self.cells[role].get(i, self.blank) == value
                        for i, value in enumerate(tapes[role])),
                    "allocated cell mismatch: " + role)
            require(all(0 <= i < self.lengths[role] for i in self.cells[role]),
                    "sparse cell outside backing: " + role)

    def snapshot(self, roles=None):
        chosen = self.roles if roles is None else tuple(roles)
        return {
            "lengths": {r: self.lengths[r] for r in chosen},
            "heads": {r: self.heads[r] for r in chosen},
            "visited_spans": {r: self.spans[r] for r in chosen},
            "growth_writes": {r: self.growth_writes[r] for r in chosen},
            "outside_reads": {r: self.outside_reads[r] for r in chosen},
            "outside_moves": {r: self.outside_moves[r] for r in chosen},
        }


def exercise_history(code, entries, canonical_execute, borrowed_calls, *,
                     private_roles, initial_lengths=None, endings=None,
                     max_steps=1000000000, output_role="OUTPUT",
                     observer_mutation=None):
    """Compare two executors after every entry of a bounded encoded history.

    ``borrowed_calls`` contains dictionaries role -> complete encoded array;
    it supplies no H/A/G/S geometry to this checker. ``endings`` optionally
    chooses consume/install per call. Returned snapshots include the complete
    OUTPUT backing at each returned cut, for a separate payload oracle.
    ``observer_mutation``, used only by the negative controls below, changes
    the independent accounting state before its canonical comparison.
    """
    calls = tuple(borrowed_calls)
    require(calls, "nonempty bounded history")
    borrowed = tuple(calls[0])
    private = tuple(private_roles)
    require(not set(borrowed) & set(private), "disjoint borrowed/private roles")
    require(all(set(call) == set(borrowed) for call in calls), "fixed borrowed roles")
    lengths = dict.fromkeys(private, 0)
    if initial_lengths is not None:
        require(set(initial_lengths) <= set(private), "private initial backing only")
        lengths.update(initial_lengths)
    require(all(type(n) is int and n >= 0 for n in lengths.values()),
            "nonnegative integer initial backing")
    endings = tuple(endings) if endings is not None else ("consume",) * len(calls)
    require(len(endings) == len(calls) and all(x in ("consume", "install") for x in endings),
            "one permitted disposal entry per call")
    roles = borrowed + private
    sparse = SparseMachine(code, entries, roles)
    sparse.initialize_private(lengths)
    tapes = {r: [sparse.blank] * lengths[r] for r in private}
    heads = dict.fromkeys(private, 0)
    snapshots = []

    def load(call):
        sparse.load_borrowed(call)
        for role, encoded in call.items():
            tapes[role], heads[role] = list(encoded), 1

    def run(entry, call_index):
        actual = canonical_execute(code, tapes, heads, entries[entry], max_steps=max_steps)
        independent = sparse.execute(entry, max_steps=max_steps)
        require(actual == independent, "independent action/status mismatch: " + entry)
        if observer_mutation is not None:
            observer_mutation(sparse, entry)
        sparse.compare_snapshot(tapes, heads)
        expected = {"init": "initialized", "run": "returned", "consume": "consumed",
                    "install": "installed", "close": "closed"}[entry]
        require(actual["status"] == expected, "successful source entry: " + entry)
        record = dict(entry=entry, call=call_index, actions=actual,
                      canonical_compared=True, **sparse.snapshot(private))
        if entry == "run":
            record["output_cells"] = list(tapes[output_role])
        snapshots.append(record)

    load(calls[0])
    run("init", None)
    for i, (call, ending) in enumerate(zip(calls, endings)):
        if i:
            load(call)
        run("run", i)
        run(ending, i)
    run("close", None)
    return snapshots


def run_checks(code, entries, canonical_execute, roles, private, borrowed,
               borrowed_calls, initial_lengths):
    """Root-verifier adapter; all geometries remain outside this module."""
    from hashlib import sha256
    import json

    require(set(roles) == set(private) | set(borrowed), "complete role inventory")
    require(all(set(call) == set(borrowed) for call in borrowed_calls),
            "complete encoded borrowed inputs")
    fresh = exercise_history(code, entries, canonical_execute, borrowed_calls,
                             private_roles=private)
    warm = exercise_history(code, entries, canonical_execute, borrowed_calls,
                            private_roles=private, initial_lengths=initial_lengths,
                            endings=["install"] * len(borrowed_calls))

    class AllocatingRead(dict):
        def __init__(self, values, owner, role):
            super().__init__(values)
            self.owner, self.role = owner, role

        def get(self, index, default=None):
            self.owner.lengths[self.role] = max(self.owner.lengths[self.role], index + 1)
            return super().get(index, default)

    def read_allocates(owner, entry):
        if entry == "init":
            for role in private:
                owner.cells[role] = AllocatingRead(owner.cells[role], owner, role)

    def erase_releases(owner, entry):
        if entry == "consume":
            for role in private:
                owner.lengths[role] = max(owner.cells[role], default=-1) + 1

    controls = {}
    for name, mutation in (("read_allocates", read_allocates),
                           ("erase_releases_backing", erase_releases)):
        try:
            exercise_history(code, entries, canonical_execute, borrowed_calls[:1],
                             private_roles=private, observer_mutation=mutation)
        except ValueError as error:
            require("retained length mismatch:" in str(error),
                    "accounting control rejected for its intended reason")
            controls[name] = str(error)
        else:
            raise ValueError("accounting mutant accepted: " + name)

    # Use one admitted role and the canonical instruction interpreter itself.
    # First read/move over implicit blanks; only the second entry writes one.
    role = private[0]
    probe_code = (("test", role, 4, 1, 6), ("move", role, 1),
                  ("test", role, 4, 3, 6), ("halt", "returned"),
                  ("write", role, 4), ("halt", "consumed"), ("halt", "rejected"))
    probe_entries = {"observe": 0, "write_blank": 4}
    probe = SparseMachine(probe_code, probe_entries, (role,))
    probe_tapes, probe_heads = {role: []}, {role: 0}
    probe_records = []
    for entry in ("observe", "write_blank"):
        before = len(probe_tapes[role])
        actual = canonical_execute(probe_code, probe_tapes, probe_heads, probe_entries[entry])
        independent = probe.execute(entry)
        require(actual == independent, "primitive action/status agreement")
        require(actual["status"] == ("returned" if entry == "observe" else "consumed"),
                "implicit blank probe accepted")
        probe.compare_snapshot(probe_tapes, probe_heads)
        probe_records.append(dict(entry=entry, before_length=before,
                                  after_length=len(probe_tapes[role]),
                                  visited_span=probe.spans[role], actions=actual))
    require(probe_records[0]["after_length"] == 0 and
            probe_records[1]["before_length"] == 0 and
            probe_records[1]["after_length"] == 2 and
            probe_tapes[role] == [4, 4],
            "implicit reads/moves preserve backing; blank write allocates")

    def serialized(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

    def compact(records):
        answer = []
        for record in records:
            summary = {key: record[key] for key in
                       ("entry", "call", "actions", "lengths", "canonical_compared")}
            summary["complete_snapshot_sha256"] = sha256(serialized(record)).hexdigest()
            for source, target in (("visited_spans", "visited_span_total"),
                                   ("growth_writes", "growth_writes_total"),
                                   ("outside_reads", "outside_reads_total"),
                                   ("outside_moves", "outside_moves_total")):
                summary[target] = sum(record[source].values())
            if "output_cells" in record:
                summary["output_backing_sha256"] = sha256(bytes(record["output_cells"])).hexdigest()
            answer.append(summary)
        return answer

    result = {"fresh": compact(fresh), "warm_install": compact(warm), "controls": controls,
              "primitive_allocation_probe": {"role": role, "entries": probe_records}}
    result["receipt_sha256"] = sha256(serialized(result)).hexdigest()
    return result
