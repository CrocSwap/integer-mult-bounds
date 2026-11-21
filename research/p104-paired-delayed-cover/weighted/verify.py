# SPDX-License-Identifier: Apache-2.0
"""Run the weighted-exit successor on the previously authenticated paired supplier."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
WEIGHTED = PACKAGE.parents[1]/"research/net-tax-rank-compiler/WEIGHTED-EXITS.md"
SEALED = {
    "moment/primary/PRICE.json": "8c09bcccce796c9b01efed5d9363af8fe6b8719f588eb6de5148933411a8850d",
    "moment/independent/PRICE.json": "5c9d36bad5d7fca162d135e9d8658ab408a6d89edd262be167747cc164c12229",
    "moment/application/RESULT.json": "0fed060d852e6e37c1ff4ffe514d5765c9efdd6e0a3a24f6bc59cbbdcc7b0d79",
    "moment/independent/ACCEPT.json": "0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377",
    "primary/PRICE.json": "4acbb38393550df5b046f125328a67bc344fe592a107556145ac315acf083a34",
    "independent/PRICE.json": "0f43bebea0a8a4a258e14ea7495ed9d2bdbfe8f952dafd423d7e1651b4807332",
    "application/RESULT.json": "65473eba091d40551586a3e078bb6c4155813ba64e7207e0698765a2e738da0d",
    "independent/ACCEPT.json": "32d40619c37fdcf91f63930e3ebdf1ec0e19210f91e4f1a74617fcc1b3ada10c",
}


def authenticate(path, digest):
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("source or receipt mismatch: " + path.name)


def run(script, *args):
    subprocess.run([sys.executable,"-IB",HERE/script,*args],check=True)


def rebuild_prices(peer, cover, normalized, previous_acceptance, work, theorem):
    application = peer/"APPLICATION.json"
    archive = peer/"APPLICATION-SOURCES.tar.gz"
    binary = cover/"BINARY.json"
    prior_price = PACKAGE/"normalized/independent/PRICE.json"
    common = ("--application",application,"--archive",archive,"--binary",binary,
              "--accept",previous_acceptance,"--prior-price",prior_price,"--weighted",theorem)
    law = work/"law.json"
    failed_mean = work/"mean.json"
    run("controls/law.py",*common,"--out",law)
    authenticate(law,"0239f7f69dea671a66a37e3bcaae61c16d23dc794812d519d1c020821332ad36")
    run("controls/mean.py","--predecessor-checker",HERE/"controls/law.py","--predecessor-price",law,
        *common,"--out",failed_mean)
    authenticate(failed_mean,"ea84892ef2b2da5572e7cdabe54d228ee74f6671d11f87bd6aa263306fd8ffdc")
    primary = work/"primary.json"
    audit = work/"independent.json"
    run("primary/price.py","--peer-application",application,"--peer-archive",archive,"--r347-binary",binary,
        "--r348-price",prior_price,"--r348-full",normalized/"REPLAY.json","--r348-accept",previous_acceptance,
        "--weighted-theorem",theorem,"--r350-exclusion",HERE/"controls/FINITE.json","--out",primary)
    run("independent/price.py","--law-checker",HERE/"controls/law.py","--law-receipt",law,"--failure",failed_mean,
        *common,"--out",audit)
    authenticate(primary,SEALED["primary/PRICE.json"])
    authenticate(audit,SEALED["independent/PRICE.json"])
    return primary, audit


def moment_prices(peer, cover, previous, previous_acceptance, previous_prices, mean_control, work, theorem):
    primary, audit = work/"moment-primary.json", work/"moment-independent.json"
    old_primary, old_audit = previous_prices
    application, archive = peer/"APPLICATION.json", peer/"APPLICATION-SOURCES.tar.gz"
    run("moment/primary/price.py","--peer-application",application,"--peer-archive",archive,
        "--r347-binary",cover/"BINARY.json","--r350-mean",HERE/"controls/FINITE.json",
        "--r351-helper",HERE/"primary/price.py","--r351-price",old_primary,"--r351-audit",old_audit,
        "--r351-full",previous/"REPLAY.json","--r351-accept",previous_acceptance,"--weighted-theorem",theorem,"--out",primary)
    run("moment/independent/price.py","--law",HERE/"controls/law.py","--old-primary",old_primary,
        "--old-independent",old_audit,"--accept",previous_acceptance,"--signed",previous/"REPLAY.json",
        "--mean",mean_control,"--application",application,"--binary",cover/"BINARY.json","--archive",archive,"--weighted",theorem,"--out",audit)
    authenticate(primary,SEALED["moment/primary/PRICE.json"])
    authenticate(audit,SEALED["moment/independent/PRICE.json"])
    return primary, audit


def signed_case(prefix, peer, previous, previous_acceptance, prices, work, acceptance_arguments):
    primary, audit = prices
    signed, accepted = work/"signed", work/"accepted.json"
    run(prefix+"application/replay.py","--peer-package",peer,"--cover-package",PACKAGE,"--prior-run",previous,
        "--prior-accept",previous_acceptance,"--primary",primary,"--independent",audit,"--out",signed)
    authenticate(signed/"REPLAY.json",SEALED[prefix+"application/RESULT.json"])
    result = json.loads((signed/"REPLAY.json").read_bytes())
    if set(result["output_sha256"]) != {"APPLICATION.json","BINARY.json","PHYSICAL.json"}:
        raise ValueError("incomplete signed result")
    for name, digest in result["output_sha256"].items():
        authenticate(signed/name,digest)
    run(prefix+"independent/accept.py","--peer",peer,"--prior-run",previous,"--prior-accept",previous_acceptance,
        "--run",signed,"--primary",primary,"--independent",audit,*acceptance_arguments,"--out",accepted)
    authenticate(accepted,SEALED[prefix+"independent/ACCEPT.json"])
    return signed, accepted, result


def main():
    parser = ArgumentParser()
    for name in ("peer","cover-run","normalized-run","normalized-accept","work"):
        parser.add_argument("--"+name,required=True,type=Path)
    args = parser.parse_args()
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3,12) or not __debug__:
        raise ValueError("CPython 3.12 with assertions is required")
    for name, expected in SEALED.items():
        authenticate(HERE/name,expected)
    args.work.mkdir()
    primary, audit = rebuild_prices(args.peer,args.cover_run,args.normalized_run,args.normalized_accept,args.work,WEIGHTED)
    first_prices = (primary,audit)
    signed, accepted, result = signed_case("",args.peer,args.normalized_run,args.normalized_accept,
                                          first_prices,args.work,())
    print("PASS_PAIRED_WEIGHTED_EXITS",result["claim"],result["difference"],flush=True)
    moment_work = args.work/"moment"
    moment_work.mkdir()
    second_prices = moment_prices(args.peer,args.cover_run,signed,accepted,first_prices,
                                  args.work/"mean.json",moment_work,WEIGHTED)
    extra = ("--prior-checker",HERE/"independent/accept.py","--replay-sha",SEALED["moment/application/RESULT.json"])
    _, _, result = signed_case("moment/",args.peer,signed,accepted,second_prices,moment_work,extra)
    print("PASS_PAIRED_SOURCE_MOMENT",result["claim"],result["difference"],flush=True)


if __name__ == "__main__":
    main()
