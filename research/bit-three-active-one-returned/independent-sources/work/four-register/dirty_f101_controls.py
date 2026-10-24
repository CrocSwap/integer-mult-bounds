"""Check the relation core with independent formal polynomial fixtures.

These fixtures check the search core. They are not paid-call circuits.
They protect collision acceptance, target-rank rejection, and the returned
monomial constraint. No interface is added to the verifier for these checks.
"""
from pathlib import Path
import json,subprocess,tempfile

root=Path(__file__).resolve().parent
source=(root/'dirty_f101.cpp').read_text().split('\nint main(',1)[0]
harness=r'''
Search fixture(int active, int ancilla) {
    Search s;
    s.word.fill(0);
    s.ancillas=8;
    s.diagonal[3]=ancilla;
    s.terms={{active,1057},{ancilla,32768}};
    return s;
}
void check(bool value, const char* message) {
    if (!value) throw std::logic_error(message);
}
int main() {
    setup();
    {
        auto s=fixture(7,0);s.go(Basis{});
        check(s.terminals==1 && s.robust==1,"Three independent target terms must pass");
    }
    {
        auto s=fixture(3,0);s.go(Basis{});
        check(s.terminals==1 && s.robust==0,"A two-term active target must fail");
    }
    {
        auto s=fixture(7,192);s.go(Basis{});
        check(s.terminals==1 && s.robust==1,"The returned monomial can require a new relation");
    }
    {
        auto s=fixture(7,7);s.go(Basis{});
        check(s.terminals==1 && s.robust==0,"The returned relation can kill an active target");
    }
    {
        Basis b;
        for(int i=0;i<6;i+=2) {
            Row r{};r[i]=1;r[i+1]=100;b=insert(b,r);
        }
        auto s=fixture(21,0);s.go(b);
        check(s.terminals==1 && s.robust==1,"Three relations can retain a three-term target");
    }
    {
        auto s=fixture(7,0);
        s.terms.push_back({8,2});s.terms.push_back({16,2});s.off.push_back(24);
        s.go(Basis{});
        check(s.terminals==1 && s.robust==1,"An off-diagonal collision must be found");
    }
    {
        auto s=fixture(7,0);s.terms.push_back({8,2});s.off.push_back(8);
        s.go(Basis{});
        check(s.terminals==0 && s.robust==0,"A lone off-diagonal monomial cannot cancel");
    }
    std::cout << "{\"formal_polynomial_controls\":7,\"passed\":true}\n";
}
'''
with tempfile.TemporaryDirectory(prefix='dirty-f101-controls-') as directory:
    path=Path(directory)
    (path/'controls.cpp').write_text(source+harness)
    subprocess.run(['clang++','-std=c++17','-O2',str(path/'controls.cpp'),'-o',str(path/'controls')],check=True)
    run=subprocess.run([str(path/'controls')],check=True,text=True,capture_output=True)
    result=json.loads(run.stdout)
    result['scope']='Formal polynomial core; these fixtures are not paid-call circuits.'
    (root/'dirty-f101-controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
