// Enumerate supports first, then positive multiplicities, for an independent census.
#include <algorithm>
#include <fstream>
#include <iostream>
#include <set>
#include <vector>
using namespace std;

struct Gate { int x, y, matrix; };
vector<Gate> gates;
vector<int> support, count_by_gate, spaces;
long long all_multisets=0, accepted=0;
int class_id, allowed_roles;

int rank_binary(vector<int> rows) {
    int rank=0;
    for(int col=0;col<16;++col) {
        auto pivot=find_if(rows.begin()+rank,rows.end(),[&](int x){return (x>>col)&1;});
        if(pivot==rows.end())continue;
        swap(rows[rank],*pivot);
        for(int i=rank+1;i<(int)rows.size();++i)
            if((rows[i]>>col)&1)rows[i]^=rows[rank];
        ++rank;
    }
    return rank;
}

void emit_if_valid() {
    int roles=0;
    for(int a=0;a<4;++a)if((allowed_roles>>a)&1) {
        bool valid=true;
        for(int v=1;v<16 && valid;++v)if(v!=(1<<a)) {
            int xhits=0,yhits=0;
            for(int j:support) {
                xhits+=count_by_gate[j]*__builtin_parity(unsigned(v&gates[j].x));
                yhits+=count_by_gate[j]*__builtin_parity(unsigned(v&gates[j].y));
            }
            valid=xhits>=3 && yhits>=3;
        }
        if(valid)roles|=1<<a;
    }
    if(!roles)return;
    ++accepted;
    cout<<"{\"class\":"<<class_id<<",\"possible_ancilla\":"<<roles<<",\"counts\":[";
    for(int j=0;j<(int)gates.size();++j)cout<<(j?",":"")<<count_by_gate[j];
    cout<<"]}\n";
}

void positive_counts(int at,int left) {
    if(at+1==(int)support.size()) {
        count_by_gate[support[at]]=left;
        emit_if_valid();
        return;
    }
    int remaining=int(support.size())-at-1;
    for(int n=1;n<=left-remaining;++n) {
        count_by_gate[support[at]]=n;
        positive_counts(at+1,left-n);
    }
}

bool invariant_proper_space_exists() {
    for(int space:spaces) {
        bool invariant=true;
        for(int v=1;v<16 && invariant;++v)if((space>>v)&1)
            for(int j:support) {
                int image=__builtin_parity(unsigned(v&gates[j].y))?gates[j].x:0;
                if(!((space>>image)&1)){invariant=false;break;}
            }
        if(invariant)return true;
    }
    return false;
}

int choose(int n,int k) {
    int out=1;
    for(int i=1;i<=k;++i)out=out*(n-i+1)/i;
    return out;
}

int main(int argc,char**argv) {
    if(argc!=2 && argc!=3)return 2;
    int required_rank=argc==3?stoi(argv[2]):3;
    if(required_rank!=2 && required_rank!=3)return 2;
    set<int> unique_spaces;
    for(int a=1;a<16;++a)for(int b=0;b<16;++b)for(int c=0;c<16;++c) {
        int mask=0;
        for(int subset=0;subset<8;++subset)
            mask|=1<<(((subset&1)?a:0)^((subset&2)?b:0)^((subset&4)?c:0));
        if(mask!=65535)unique_spaces.insert(mask);
    }
    spaces.assign(unique_spaces.begin(),unique_spaces.end());
    if(spaces.size()!=65)return 3;
    ifstream input(argv[1]);int classes;
    if(!(input>>classes))return 4;
    for(class_id=0;class_id<classes;++class_id) {
        int n;input>>n;gates.resize(n);
        for(auto &gate:gates) {
            int ignored;input>>gate.x>>gate.y>>ignored;gate.matrix=0;
            for(int i=0;i<4;++i)if((gate.x>>i)&1)gate.matrix|=gate.y<<(4*i);
        }
        if(!input)return 5;
        for(int selected=1;selected<(1<<n);++selected) {
            int size=__builtin_popcount(unsigned(selected));
            if(size>8)continue;
            all_multisets+=choose(7,size-1);
            support.clear();
            vector<int> off;
            for(int i=0;i<n;++i)if((selected>>i)&1) {
                support.push_back(i);off.push_back(gates[i].matrix&0x7bde);
            }
            if(rank_binary(off)!=required_rank)continue;
            allowed_roles=0;
            for(int a=0;a<4;++a) {
                vector<int> rows;
                for(int i:support)rows.push_back(gates[i].matrix&(0x7bde|(1<<(5*a))));
                if(rank_binary(rows)<=3)allowed_roles|=1<<a;
            }
            if(!allowed_roles || invariant_proper_space_exists())continue;
            count_by_gate.assign(n,0);positive_counts(0,8);
        }
    }
    int extra;if(input>>extra)return 6;
    cerr<<"{\"classes\":"<<classes<<",\"multisets\":"<<all_multisets
        <<",\"accepted\":"<<accepted<<",\"proper_subspaces\":"<<spaces.size()<<"}\n";
}
