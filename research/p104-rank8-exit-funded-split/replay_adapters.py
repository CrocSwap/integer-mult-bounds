# SPDX-License-Identifier: Apache-2.0
"""Counted edits to the private copies of the exact #7156 replay engines."""

from replay_sources import need


def adapt_replay(work, profile, witness):
    def patch(file, old, new, count=1):
        path = work / file
        raw = path.read_text()
        need(raw.count(old) == count, "Unexpected predecessor adapter anchor in " + file + ": " + old)
        path.write_text(raw.replace(old, new))

    native = "verify_native.py"
    owned = f'({profile["lifetimes"]}, {profile["peak"]}, {profile["owned"]})'
    patch(native, "(64, 47, 61)", owned, count=2)
    patch(native, "oldN['lifetimes']+2==64 and N['owned_peak']==47",
          f'oldN[\'lifetimes\']+2=={profile["lifetimes"]} and N[\'owned_peak\']=={profile["peak"]}')
    patch(native, "old['owned_fields']+2==61", f'old[\'owned_fields\']+2=={profile["owned"]}')
    patch(native, "['lifetimes']==64,'Fresh exact owned census",
          f'["lifetimes"]=={profile["lifetimes"]},\'Fresh exact owned census')
    paid = {int(r): q for r, q in profile["paid_delta"].items()}
    target = {int(r): q for r, q in profile["target_delta"].items()}
    patch(native, "=={4:1,5:1,9:-1} and delta(N['paid'],oldN['paid'])=={3:1,5:1,8:-1}",
          f"=={target!r} and delta(N['paid'],oldN['paid'])=={paid!r}")
    patch(native, "len(old['program'])+40 and new['public']==old['public']+1==1498",
          f'len(old[\'program\'])+{profile["added_events"]} and new[\'public\']==old[\'public\']+1==1499')
    patch(native, ";a=hit['path']['old'];b=hit['path']['new']\n    needed=changed|{(u,f),(f,v),(a,f),(f,b),(a,b),(u,v)}",
          "\n    needed=changed|{(u,f),(f,v),(u,v)}\n"
          "    if 'path' in hit:\n"
          "        a,b=hit['path']['old'],hit['path']['new'];needed|={(a,f),(f,b),(a,b)}\n"
          "    e=hit['extension'];needed|={(3,e['old']),(e['old'],e['new']),(3,e['new'])}")
    patch(native, "PASS_TEMPORAL_CHART306_NATIVE", "PASS_FUNDED_EXIT_NATIVE")
    patch("verify.py", "PASS_TEMPORAL_CHART306_CONTINUATION", "PASS_FUNDED_EXIT_CONTINUATION")
    patch("adapt.py", "(64, 47, 61)", owned)
    patch("price.py", "Entire reconstructed current #7155 invoice", "Entire reconstructed current #7156 invoice")
    patch("adapt.py", 'crossing_probe_rejected,"scope":"Reuse exact same native word all-column adjoint;',
          'crossing_probe_rejected,"scope":"Fresh exact current native arbitrary-input adjoint;')
    if "path" not in witness:
        start = "    bad = deepcopy(hit)\n    bad['paid_delta'] = {}\n"
        stop = "    bad = deepcopy(hit)\n    bad['ranks']"
        text = (work / "certificate.py").read_text()
        a, b = text.index(start), text.index(stop)
        patch("certificate.py", text[a:b], "")

    patch("construct.py", "from source import need", "from source import need\nfrom replay_checks import extend_exit")
    patch("construct.py", "candidate = split(word, hit, paths)", "candidate = split(extend_exit(word, hit), hit, paths)")

    early = "verify_early.py"
    patch(early, "from construct import construct",
          "from construct import construct\nfrom replay_checks import check_stationary, check_exit, packing\nfrom fractions import Fraction as Q")
    patch(early, "new=construct(old,read(HERE/'WITNESS.json'),read(HERE/'PATHS.json'));",
          "hit=read(HERE/'WITNESS.json');stationary=check_stationary(old,hit);exit_check=check_exit(old,hit,read(HERE/'PATHS.json'))\n"
          "        new=construct(old,hit,read(HERE/'PATHS.json'));")
    patch(early, "        return normalized(dict(status=",
          "        pack=packing(invoice,after,G.module('stationary_packing',vendor/'interval_gate.py'),Q(gate['claim']))\n"
          "        return normalized(dict(stationary=stationary,exit_extension=exit_check,packing=pack,status=")
    patch(early, "    r=run();need(r==read(HERE/'EARLY-RESULT.json'),'Every frozen early receipt field');"
                 "print(r['status'],r['price']['claim_decimal'],flush=True)",
          "    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args()\n"
          "    r=run()\n"
          "    if args.out:\n"
          "        with args.out.open('x') as out:json.dump(r,out,sort_keys=True,indent=2);out.write('\\n')\n"
          "    else:need(r==read(HERE/'EARLY-RESULT.json'),'Every frozen early receipt field')\n"
          "    print(r['status'],r['price']['claim_decimal'],flush=True)")
