"""Independently replay the exact helper-624 main-130 fixed-chart delay gate."""
import argparse
import gzip
import hashlib
import json
import signal
from pathlib import Path

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
GZIP_PIN = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
DECODED_PIN = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PUBLIC = 1501
MAIN = 130
HELPER = 624
UPPER = 117
LIMIT = 10


def stop(*_):
    raise TimeoutError("10-second fixed-chart delay cap")


def involved(event):
    op, dest, *rest = event
    if op in ("ADD", "COPY"):
        return dest, rest[0]
    assert op in ("MOVE", "SCALE", "CLEAR", "INIT")
    return (dest,)


def span(basis):
    vectors = {0}
    for direction in basis:
        assert 0 < direction < 512 and direction not in vectors
        vectors |= {direction ^ row for row in vectors}
    return vectors


def active_chart(start, moves, pre_event):
    current = start
    for clock, old, new in moves:
        if clock >= pre_event:
            break
        assert current == old
        current = new
    return current


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("word", type=Path)
    path = parser.parse_args().word
    signal.signal(signal.SIGALRM, stop)
    signal.alarm(LIMIT)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != GZIP_PIN:
        raise ValueError("changed gzip input")
    decoded = gzip.decompress(raw)
    assert hashlib.sha256(decoded).hexdigest() == DECODED_PIN
    word = json.loads(decoded)
    events = word["program"]
    assert len(events) == 76466 and word["public"] == PUBLIC
    live = set(word["live"])
    main_roles = live | {r+112 for r in live} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(main_roles) == 400 and MAIN in main_roles and HELPER not in main_roles
    contacts = {MAIN:[], HELPER:[]}
    for clock in range(len(events)-1,-1,-1):
        event = events[clock]
        for role in set(involved(event)).intersection(contacts):
            contacts[role].append((clock, event))
    for role in contacts:
        contacts[role].reverse()

    by_role = {role:[(clock,e[2],e[3]) for clock,e in occurrences if e[0]=="MOVE"]
               for role,occurrences in contacts.items()}
    for role, moves in by_role.items():
        assert active_chart(word["initial"][role],moves,len(events)) == word["final"][role]
    assert word["initial"][MAIN] == word["initial"][HELPER] == 3
    old_read, first_lift = contacts[HELPER][:2]
    next_contact = next((clock, event) for clock,event in contacts[HELPER][2:]
                        if event[1] == HELPER and event[0] != "MOVE")
    read_only = [(clock,event) for clock,event in contacts[HELPER][2:] if clock < next_contact[0]]
    assert all(e[0] == "ADD" and e[1] != HELPER and e[2] == HELPER for _,e in read_only)
    assert not any(old_read[0] < clock < next_contact[0] for clock,_ in contacts[MAIN])
    assert old_read[1] == ["ADD",MAIN,HELPER,"-1/2",3]
    assert first_lift[1] == ["MOVE",HELPER,3,UPPER,False]
    assert next_contact[1] == ["ADD",HELPER,623,"1",UPPER]
    assert by_role[HELPER][0][0] == first_lift[0]
    cuts = list(range(first_lift[0]+1, next_contact[0]+1))
    assert all(active_chart(3,by_role[HELPER],cut) == UPPER for cut in cuts)
    live_main = [active_chart(3,by_role[MAIN],cut) for cut in cuts]
    assert live_main == [3]*len(cuts) and cuts[-1] < by_role[MAIN][0][0]

    basis = word["frames"][UPPER]
    upper_space = span(basis)
    main_charts = {3, *(high for _,_,high in by_role[MAIN])}
    aliases = sorted(chart for chart in main_charts if span(word["frames"][chart]) == upper_space)
    assert UPPER not in main_charts and not aliases
    old_rank = len(word["frames"][word["final"][HELPER]])
    removed = len(basis)
    new_rank = old_rank-removed
    assert (old_rank,removed,new_rank) == (9,5,4)
    signal.alarm(0)
    print(json.dumps(dict(
        head=HEAD, helper=HELPER, main=MAIN, word_sha256=GZIP_PIN, payload_sha256=DECODED_PIN,
        event_count=len(events), seconds_cap=LIMIT, old_add=old_read, first_move=first_lift,
        first_blocker=next_contact, literal_paths=by_role, tested_pre_event_cuts=cuts,
        live_main_charts=live_main, intervening_read_only=read_only, reachable_cut=[],
        main_path_aliases_to_upper_span=aliases,
        paid_delta={5:-17}, target_delta={9:-17,4:17}, compatible_saving=0
    ),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
