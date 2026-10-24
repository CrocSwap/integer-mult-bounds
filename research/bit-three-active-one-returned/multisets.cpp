#include <array>
#include <fstream>
#include <iostream>
#include <vector>
using namespace std;

struct Projector { int x, y, off; };
vector<Projector> p;
vector<int> counts;
vector<int> irreducible_cache;
long long visited=0, distance_ok=0, rank_ok=0, accepted=0;
int class_index;

int binary_rank(vector<int> a) {
    int pivots[16]={}, rank=0;
    for(int x:a) while(x) {
        int k=31-__builtin_clz((unsigned)x);
        if(pivots[k]) x^=pivots[k];
        else { pivots[k]=x; ++rank; break; }
    }
    return rank;
}

bool irreducible(int support) {
    int &cached=irreducible_cache[support];
    if(cached>=0) return cached;
    for(int start=1;start<16;++start) {
        unsigned span=1u|(1u<<start);
        bool changed=true;
        while(changed) {
            changed=false;
            for(int j=0;j<(int)p.size();++j) if((support>>j)&1) {
                if((span>>p[j].x)&1) continue;
                bool active=false;
                for(int v=0;v<16;++v) if(((span>>v)&1) && __builtin_parity((unsigned)(v&p[j].y))) active=true;
                if(active) {
                    unsigned old=span;
                    for(int v=0;v<16;++v) if((old>>v)&1) span|=1u<<(v^p[j].x);
                    changed=true;
                }
            }
        }
        if(span!=65535) return cached=0;
    }
    return cached=1;
}

void check() {
    ++visited;
    int bad=0, support=0;
    vector<int> off;
    for(int j=0;j<(int)p.size();++j) if(counts[j]) { support|=1<<j; off.push_back(p[j].off); }
    if(binary_rank(off)!=3) return;
    for(int v=1;v<16;++v) {
        int cx=0,cy=0;
        for(int j=0;j<(int)p.size();++j) {
            cx+=counts[j]*__builtin_parity((unsigned)(v&p[j].x));
            cy+=counts[j]*__builtin_parity((unsigned)(v&p[j].y));
        }
        if(cx<3 || cy<3) {
            if(v&(v-1)) return;
            bad|=v;
            if(bad&(bad-1)) return;
        }
    }
    ++distance_ok;
    int possible=0;
    for(int a=0;a<4;++a) if(!bad || bad==(1<<a)) {
        vector<int> augmented;
        for(int j=0;j<(int)p.size();++j) if(counts[j]) augmented.push_back(p[j].off | (((p[j].x>>a)&(p[j].y>>a)&1)<<3));
        if(binary_rank(augmented)<=3) possible|=1<<a;
    }
    if(!possible) return;
    ++rank_ok;
    if(!irreducible(support)) return;
    ++accepted;
    cout << "{\"class\":"<<class_index<<",\"possible_ancilla\":"<<possible<<",\"counts\":[";
    for(int j=0;j<(int)counts.size();++j) cout<<(j?",":"")<<counts[j];
    cout<<"]}\n";
}

void enumerate(int position,int left) {
    if(position+1==(int)p.size()) { counts[position]=left; check(); return; }
    for(int c=0;c<=left;++c) { counts[position]=c; enumerate(position+1,left-c); }
}

int main(int argc,char**argv) {
    if(argc!=2) return 2;
    ifstream input(argv[1]);
    int number; input>>number;
    for(class_index=0;class_index<number;++class_index) {
        int n; input>>n;
        p.resize(n);counts.assign(n,0);irreducible_cache.assign(1<<n,-1);
        for(auto &q:p) input>>q.x>>q.y>>q.off;
        enumerate(0,8);
    }
    cerr<<"{\"classes\":"<<number<<",\"multisets\":"<<visited<<",\"distance_ok\":"<<distance_ok<<",\"rank_ok\":"<<rank_ok<<",\"irreducible\":"<<accepted<<"}\n";
}
