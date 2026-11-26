"""Fixed tape schoolbook multiplier on the published raw input/output interface."""
from pathlib import Path
import json
import random
import runpy

tm = runpy.run_path(str(Path(__file__).with_name("node-tapes.py")))
Builder, Action = tm["Builder"], tm["Action"]
BLANK, HALT = tm["BLANK"], tm["HALT"]
DIGITS, MARKED = ("0", "1"), ("u", "v")
END, LEFT = "$", "^"


def machine():
    b=Builder()
    names=("start","copy_x","copy_y","seek_start","mark_zero","next_y","add0","add1",
           "carry","seek_mark","reset_x","shift","set_mark","seek_output","emit")
    s={name:b.label(name) for name in names}
    b.put(s["start"],s["copy_x"],[(t,LEFT) for t in "ABR"],[(t,1) for t in "ABR"])
    for src,dst,stop,nxt in (("copy_x","A","|","copy_y"),("copy_y","B",BLANK,"seek_start")):
        choices={d:Action(s[src],((dst,d),("R","0")),(("I",1),(dst,1),("R",1))) for d in DIGITS}
        if dst=="A":
            choices[stop]=Action(s[nxt],(("A",END),),(("I",1),("A",-1)))
        else:
            choices[stop]=Action(s[nxt],(("B",END),("R",END)),(("B",-1),("R",-1)))
        b.sel(s[src],"I",choices)
    b.sel(s["seek_start"],"R",{LEFT:Action(s["mark_zero"],moves=(("R",1),))},
          Action(s["seek_start"],moves=(("R",-1),)))
    b.put(s["mark_zero"],s["next_y"],(("R",MARKED[0]),))
    b.sel(s["next_y"],"B",{"0":Action(s["shift"]),"1":Action(s["add0"]),LEFT:Action(s["seek_output"])})

    for carry in (0,1):
        choices={LEFT:Action(s["carry"] if carry else s["seek_mark"])}
        for d in (0,1):
            stage=b.label("add_bits")
            choices[str(d)]=Action(stage)
            digits={}
            for alphabet in (DIGITS,MARKED):
                for old in (0,1):
                    value=d+old+carry
                    digits[alphabet[old]]=Action(s["add"+str(value//2)],(("R",alphabet[value%2]),),
                                                 (("R",1),("A",-1)))
            b.sel(stage,"R",digits)
        b.sel(s["add"+str(carry)],"A",choices)
    b.sel(s["carry"],"R",{"0":Action(s["seek_mark"],(("R","1"),)),
                           "1":Action(s["carry"],(("R","0"),),(("R",1),))})
    b.sel(s["seek_mark"],"R",{c:Action(s["reset_x"]) for c in MARKED},
          Action(s["seek_mark"],moves=(("R",-1),)))
    b.sel(s["reset_x"],"A",{END:Action(s["shift"],moves=(("A",-1),))},
          Action(s["reset_x"],moves=(("A",1),)))
    b.sel(s["shift"],"R",{m:Action(s["set_mark"],(("R",str(i)),),(("R",1),("B",-1)))
                            for i,m in enumerate(MARKED)})
    b.sel(s["set_mark"],"R",{d:Action(s["next_y"],(("R",MARKED[i]),)) for i,d in enumerate(DIGITS)})
    b.sel(s["seek_output"],"R",{END:Action(s["emit"],moves=(("R",-1),))},
          Action(s["seek_output"],moves=(("R",1),)))
    emit={LEFT:Action(HALT)}
    for alphabet in (DIGITS,MARKED):
        for i,c in enumerate(alphabet):
            emit[c]=Action(s["emit"],(("O",str(i)),),(("O",1),("R",-1)))
    b.sel(s["emit"],"R",emit)
    return b,tuple("IABRO"),s["start"]


def main():
    prog=machine()
    rng=random.Random(89105)
    tests=[(n,x,y) for n in range(1,6) for x in range(1<<n) for y in range(1<<n)]
    for n in (7,16,32,65,128):
        tests.extend((n,x,y) for x,y in [(0,0),((1<<n)-1,(1<<n)-1),
                      *[(rng.getrandbits(n),rng.getrandbits(n)) for _ in range(8)]])
    max_t=max_s=0
    for n,x,y in tests:
        raw=f"{x:0{n}b}|{y:0{n}b}"
        sim=tm["Simulation"](prog,{"I":raw}).execute(64*(n+1)**2)
        assert sim.tape["O"]==dict(enumerate(f"{x*y:0{2*n}b}"))
        assert sim.tape["I"]==dict(enumerate(raw))
        assert sim.visited<=12*(n+1)
        max_t,max_s=max(max_t,sim.steps),max(max_s,sim.visited)
    print(json.dumps(dict(pairs=len(tests),finite_states=len(prog[0].rules),tapes=len(prog[1]),
                          max_steps=max_t,max_cells=max_s)))

if __name__=="__main__":
    main()
