#!/usr/bin/env python3
"""Independent OLD-word scalar preparation and six lift-boundary certificate.

No author/predecessor code is imported. This does not replay the NEW scalar
endpoint, reconstruct both lift rounds or grant native/erasure permission.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PINS = {'sources/NEW-WORD.json.gz': ['9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3', 'b1cfd03abe9128cf5a3908fbd82652e5e8a2e292'], 'sources/OLD-WORD.json.gz': ['e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491', '0af79e58172f85c302c35b193205c0b185b09393'], 'sources/LIFTS.json': ['38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5', '2ee8cb78fd149f9aca8dd953c650b92495a56266'], 'sources/constructor-source.py': ['fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08', 'c099995bef0e224cbb0ec61c06ed3d0b4d478b33'], 'sources/upstream-PROOF.md': ['769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af', 'bd20fcaf2078691d914d6afbc5cb06a75f47770d'], 'sources/NOTICE': ['91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe', '638a187d1417bda8976e945a2aeaed116a090e37'], 'sources/author-VALIDATION.md': ['cf33fe7acd32b1912bde7bf67abe1386eb042c6d269a9540cd28cdd076a7cac3', '0be8e7f1052628c34e24dfae6777cb3749b224a9']}
PUBLIC, OWNED, Z, OMEGA = 770, 29, 3, 127
ANCHORS = (472, 520, 544, 624, 655, 671)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def strict(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def scalar(raw):
    need(type(raw) is str, "rational coefficient string")
    q = F(raw)
    need(q and str(q) == raw and q.denominator & (q.denominator-1) == 0,
         "nonzero canonical dyadic coefficient")
    return q


def integer(x, maximum, description):
    need(type(x) is int and 0 <= x < maximum, description)


def encoded(row):
    return [[k, str(value)] for k, value in sorted(row.items()) if value]


def add(target, source, q):
    for key, value in source.items():
        new = target.get(key, F(0)) + q*value
        if new:
            target[key] = new
        else:
            target.pop(key, None)
    need(len(target) <= PUBLIC, "bounded sparse row")


def image(row, column):
    return sum((value*column.get(k, F(0)) for k, value in row.items()), F(0))


def binary_span(generators):
    result = {0}
    for vector in generators:
        result |= {x ^ vector for x in result}
    need(len(result) == 1 << len(generators), "independent local frame generators")
    return result


def authenticate():
    raw = {}
    for name, (sha, blob) in PINS.items():
        value = (HERE/name).read_bytes()
        need(hashlib.sha256(value).hexdigest() == sha, "SHA256 source: "+name)
        need(hashlib.sha1(b"blob "+str(len(value)).encode()+b"\0"+value).hexdigest() == blob,
             "Git blob source: "+name)
        raw[name] = value
    return (strict(gzip.decompress(raw["sources/OLD-WORD.json.gz"])),
            strict(gzip.decompress(raw["sources/NEW-WORD.json.gz"])),
            strict(raw["sources/LIFTS.json"]))


def inspect_word(word, prepare):
    need(type(word) is dict and word.get("public") == PUBLIC and type(word["public"]) is int,
         "770 public word interface")
    need(type(word.get("owned_fields")) is int and word["owned_fields"] == OWNED, "29 owned labels")
    need(len(word["initial"]) == len(word["final"]) == PUBLIC, "public frame arrays")
    frames = word["frames"]
    for frame in frames:
        need(type(frame) is list and all(type(v) is int and 0 <= v < 512 for v in frame), "GF2 frame generators")
    for i in word["initial"]+word["final"]:
        integer(i, len(frames), "boundary frame")
    current = word["initial"][:] + [None]*OWNED
    active = set()
    values = {r: {r:F(1)} for r in range(PUBLIC) if current[r] == Z} if prepare else {}
    # Initial non-Z public roles are untouched by the Z preparation. Their
    # identity rows make the mixed first-departure map a declared770-row map.
    rows = {r:{r:F(1)} for r in range(PUBLIC) if current[r] != Z} if prepare else {}
    first, public_first, first_move, last_z_write, z_uses = {}, {}, {}, {}, {}
    owned_z_rows = []
    unknown_arrivals = []
    lifetimes, peak, z_events = 0, 0, 0
    old_z_writes = []
    before_frames = []
    for i, e in enumerate(word["program"]):
        need(type(e) is list and len(e) >= 2 and type(e[0]) is str, "event shape")
        op, r = e[:2]
        integer(r, PUBLIC+OWNED, "event role")
        before_frames.append(current[r])
        if op == "MOVE":
            need(len(e) == 5 and type(e[4]) is bool, "MOVE schema")
            integer(e[2], len(frames), "MOVE source frame")
            integer(e[3], len(frames), "MOVE target frame")
            need(current[r] == e[2] and (r in active) == e[4], "literal MOVE frame and ownership")
            first_move.setdefault(r,(i,e[2],e[3]))
            if e[2] == Z:
                first.setdefault(r, (i, e[3]))
                if r < PUBLIC:
                    need(word["initial"][r] == Z and r not in public_first, "one public Z departure/no return")
                    public_first[r] = (i, e[3])
                    if prepare:
                        need(r in values and values[r] is not None, "known Z-born public value")
                        rows[r] = dict(values[r])
                elif prepare and r in values and values[r] is not None:
                    owned_z_rows.append((i, r, "departure", dict(values[r])))
                if prepare:
                    values.pop(r, None)
            if e[3] == Z and prepare:
                values[r] = None
                unknown_arrivals.append([i, r])
            current[r] = e[3]
        elif op == "INIT":
            need(len(e) == 3 and r >= PUBLIC and r not in active, "owned INIT lifecycle")
            integer(e[2], len(frames), "INIT frame")
            active.add(r)
            lifetimes += 1
            peak = max(peak, len(active))
            current[r] = e[2]
            if e[2] == Z:
                z_events += 1
                if prepare:
                    values[r] = {}
        elif op == "CLEAR":
            need(len(e) == 3 and r in active and current[r] == e[2], "owned CLEAR lifecycle/frame")
            if e[2] == Z:
                z_events += 1
                if prepare:
                    if r in values and values[r] is not None:
                        owned_z_rows.append((i, r, "clear", dict(values[r])))
                    values.pop(r, None)
            active.remove(r)
            current[r] = None
        else:
            need(op in ("ADD", "COPY", "SCALE") and len(e) == (4 if op == "SCALE" else 5), "scalar opcode/schema")
            q, frame = scalar(e[-2]), e[-1]
            integer(frame, len(frames), "scalar frame")
            need(current[r] == frame and (r < PUBLIC or r in active), "scalar destination frame/lifecycle")
            if op != "SCALE":
                source = e[2]
                integer(source, PUBLIC+OWNED, "scalar source")
                need(source != r and current[source] == frame and (source < PUBLIC or source in active),
                     "scalar source common frame/lifecycle")
                if op == "COPY":
                    need(r in active, "COPY owned destination")
            if frame == Z:
                z_events += 1
                last_z_write[r] = i
                z_uses[r] = i
                if op != "SCALE":
                    z_uses[source] = i
                if op == "ADD":
                    old_z_writes.append((i, r, e[2], str(q)))
                if prepare:
                    need(r in values and values[r] is not None, "no uncomputed outside-Z arrival used at Z")
                    if op == "SCALE":
                        values[r] = {k:q*v for k,v in values[r].items()}
                    else:
                        need(source in values and values[source] is not None, "known Z source value")
                        if op == "COPY":
                            need(not values[r], "Z COPY destination is zero")
                            values[r] = {k:q*v for k,v in values[source].items()}
                        else:
                            add(values[r], values[source], q)
                    need(sum(len(v) for v in values.values() if v is not None) <= 100000,
                         "bounded current Z preparation terms")
    need(not active and current[:PUBLIC] == word["final"], "all literal exits and lifetimes")
    if prepare:
        need(len(rows) == PUBLIC and all(r in public_first for r in range(PUBLIC) if word["initial"][r] == Z),
             "every Z-born public first-departure row")
    return {"rows":rows, "first":first, "public_first":public_first, "first_move":first_move,
            "last_z_write":last_z_write, "z_uses":z_uses, "owned_z_rows":owned_z_rows,
            "unknown_arrivals":unknown_arrivals, "z_writes":old_z_writes,
            "before_frames":before_frames,
            "summary":{"events":len(word["program"]), "owned_lifetimes":lifetimes,
                       "peak_owned":peak, "public_Z_departures":len(public_first),
                       "Z_events":z_events}}


def parse_lifts(lifts, old, new):
    need(type(lifts) is dict and type(lifts.get("schema_version")) is int and lifts["schema_version"] == 1,
         "LIFTS schema")
    columns, clusters = {}, []
    for round_index, rnd in enumerate(lifts["rounds"]):
        for cluster_index, cluster in enumerate(rnd["clusters"]):
            frame = cluster["F"]
            integer(frame, len(old["frames"]), "lift entrance")
            anchors = []
            for raw, entry in cluster["anchors"].items():
                q = int(raw)
                need(str(q) == raw and q in ANCHORS and q not in columns, "canonical unique anchor")
                h = {}
                for key, value in entry["h"].items():
                    k = int(key)
                    need(str(k) == key and 0 <= k < PUBLIC, "lift coordinate role")
                    h[k] = scalar(value)
                    need(old["initial"][k] == Z, "lift coordinate lies in Z input domain")
                need(old["initial"][q] == Z and old["final"][q] == OMEGA and new["initial"][q] == frame,
                     "changed anchor endpoint frames")
                columns[q] = h
                anchors.append(q)
            carriers = cluster["carriers"]
            need(type(carriers) is list and len(carriers) == 1 and all(type(c) is int for c in carriers), "one shared carrier")
            clusters.append({"round":round_index, "cluster":cluster_index, "entrance":frame,
                             "anchors":sorted(anchors), "carriers":carriers})
    need(tuple(sorted(columns)) == ANCHORS, "exact six lift coordinates")
    need({r for r in range(PUBLIC) if old["initial"][r] != new["initial"][r]} == set(ANCHORS), "exact six initial frame changes")
    need(all(old[k] == new[k] for k in old if k not in ("initial", "program")), "unchanged other word metadata")
    return columns, clusters


def response(rows, h):
    return {r:value for r,row in sorted(rows.items()) if (value:=image(row,h))}


def main_map(column, live):
    result = dict(column)
    for r in live:
        value = column.get(r, F(0))
        if value:
            result[r+112] = result.get(r+112,F(0))+value
            if not result[r+112]:
                del result[r+112]
    return result


def boundary_identities(old, h, rows):
    live = old["live"]
    need(type(live) is list and len(set(live)) == len(live) == len(old["ports"]) == 104,
         "declared104 main pairs")
    need(all(type(r) is int and 0 <= r < PUBLIC-112 for r in live), "main driving role types")
    need(not (set(live) & {r+112 for r in live}), "disjoint declared main pairs")
    unit, prepared_unit, U = {}, {}, {}
    for q in ANCHORS:
        unit[str(q)] = [str(h[p].get(q,F(0))) for p in ANCHORS]
        prepared_unit[str(q)] = [str(image(rows[q],h[p])) for p in ANCHORS]
        expect = [str(int(q==p)) for p in ANCHORS]
        need(unit[str(q)] == prepared_unit[str(q)] == expect, "all-six anchor and prepared cross-unit conditions")
        col = dict(h[q])
        add(col,{q:F(1)},F(-1))
        U[q] = col
        need(main_map(col,live) == col, "declared M U=U")
        need(q not in {r+112 for r in live}, "anchor row of M is unit")
    squares = {}
    for q in ANCHORS:
        col = {}
        for p in ANCHORS:
            add(col,U[p],U[q].get(p,F(0)))
        need(not col, "N squared zero on all six nonzero columns")
        squares[str(q)] = encoded(col)
    return {"anchor_order":list(ANCHORS), "h_anchor_matrix":unit, "A_h_anchor_matrix":prepared_unit,
            "U_columns":{str(q):encoded(U[q]) for q in ANCHORS}, "N_squared_columns":squares,
            "declared_M":"output(r+112) += input(r) for r in word.live; identity elsewhere",
            "identities":["N=sum U_q e_q^T", "N^2=0", "(I+N)^-1=I-N", "M U=U", "e_q^T M=e_q^T", "M N=N M=N"],
            "scope":"Algebra of the declared interface and lift coordinates; not a NEW-word endpoint replay."}


def literal_matches(program, target):
    return [i for i,e in enumerate(program) if e == target]


def placement(old,new,old_scan,new_scan,h,clusters,responses):
    program = new["program"]
    placements = []
    for cluster in clusters:
        F0 = cluster["entrance"]
        carrier = cluster["carriers"][0]
        carrier_coeffs = {q:responses[q].get(carrier,F(0)) for q in cluster["anchors"]}
        need(all(carrier_coeffs.values()), "both anchors share a nonzero carrier response")
        old_carrier_index, old_destination = old_scan["public_first"][carrier]
        entrance_span = binary_span(old["frames"][F0])
        need(binary_span(old["frames"][Z]) < entrance_span < binary_span(old["frames"][old_destination]),
             "shared carrier entrance strictly inside old destination")
        block = [["MOVE",carrier,Z,F0,False]]
        block += [["ADD",carrier,q,str(carrier_coeffs[q]),F0] for q in cluster["anchors"]]
        block += [["MOVE",carrier,F0,old_destination,False]]
        starts = [i for i in range(len(program)-len(block)+1) if program[i:i+len(block)] == block]
        need(len(starts) == 1, "exact unique shared carrier response block")
        start = starts[0]
        need(new_scan["z_uses"].get(carrier,-1) < start, "carrier unused at Z after its detour")
        need(all(start+len(block) <= new_scan["first_move"][q][0] for q in cluster["anchors"]),
             "carrier responses delivered before either anchor departure")
        anchors = []
        for q in cluster["anchors"]:
            departure, destination = old_scan["public_first"][q]
            need(entrance_span < binary_span(old["frames"][destination]),
                 "anchor entrance strictly inside first destination")
            new_departures = literal_matches(program,["MOVE",q,F0,destination,False])
            need(len(new_departures) == 1, "unique lifted anchor departure")
            off = []
            for r,coefficient in responses[q].items():
                if r == q:
                    need(coefficient == 1, "unit self response")
                    continue
                if r == carrier:
                    off.append({"role":r,"coefficient":str(coefficient),"class":"shared_carrier",
                                "event":start+1+cluster["anchors"].index(q)})
                else:
                    need(r in old_scan["public_first"] and old_scan["public_first"][r][1] == destination,
                         "complete response support is carrier or same destination recipient")
                    event=["ADD",r,q,str(coefficient),destination]
                    matches=literal_matches(program,event)
                    typed=[i for i in matches if i > new_departures[0] and
                           i > next(j for j,e in enumerate(program) if e[0]=="MOVE" and e[1]==r)]
                    need(typed, "literal same-destination response ADD after both departures")
                    off.append({"role":r,"coefficient":str(coefficient),"class":"same_destination_recipient",
                                "events":typed})
            anchors.append({"anchor":q,"old_departure":[departure,destination],
                            "new_departure":new_departures[0],"response":encoded(responses[q]),"off_anchor":off})
        placements.append({**cluster,"carrier":carrier,"old_carrier_departure":old_carrier_index,
                           "carrier_block_start":start,"carrier_block":block,"anchors_certificate":anchors,
                           "entrance_dimension":len(old["frames"][F0]),
                           "carrier_destination_dimension":len(old["frames"][old_destination])})
    old_writes=[entry for entry in old_scan["z_writes"] if entry[1] in ANCHORS]
    need(old_writes == [(5558,624,623,"1")], "exact postponed anchor write inventory")
    _,q,source,coefficient=old_writes[0]
    need(old_scan["public_first"][source][1] == old_scan["public_first"][q][1] == 117,
         "postponed source same first destination")
    need(old_scan["last_z_write"].get(source,-1) < 5558, "postponed source unchanged at Z after original write")
    need(not any(i>5558 and e[0]=="ADD" and e[-1]==Z and e[2]==q for i,e in enumerate(old["program"])),
         "anchor not read at Z after its postponed write")
    write=["ADD",624,623,"1",117]
    postponed=literal_matches(program,write)
    need(len(postponed)==1 and not literal_matches(program,["ADD",624,623,"1",Z]), "actual postponed write only at117")
    need(new_scan["first_move"][624][0] < postponed[0] and new_scan["first_move"][623][0] < postponed[0],
         "actual postponed write after both first arrivals")
    restores=[]
    for cluster in clusters:
        for q in cluster["anchors"]:
            for r,coefficient in h[q].items():
                if r!=q:
                    restores.append(["ADD",r,q,str(-coefficient),OMEGA])
    need(len(restores)==16 and program[-len(restores):] == restores, "exact ordered final h-restoration suffix")
    need(all(new["final"][e[1]]==new["final"][e[2]]==OMEGA for e in restores), "restoration common final frame")
    return {"clusters":placements,"postponed_write":{"old_index":5558,"new_index":postponed[0],"event":write,
                "new_anchor_arrival":new_scan["first_move"][624][0],
                "new_source_arrival":new_scan["first_move"][623][0],
                "old_source_last_Z_write":old_scan["last_z_write"].get(623,-1)},
            "restore_suffix_start":len(program)-len(restores),"restore_suffix":restores,
            "placement_limit":"Common-frame structural placement and source side conditions, not complete chronological reconstruction of either lift round."}


def controls(rows,h,baseline,old_scan):
    result={}
    for label,column in (("naive_two_term_624",{624:F(1),625:F(-1)}),
                         ("omit_624_dyadic_732",{k:v for k,v in h[624].items() if k!=732}),
                         ("omit_624_main_destination_205",{k:v for k,v in h[624].items() if k!=205})):
        changed=response(rows,column)
        keys=sorted(set(changed)|set(baseline[624]))
        differences=[r for r in keys if changed.get(r,F(0))!=baseline[624].get(r,F(0))]
        need(differences,"response semantic control must change an actual coefficient")
        r=differences[0]
        need([column.get(q,F(0)) for q in ANCHORS]==[F(int(q==624)) for q in ANCHORS],
             "control preserves all-six raw anchor unit conditions")
        need([image(rows[q],column) for q in ANCHORS]==[F(int(q==624)) for q in ANCHORS],
             "control preserves all-six prepared anchor unit conditions")
        result[label]={"kind":"counterfactual lift coordinate, not an accepted alternative program",
                       "raw_anchor_units_still_hold":True,"prepared_anchor_units_still_hold":True,
                       "changed_response_rows":differences,
                       "first_response_witness":{"role":r,"actual":str(changed.get(r,F(0))),
                                                 "expected":str(baseline[624].get(r,F(0))),
                                                 "old_first_departure":old_scan["public_first"].get(r)},
                       "control_coordinate":encoded(column)}
    return result


def run():
    old,new,lifts=authenticate()
    h,clusters=parse_lifts(lifts,old,new)
    old_scan=inspect_word(old,True)
    new_scan=inspect_word(new,False)
    responses={q:response(old_scan["rows"],h[q]) for q in ANCHORS}
    owned=[]
    for i,r,kind,row in old_scan["owned_z_rows"]:
        values=[image(row,h[q]) for q in ANCHORS]
        need(not any(values), "all known Z-owned preparation outputs have zero six-lift response")
        owned.append({"index":i,"role":r,"kind":kind,"responses":list(map(str,values))})
    basis=boundary_identities(old,h,old_scan["rows"])
    places=placement(old,new,old_scan,new_scan,h,clusters,responses)
    row_payload=[encoded(old_scan["rows"][r]) for r in range(PUBLIC)]
    return {"schema_version":1,"scope":"OLD6372 Z-preparation/six-coordinate basis and literal6375 local boundary only",
            "source_pins":PINS,"old_inventory":old_scan["summary"],"new_structural_inventory":new_scan["summary"],
            "mixed_preparation_rows_sha256":hashlib.sha256((canonical(row_payload)+"\n").encode()).hexdigest(),
            "mixed_preparation_definition":"Z-born public rows frozen at first Z departure; other public rows are boundary identity; not one simultaneous full-word endpoint.",
            "first_Z_departures":{str(r):list(v) for r,v in sorted(old_scan["public_first"].items())},
            "lift_coordinates":{str(q):encoded(h[q]) for q in ANCHORS},
            "responses":{str(q):encoded(responses[q]) for q in ANCHORS},"basis":basis,"literal_local_placement":places,
            "known_Z_owned_outputs":owned,"outside_Z_arrivals_not_value_replayed":old_scan["unknown_arrivals"],
            "controls":controls(old_scan["rows"],h,responses,old_scan),
            "remaining":["Round2 actual intermediate preparation equivalence is not proved by using the OLD response columns alone.",
                         "Complete chronological two-round NEW reconstruction, arbitrary-public endpoint and all dirty-owned functionals remain session8 work.",
                         "Non-Z values, NEW scalar values and COPY-zero outside Z were not propagated by this local checker.",
                         "MOVE is scalar identity under the retained projection; no native phase, all-width, erasure, pricing or kappa admission."]}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true")
    options=parser.parse_args()
    result=run()
    payload=(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    if options.emit:
        sys.stdout.buffer.write(payload)
    else:
        retained=HERE/"PREP-RESULT.json"
        need(retained.is_file(),"retained PREP-RESULT.json receipt required")
        observed=strict(retained.read_bytes())
        need(type(observed) is dict and type(observed.get("schema_version")) is int and observed["schema_version"]==1,
             "typed preparation receipt schema")
        need(canonical(observed)==canonical(result),"strict typed PREP-RESULT receipt")
        print("PASS six-coordinate local preparation and retained receipt")
