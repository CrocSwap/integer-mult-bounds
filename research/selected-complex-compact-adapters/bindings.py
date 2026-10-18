"""Bind the adapter catalogue to the actual selected R480/T16 supplier."""
from hashlib import sha256
from io import BytesIO
import gzip
import json
import tarfile

from streams import need
import source_data

SELECTED_ARCHIVE="research/community-frontier1094-audit/selected-replay.tar.gz"
TEMPLATE="candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz"
TEMPLATE_PAYLOAD="9c4c51425251389ee9a747c465814cd07c64812c15b7aeef704dad7d65395a74"


def load(root):
    local=source_data.load_local(root)
    with tarfile.open(fileobj=BytesIO((root/SELECTED_ARCHIVE).read_bytes()),mode="r:gz") as archive:
        matches=[m for m in archive.getmembers() if m.name==TEMPLATE]
        need(len(matches)==1 and matches[0].isfile(),"one selected template member")
        payload=gzip.decompress(archive.extractfile(matches[0]).read())
    need(sha256(payload).hexdigest()==TEMPLATE_PAYLOAD,"actual selected template payload")
    selected=json.loads(payload);provider=selected["local_providers"]["gauge44"]
    need((selected["m"],selected["live"],selected["physical"],len(selected["calls"]))
         ==(73,14336,14826,144),"selected complex dimensions")
    need((provider["h"],provider["R"])==(9,480),"actual R480 provider, not R492 predecessor")
    need(provider["local_programs"]==local["LOCAL-PROGRAMS.json.gz"],"selected literal program binding")
    pins=source_data.MEMBER_PINS
    need(provider["canonical_word_sha256"]==pins["slots/local/CANONICAL-WORD.json.gz"] and
         provider["exact_local_clifford_recipe_sha256"]==pins["slots/local/CLIFFORD-RECIPES.json"],
         "selected canonical word and Clifford recipe binding")
    need(selected["exact_data_phase_recipe_sha256"]==pins[
         "t16/global/base/work/complex-nine-native/DATA-PHASES.json"],"selected data phase binding")
    records={}
    for direction,events in provider["local_programs"].items():
        encoded=json.dumps(events,separators=(",",":"),sort_keys=True).encode()
        need(sha256(encoded).hexdigest()==provider["local_program_checks"][direction]["sha256"],
             "literal selected orientation digest")
        records[direction]={"events":len(events),"sha256":sha256(encoded).hexdigest(),
                            "paid_profile":provider["local_program_checks"][direction]["paid_profile"]}
    receipt={"selected_template_payload_sha256":TEMPLATE_PAYLOAD,
             "m":73,"live_families":14336,"physical_slots":14826,"calls":144,
             "local_helper_count":480,"local_programs":records,
             "scope":"Source binding to retained finite certificates; no new whole-supplier cold replay."}
    return local,receipt
