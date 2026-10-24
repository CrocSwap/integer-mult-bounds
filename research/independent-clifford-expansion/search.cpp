// Independent Lagrangian chart descent. Apache-2.0.
// Cinna Davis, with substantial OpenAI Codex assistance.
// Floating discovery only; algebra.py independently replays all accepted moves.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <vector>
using Chart = std::array<unsigned,9>;
struct Edge { int a,b,op,sign; };
unsigned low=511;
int pair(unsigned a,unsigned b) {
    return (__builtin_popcount((a&low)&(b>>9))+
            __builtin_popcount((a>>9)&(b&low)))&1;
}
int rank(const Chart& a,const Chart& b) {
    unsigned piv[18]={}; int count=0;
    for(int k=0;k<18;k++) {
        unsigned v=k<9?a[k]:b[k-9];
        while(v) {
            int p=31-__builtin_clz(v);
            if(piv[p]) v^=piv[p];
            else {piv[p]=v;count++;break;}
        }
    }
    return count-9;
}
Chart turn(Chart a,unsigned axis) {
    for(auto &v:a) if(pair(v,axis)) v^=axis;
    return a;
}
Chart image(const Chart& a,const std::array<unsigned,18>& cols) {
    Chart result{};
    for(int j=0;j<9;j++) for(unsigned v=a[j];v;v&=v-1)
        result[j]^=cols[__builtin_ctz(v)];
    return result;
}
std::array<unsigned,9> dual(const Chart& a) {
    unsigned piv[9]={},lift[9]={};
    for(int bit=0;bit<18;bit++) {
        unsigned v=0,w=1u<<bit;
        for(int j=0;j<9;j++) v|=pair(a[j],w)<<j;
        while(v) {
            int p=31-__builtin_clz(v);
            if(piv[p]) {v^=piv[p];w^=lift[p];}
            else {piv[p]=v;lift[p]=w;break;}
        }
    }
    std::array<unsigned,9> result{};
    for(int j=0;j<9;j++) {
        unsigned v=1u<<j;
        while(v) {int p=31-__builtin_clz(v); if(!piv[p]) std::abort();v^=piv[p];result[j]^=lift[p];}
    }
    return result;
}
int main(int argc,char**argv) {
    if(argc!=4) return 2;
    bool certificate=std::string(argv[1])=="certificate";
    uint64_t seed=certificate?0:std::stoull(argv[1]);int rounds=std::stoi(argv[2]);
    bool plateau=std::stoi(argv[3]);std::mt19937_64 rng(seed);
    int count,edges,ops;std::cin>>count>>edges>>ops;
    std::vector<Chart> charts(count);std::vector<int> fixed(count);
    for(int i=0;i<count;i++) {std::cin>>fixed[i];for(auto&v:charts[i])std::cin>>v;}
    std::vector<std::array<unsigned,18>> maps(ops);
    for(auto&cols:maps)for(auto&v:cols)std::cin>>v;
    std::vector<Edge> es(edges);std::vector<std::vector<int>> adj(count);
    for(int i=0;i<edges;i++) {
        auto&e=es[i];std::cin>>e.a>>e.b>>e.op>>e.sign;
        adj[e.a].push_back(i);if(e.a!=e.b)adj[e.b].push_back(i);
    }
    auto edge_rank=[&](const Edge&e,int at,const Chart& trial) {
        Chart a=e.a==at?trial:charts[e.a];const Chart& b=e.b==at?trial:charts[e.b];
        if(e.op>=0) a=image(a,maps[e.op]);
        return rank(a,b);
    };
    double powers[10];for(int i=0;i<10;i++)powers[i]=std::pow(i,1-.00302177585);
    std::vector<double> costs(edges);std::vector<int> ranks(edges);
    for(int i=0;i<edges;i++) {int r=edge_rank(es[i],-1,charts[0]);ranks[i]=r;costs[i]=es[i].sign*powers[r];}
    if(certificate) {
        using Delta=std::array<int,10>;
        struct Bucket {uint64_t count=0;int node=0;unsigned axis=0;};
        std::map<Delta,Bucket> histogram;uint64_t valid=0,invalid=0;
        for(int node=0;node<count;node++) {
            if(fixed[node])continue;
            auto d=dual(charts[node]);
            for(unsigned functional=1;functional<512;functional++) {
                unsigned axis=0;
                for(unsigned f=functional;f;f&=f-1)axis^=d[__builtin_ctz(f)];
                for(int side=0;side<2;side++) {
                    unsigned move=axis^(side?charts[node][__builtin_ctz(functional)]:0);
                    Chart trial=turn(charts[node],move);Delta delta{};bool ok=true;
                    for(int i:adj[node]) {
                        int r=edge_rank(es[i],node,trial);
                        if(es[i].sign<0 && r==0) {ok=false;break;}
                        if(r)delta[r]+=es[i].sign;
                        if(ranks[i])delta[ranks[i]]-=es[i].sign;
                    }
                    if(!ok) {invalid++;continue;}
                    valid++;auto& bucket=histogram[delta];
                    if(!bucket.count) {bucket.node=node;bucket.axis=move;}
                    bucket.count++;
                }
            }
        }
        std::cout<<"CENSUS "<<valid<<" "<<invalid<<" "<<histogram.size()<<"\n";
        for(auto const& row:histogram) {
            std::cout<<"PAT "<<row.second.count;
            for(int v:row.first)std::cout<<" "<<v;
            std::cout<<" "<<row.second.node<<" "<<row.second.axis<<"\n";
        }
        return 0;
    }
    std::vector<int> order(count);std::iota(order.begin(),order.end(),0);
    std::cout<<std::setprecision(17);
    for(int round=0;round<rounds;round++) {
        std::shuffle(order.begin(),order.end(),rng);int changed=0,strict=0;double total=0;
        for(int node:order) {
            if(fixed[node])continue;
            auto d=dual(charts[node]);double best=0;unsigned chosen=0;uint64_t ties=0;
            for(unsigned functional=1;functional<512;functional++) {
                unsigned axis=0;
                for(unsigned f=functional;f;f&=f-1)axis^=d[__builtin_ctz(f)];
                for(int side=0;side<2;side++) {
                    unsigned move=axis^(side?charts[node][__builtin_ctz(functional)]:0);
                    Chart trial=turn(charts[node],move);double delta=0;bool valid=true;
                    for(int i:adj[node]) {
                        int r=edge_rank(es[i],node,trial);
                        if(es[i].sign<0 && r==0) {valid=false;break;}
                        delta+=es[i].sign*powers[r]-costs[i];
                    }
                    if(!valid)continue;
                    if(delta<best-1e-10) {best=delta;chosen=move;ties=1;}
                    else if(plateau && std::abs(delta-best)<1e-10) {ties++;if(rng()%ties==0)chosen=move;}
                }
            }
            if(chosen && (best < -1e-10 || plateau)) {
                charts[node]=turn(charts[node],chosen);
                for(int i:adj[node]) {int r=edge_rank(es[i],-1,charts[0]);ranks[i]=r;costs[i]=es[i].sign*powers[r];}
                std::cout<<"MOVE "<<round<<" "<<node<<" "<<chosen<<" "<<best<<"\n";
                changed++;strict+=best < -1e-10;total+=best;
            }
        }
        std::cout<<"ROUND "<<round<<" "<<changed<<" "<<strict<<" "<<total<<std::endl;
        if(!changed)break;
    }
}
