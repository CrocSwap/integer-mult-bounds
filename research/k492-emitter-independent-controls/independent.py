"""Exact, standalone structural checker for the eight K492 emitter R/R0 sites.

No repository implementation is imported. Inputs are the retained source words,
programs, literal owner allocation, data phases, and parent template. This is
not a scalar/Clifford replay or an invoice/assembly checker.

Prepared with substantial OpenAI Codex (GPT-6 Astra) assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path


class Rejected(ValueError):
    def __init__(self, obligation, detail):
        self.obligation = obligation
        self.detail = detail
        super().__init__(f"{obligation}: {detail}")


def require(condition, obligation, detail):
    if not condition:
        raise Rejected(obligation, detail)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)


def rank(vectors):
    """Binary Gaussian elimination; no floating point or repository rank helper."""
    pivots = {}
    for item in vectors:
        require(type(item) is int and 0 <= item < 512,
                "frame.vector", str(item))
        value = item
        while value:
            k = value.bit_length() - 1
            if k not in pivots:
                pivots[k] = value
                break
            value ^= pivots[k]
    return len(pivots)


@lru_cache(maxsize=None)
def chart(port_vector):
    """Matrix columns of x -> x + <x,u>u, followed by the declared pivot swap.

    u=q+e_z has even weight, so the transvection is orthogonal over F2.
    Verify its entire Gram matrix independently rather than trusting this fact.
    """
    z = next(j for j in range(9) if not (port_vector >> j) & 1)
    u = port_vector ^ (1 << z)
    columns = [((1 << j) ^ (u if (u >> j) & 1 else 0)) for j in range(73)]
    columns[0], columns[z] = columns[z], columns[0]
    require(all((x & y).bit_count() % 2 == (i == j)
                for i, x in enumerate(columns) for j, y in enumerate(columns)),
            "chart.orthogonality", str(port_vector))
    return tuple(columns)


class Reconstruction:
    def __init__(self, fixture):
        self.root = Path(fixture)
        self.base = self.root / "base"
        self.plan = read(self.root / "PLAN.json")
        self.allocation = read(self.root / "OWNERS.json.gz")
        self.spec = read(self.root / "SPEC.json")
        self.parent = read(self.base / "split-centres/GLOBAL-TEMPLATE.json.gz")
        self.parent_word = read(self.base / "split-centres/CANONICAL-WORD.json.gz")
        self.phases = read(self.base / "work/complex-nine-native/DATA-PHASES.json")
        self.words, self.widths, self.programs, self.checks = {}, {}, {}, {}
        self.source_hashes = {}
        for file in sorted(self.base.rglob("*")):
            if file.is_file():
                self.source_hashes[file.relative_to(self.base).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
        for pid in sorted(self.plan["provider_registry"]):
            directory = self.base / "providers" / pid
            word = read(directory / "CANONICAL-WORD.json.gz")
            self.words[pid] = word
            require((word["v"], word["h"], len(word["centers"])) == (112, 9, 8),
                    "provider.geometry", pid)
            require(type(word["R"]) is int and word["R"] > 0,
                    "provider.R", pid)
            n = 2 * word["v"] + word["R"]
            require(len(word["start"]) == len(word["final"]) == n,
                    "provider.columns", pid)
            widths = []
            for h in range(word["R"]):
                entrance = word["frames"][word["start"][224 + h]]
                terminal = word["frames"][word["final"][224 + h]]
                a, b = rank(entrance), rank(terminal)
                require(a == len(entrance) and b == len(terminal)
                        and rank(entrance + terminal) == b,
                        "provider.nested_independent_frames", f"{pid}:{h}")
                require(0 < b - a <= 9, "provider.width", f"{pid}:{h}")
                widths.append(b - a)
            self.widths[pid] = widths
            require(widths == self.plan["provider_registry"][pid]["widths"],
                    "plan.widths", pid)
            self.programs[pid] = read(directory / "LOCAL-PROGRAMS.json.gz")
            self.checks[pid] = read(directory / "LOCAL-CHECKS.json")
            for orientation, events in self.programs[pid].items():
                literal = dict(sorted(Counter(e[-1] for e in events if e[0] in ("climb", "center")).items()))
                claimed = {int(k): v for k, v in self.checks[pid][orientation]["paid_profile"].items()}
                require(literal == claimed, "provider.literal_profile", f"{pid}:{orientation}")
                require(digest(events) == self.checks[pid][orientation]["sha256"],
                        "provider.program_digest", f"{pid}:{orientation}")
        counts = {w["R"] for w in self.words.values()}
        require(len(counts) == 1, "provider.common_R", str(counts))
        self.R = counts.pop()
        self.v = self.parent_word["v"]
        self.R0 = self.parent_word["R"]
        self.live = 8 * 8 * self.v
        self.centers = len(self.parent_word["centers"])
        require((self.v, self.parent_word["h"], self.R0, self.centers) == (112, 9, 504, 8),
                "parent.geometry", "fixed parent must remain the retained 504-helper template")
        require((self.parent["live"], self.parent["physical"]) ==
                (self.live + 9 * self.R0, self.live + 10 * self.R0 + self.centers + 2),
                "parent.stock_R0", "parent live/physical must use R0, not provider R")
        self.physical = self.live + self.centers + self.R + 2
        for port in self.parent_word["ports"]:
            chart(port)
        self.gram_entries = len(set(self.parent_word["ports"]))*73*73
        self.order = [tuple(c) for c in self.plan["order"]]
        domain = {(s, r) for s in range(9) for r in range(8)}
        require(len(self.order) == 72 and set(self.order) == domain,
                "plan.call_domain", "all 9 by 8 calls exactly once")
        self.dispatch = {(s, r): pid for s, r, pid in self.spec["dispatch"]}
        selected = {(c["stage"], c["replica"]): c for c in self.plan["provider_calls"]}
        require(set(selected) == domain and self.dispatch == {k:c["provider"] for k,c in selected.items()},
                "plan.dispatch", "spec and plan must bind the same calls")
        self.selected = selected
        self.old_calls = {(c["stage"], c["replica"]): c for c in self.parent["calls"]}
        self.idle = {(c["child"], c["port"]): c for c in self.parent["idle_children"]}
        self.side_pair = {i:(side,e["pair"]) for e in self.parent["execution_schedule"]
                          if e["kind"] == "idle_cover_sweep" for side,i in enumerate(e["child_indices"])}
        self.by_role = {}
        for row in self.allocation:
            key = row["stage"], row["replica"], row["helper"]
            require(key not in self.by_role, "allocation.duplicate_role", str(key))
            self.by_role[key] = row
        expected = {(s, r, h) for s, r in self.order for h in range(self.R)}
        require(set(self.by_role) == expected, "allocation.complete_role_domain", "72 times R literal roles")
        self.expected_schedule = self.reconstruct_schedule()

    def reconstruct_schedule(self):
        """Assign each parent event to its most recent local sweep, then expand."""
        src = self.parent["execution_schedule"]
        local_positions = [j for j, e in enumerate(src) if e["kind"] == "local_cover_sweep"]
        blocks = {}
        for i, pos in enumerate(local_positions):
            stop = local_positions[i+1] if i+1 < len(local_positions) else len(src)-2
            blocks[src[pos]["stage"]] = range(pos, stop)
        out = []
        for time, (stage, replica) in enumerate(self.order):
            for j in blocks[stage]:
                event = dict(src[j], time=time, replica=replica, replicas=[replica], source_event=j)
                if event["kind"] == "local_cover_sweep":
                    event["provider_id"] = self.dispatch[stage, replica]
                out.append(event)
        for j in range(len(src)-2, len(src)):
            event = dict(src[j], source_event=j)
            if event["kind"] == "bank_padding_cover_sweep":
                event["families"] = [self.live, self.live]
            else:
                event.update(families=[0, self.live], charged_calls_per_cover=self.live)
            out.append(event)
        return out

    def verify(self, template, summary, sigmas):
        """Verify semantics first; refreshable output digests are checked last."""
        removed = {"local_programs", "exact_local_clifford_recipe_sha256", "residual_adapter_sha256"}
        rewritten = {"version", "live", "physical", "private_namespace", "local_providers", "calls",
                     "idle_children", "hosting", "route_semantics", "bank_padding", "cover_final_correction",
                     "execution_schedule", "loop_order", "async_schedule", "provider_dispatch"}
        require(set(template) == (set(self.parent)-removed)|rewritten,
                "emit.template_fields", "unexpected or missing top-level field")
        for key in set(self.parent)-removed-rewritten:
            require(template[key] == self.parent[key], "emit.retained_parent_field", key)
        expected_padding = dict(self.parent["bank_padding"],families=[],children=[])
        expected_correction = dict(self.parent["cover_final_correction"],families=[0,self.live],
                                   charged_calls_per_cover=self.live)
        require(template["bank_padding"] == expected_padding and template["cover_final_correction"] == expected_correction,
                "emit.global_corrections", "retained correction changes differ")
        require({k:v for k,v in template["route_semantics"].items() if k != "helper"} ==
                {k:v for k,v in self.parent["route_semantics"].items() if k != "helper"},
                "emit.retained_routes", "non-helper route semantics changed")
        hosting = template["hosting"]
        require(hosting["max_helpers_per_physical_family_per_call"] == 1 and hosting["banks"] == [0]*9
                and hosting["owner_map_sha256"] == hashlib.sha256((self.root/"OWNERS.json.gz").read_bytes()).hexdigest(),
                "emit.hosting_contract", "owner source or whole-invocation limits changed")
        require(template["live"] == self.live, "emit.live", str(template["live"]))
        require(template["physical"] == self.physical, "emit.physical",
                f"expected {self.live}+{self.centers}+{self.R}+2={self.physical}, got {template['physical']}")
        expected_namespace = {"centers":[self.live,self.live+self.centers],
                              "reserved_tableau":[self.live+self.centers,self.live+self.centers+self.R],
                              "coefficient":[self.physical-2,self.physical]}
        require(template["private_namespace"] == expected_namespace,
                "emit.reserved_tableau", str(template["private_namespace"]))
        require(template["execution_schedule"] == self.expected_schedule,
                "emit.controller_expansion", "source event blocks or complete invocation order differ")
        require(template["async_schedule"]["order"] == [list(c) for c in self.order],
                "emit.call_order", "plan order changed")
        require(template["async_schedule"]["source_schedule"] == self.parent["execution_schedule"]
                and template["async_schedule"]["source_call_order"] == [[c["stage"],c["replica"]] for c in self.parent["calls"]]
                and template["async_schedule"]["source_plan_sha256"] ==
                hashlib.sha256((self.root/"PLAN.json").read_bytes().replace(b"\r\n",b"\n")).hexdigest(),
                "emit.async_source_binding", "parent schedule/calls or source PLAN changed")
        require(len(template["calls"]) == 72, "emit.call_count", str(len(template["calls"])))
        require(template["hosting"]["pooled_slots"] == self.allocation,
                "emit.role_metadata", "serialized role metadata must be the complete literal allocation")
        require(set(template["local_providers"]) == set(self.words),
                "emit.provider_registry", "provider set changed")
        for pid, word in self.words.items():
            p = template["local_providers"][pid]
            require(all(p[k] == word[k] for k in ("v","h","R","ports","centers"))
                    and p["widths"] == self.widths[pid]
                    and p["local_programs"] == self.programs[pid]
                    and p["local_program_checks"] == self.checks[pid],
                    "emit.provider_semantics", pid)
            linked = {"canonical_word_sha256":"CANONICAL-WORD.json.gz", "local_programs_sha256":"LOCAL-PROGRAMS.json.gz",
                      "exact_local_clifford_recipe_sha256":"CLIFFORD-RECIPES.json", "residual_adapter_sha256":"RESIDUAL-ADAPTERS.json"}
            require(all(p[field] == self.source_hashes[f"providers/{pid}/{filename}"] for field,filename in linked.items()),
                    "emit.provider_artifact_binding", pid)
        intervals = defaultdict(list)
        paid = Counter()
        actual_sigmas = {}
        stream = hashlib.sha256()
        entering = cross = 0
        for time, call in enumerate(template["calls"]):
            key = (call["stage"], call["replica"])
            require(key == self.order[time] and call["time"] == time,
                    "emit.call_order", str(key))
            pid = self.dispatch[key]
            require(call["provider_id"] == pid, "emit.call_provider", str(key))
            source = self.old_calls[key]
            changed_call_fields = {"owners","time","provider_id","local_program_sha256"}
            require({k:v for k,v in call.items() if k not in changed_call_fields} ==
                    {k:v for k,v in source.items() if k not in changed_call_fields},
                    "emit.retained_call_fields", str(key))
            require(call["orientation"] == source["orientation"], "emit.orientation", str(key))
            require(call["local_program_sha256"] == self.checks[pid][call["orientation"]]["sha256"],
                    "emit.call_program", str(key))
            owners = call["owners"]
            require(len(owners) == 224 + self.R, "emit.all_helpers_owned",
                    f"{key}: expected {224+self.R} owners, got {len(owners)}")
            require(len({x[0] for x in owners}) == len(owners)
                    and all(type(x[0]) is int and 0 <= x[0] < self.live for x in owners),
                    "emit.owner_family_uniqueness", str(key))
            require(owners[:224] == source["owners"][:224], "emit.data_owners", str(key))
            for helper, (family, route) in enumerate(owners[224:]):
                role = self.by_role[(*key, helper)]
                width = self.widths[pid][helper]
                child, off = role["child"], role["offset"]
                replica, port = divmod(role["copy"], 112)
                side, pair = self.side_pair[child]
                expected_family = ((replica * 4 + pair) * 2 + side) * 112 + port
                require(family == expected_family == role["family"] and width == role["width"]
                        and replica == role["owner_replica"] and port == role["port"] and role["time"] == time,
                        "emit.role_binding", str((*key, helper)))
                require(off >= 0 and off + width <= self.idle[child,port]["rank"],
                        "emit.role_interval", str((*key, helper)))
                basis = chart(self.parent_word["ports"][port])
                axes = tuple(map(int,self.phases["recipes"][port]["idle_children"][child]["orthogonal_axes"]))
                wanted = axes[off:off+width]
                coordinates = [basis.index(v) for v in wanted]
                spare = sorted(set(range(73)) - set(coordinates))[:9-width]
                expected_route = [3,child,off] if width == 9 else [4,child,off,width,spare]
                require(route == expected_route, "emit.residual_chart", str((*key,helper)))
                indices = coordinates + spare + sorted(set(range(73))-set(coordinates)-set(spare))
                require(len(indices) == len(set(indices)) == 73,
                        "emit.chart_permutation", str((*key, helper)))
                sigma = [basis[j] for j in indices]
                sh = digest(sigma)
                actual_sigmas[sh] = sigma
                stream.update(encoded([*key,helper,family,sh])+b"\n")
                intervals[child,replica,port].append((off, off+width))
                entering += width < 9
                cross += key[1] != replica
            paid.update({int(k):v for k,v in self.checks[pid][call["orientation"]]["paid_profile"].items()})
        remainders = []
        for old in self.parent["idle_children"]:
            child, port = old["child"], old["port"]
            side, pair = self.side_pair[child]
            for replica in range(8):
                endpoint = 0
                for lo, hi in sorted(intervals[child,replica,port]):
                    require(lo == endpoint, "emit.disjoint_prefix", str((child,replica,port,lo,endpoint)))
                    endpoint = hi
                remaining = old["rank"] - endpoint
                if remaining:
                    remainders.append(dict(child=child,port=port,replica=replica,replicas=1,
                                           family=((replica*4+pair)*2+side)*112+port,
                                           rank=remaining,hosted=endpoint,pending_offset=endpoint))
                    paid[remaining] += 1
        require(template["idle_children"] == remainders, "emit.idle_remainders", "literal remainder list differs")
        profile = dict(sorted(paid.items()))
        mass = sum(k*v for k,v in profile.items())
        require(73*self.live-mass == 2560, "emit.rank_mass", str(mass))
        require(profile == {int(k):v for k,v in self.plan["profile"].items()},
                "emit.plan_profile", str(profile))
        require(sigmas == actual_sigmas, "emit.sigma_artifact", "exact 73-column charts differ")
        expected_summary = dict(live=self.live,physical=self.physical,rank_mass=mass,deficit=2560,
                                maxchild=max(profile),hosted_residuals=72*self.R,
                                entering_helper_roles=entering,unique_actual_73column_sigmas=len(actual_sigmas),
                                sigma_stream_sha256=stream.hexdigest(),cross_replica_helper_roles=cross,
                                asynchronous_order_sha256=digest([list(c) for c in self.order]),banks_per_stage=[0]*9,
                                provider_counts=dict(Counter(self.dispatch.values())))
        for key, value in expected_summary.items():
            require(summary[key] == value, "summary."+key, f"expected {value}, got {summary[key]}")
        require({int(k):v for k,v in summary["global_profile"].items()} == profile,
                "summary.global_profile", "literal program plus remainder recount differs")
        require(summary["template_sha256"] == digest(template), "links.template", "digest mismatch")
        parent_payload = gzip.decompress((self.base/"split-centres/GLOBAL-TEMPLATE.json.gz").read_bytes())
        require(summary["parent_template_sha256"] == hashlib.sha256(parent_payload).hexdigest(),
                "links.parent", "digest mismatch")
        artifact_names = ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "LOCAL-CHECKS.json",
                          "INDEPENDENT-LOCAL-REPLAY.json", "RESIDUAL-ADAPTERS.json", "CLIFFORD-RECIPES.json", "CLIFFORD-REVIEW.json")
        required_sources = {"work/complex-nine-native/DATA-PHASES.json"} | {
            f"providers/{pid}/{name}" for pid in self.words for name in artifact_names}
        require(set(summary["source_artifacts"]) == required_sources,
                "links.input_inventory", "exact data-phase plus seven-artifact-per-provider set required")
        require(all(self.source_hashes.get(k) == v for k,v in summary["source_artifacts"].items()),
                "links.inputs", "input byte digest mismatch")
        return dict(status="PASS_EXACT_EMITTER_STRUCTURAL_CONTRACT",R=self.R,R0=self.R0,
                    provider_width_histograms={p:dict(sorted(Counter(w).items())) for p,w in self.widths.items()},
                    provider_helper_frames_checked=sum(len(w) for w in self.widths.values()),
                    owners_per_call=224+self.R,role_domain_size=len(self.by_role),idle_remainders=len(remainders),
                    physical=self.physical,parent_live=self.parent["live"],parent_physical=self.parent["physical"],
                    global_profile=profile,rank_mass=mass,deficit=2560,entering_helper_roles=entering,
                    cross_replica_helper_roles=cross,actual_sigmas=len(actual_sigmas),
                    orthogonal_basis_gram_entries=self.gram_entries,template_semantic_sha256=digest(template))
