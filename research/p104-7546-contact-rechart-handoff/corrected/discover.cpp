// SPDX-License-Identifier: Apache-2.0
// Contact-level adaptation of 1337isnot1337/OpenAI Codex's discover-cut.cpp.
// Rohan Arun's #7122/#7124 boundary objective; OpenAI Pro/Codex assistance.
// Floating nomination only. All candidates require independent exact checks.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using namespace std;

struct Arc { int to, rev; double capacity; };
struct Flow {
    vector<vector<Arc>> adjacency;
    vector<int> level, cursor;
    explicit Flow(int n): adjacency(n), level(n), cursor(n) {}
    void edge(int u, int v, double capacity) {
        if (capacity < -1e-7) throw runtime_error("negative capacity");
        Arc a{v, int(adjacency[v].size()), max(0., capacity)};
        Arc b{u, int(adjacency[u].size()), 0.};
        adjacency[u].push_back(a); adjacency[v].push_back(b);
    }
    double send(int u, int sink, double amount) {
        if (u == sink) return amount;
        for (int &i=cursor[u]; i<int(adjacency[u].size()); ++i) {
            Arc &a=adjacency[u][i];
            if (a.capacity <= 1e-9 || level[a.to] != level[u]+1) continue;
            double pushed=send(a.to, sink, min(amount, a.capacity));
            if (pushed > 1e-9) {
                a.capacity-=pushed; adjacency[a.to][a.rev].capacity+=pushed;
                return pushed;
            }
        }
        return 0.;
    }
    vector<bool> cut(int source, int sink) {
        for (;;) {
            fill(level.begin(),level.end(),-1);
            queue<int> q; q.push(source); level[source]=0;
            while (!q.empty()) {
                int u=q.front(); q.pop();
                for (const auto &a:adjacency[u])
                    if (a.capacity>1e-9 && level[a.to]<0) {
                        level[a.to]=level[u]+1; q.push(a.to);
                    }
            }
            if (level[sink]<0) {
                vector<bool> reached(level.size());
                for (int i=0;i<int(level.size());++i) reached[i]=level[i]>=0;
                return reached;
            }
            fill(cursor.begin(),cursor.end(),0);
            while (send(source,sink,1e30)>1e-9) {}
        }
    }
};

struct Node { bool entry, exit; int before, after; };
struct Model {
    vector<int> dimension;
    vector<array<unsigned long long,8>> spaces;
    vector<vector<bool>> legal;
    vector<Node> nodes;
    vector<pair<int,int>> edges;
    vector<pair<int,int>> targets;
    array<double,10> price{};
    double penalty=0.;

    void prepare(double exponent) {
        if (!(exponent>0. && exponent<1.)) throw runtime_error("tariff");
        for (int r=0;r<=9;++r) price[r]=pow(r,exponent);
        int f=int(spaces.size()); legal.assign(f,vector<bool>(f));
        for (int a=0;a<f;++a) for (int b=0;b<f;++b) {
            bool subset=true;
            for (int k=0;k<8;++k) if (spaces[a][k]&~spaces[b][k]) subset=false;
            legal[a][b]=(a==b || (dimension[a]<dimension[b] && subset));
        }
        penalty=36.*(edges.size()+targets.size()+1.);
    }
    double paid(int a, int b) const {
        if (!legal[a][b]) return penalty;
        int rank=dimension[b]-dimension[a];
        if (rank<0 || rank>9) throw runtime_error("rank index");
        return price[rank];
    }
    double target(int a, int b) const {
        return legal[a][b] && dimension[a]<dimension[b]
            ? -price[dimension[b]-dimension[a]] : penalty;
    }
};

struct Proposal { vector<bool> switched; double delta; bool valid; };

Proposal expand(const Model &m, int label, bool entry) {
    vector<int> index(m.nodes.size(),-1), reverse;
    for (int i=0;i<int(m.nodes.size());++i)
        if (entry?m.nodes[i].entry:m.nodes[i].exit) {
            index[i]=int(reverse.size()); reverse.push_back(i);
        }
    int v=int(reverse.size()), source=v, sink=v+1;
    Flow flow(v+2); vector<double> unary(v);
    for (auto [a,b]:m.edges) {
        int fa=m.nodes[a].after, fb=m.nodes[b].before;
        double e00=m.paid(fa,fb), e10=m.paid(label,fb), e01=m.paid(fa,label);
        int i=index[a], j=index[b];
        if (i>=0 && j>=0) {
            double capacity=e10+e01-e00;
            if (capacity < -1e-7) throw runtime_error("non-submodular paid edge");
            unary[i]-=e01; unary[j]+=e01-e00;
            flow.edge(i,j,max(0.,capacity));
        } else if (i>=0) unary[i]+=e10-e00;
        else if (j>=0) unary[j]+=e01-e00;
    }
    for (auto [a,b]:m.targets) {
        int node=entry?a:b, i=index[node];
        if (i<0) continue; // This mode's fixed target is a constant, never a unary.
        double old=m.target(m.nodes[a].before,m.nodes[b].before);
        double now=entry?m.target(label,m.nodes[b].before):m.target(m.nodes[a].before,label);
        unary[i]+=now-old;
    }
    for (int i=0;i<v;++i)
        if (unary[i]<0) flow.edge(source,i,-unary[i]);
        else flow.edge(i,sink,unary[i]);
    auto reached=flow.cut(source,sink);
    vector<bool> switched(m.nodes.size());
    for (int i=0;i<v;++i) switched[reverse[i]]=reached[i];
    double delta=0.; bool valid=true;
    for (auto [a,b]:m.edges) {
        int fa=m.nodes[a].after, fb=m.nodes[b].before;
        int ga=switched[a]?label:fa, gb=switched[b]?label:fb;
        valid=valid && m.legal[ga][gb]; delta+=m.paid(ga,gb)-m.paid(fa,fb);
    }
    for (auto [a,b]:m.targets) {
        int fa=m.nodes[a].before, fb=m.nodes[b].before;
        int ga=switched[a]?label:fa, gb=switched[b]?label:fb;
        valid=valid && m.legal[ga][gb] && m.dimension[ga]<m.dimension[gb];
        delta+=m.target(ga,gb)-m.target(fa,fb);
    }
    return {switched,delta,valid};
}

Model input(istream &in, double exponent) {
    int f,n,e,h; in>>f>>n>>e>>h;
    if (!(f>0 && f<10000 && n>0 && e>=0 && h>=0)) throw runtime_error("header");
    Model m; m.dimension.resize(f); m.spaces.resize(f); m.nodes.resize(n);
    for (int i=0;i<f;++i) {
        in>>m.dimension[i]; for (auto &b:m.spaces[i]) in>>b;
        if (m.dimension[i]<0 || m.dimension[i]>9) throw runtime_error("dimension");
    }
    for (auto &node:m.nodes) in>>node.entry>>node.exit>>node.before>>node.after;
    for (int i=0,a,b;i<e;++i) { in>>a>>b; m.edges.push_back({a,b}); }
    for (int i=0,a,b;i<h;++i) { in>>a>>b; m.targets.push_back({a,b}); }
    if (!in) throw runtime_error("truncated input");
    m.prepare(exponent); return m;
}

double assignment_cost(const Model &m, int label, const vector<bool> &switched) {
    double result=0.;
    for (auto [a,b]:m.edges)
        result+=m.paid(switched[a]?label:m.nodes[a].after,
                       switched[b]?label:m.nodes[b].before);
    for (auto [a,b]:m.targets)
        result+=m.target(switched[a]?label:m.nodes[a].before,
                         switched[b]?label:m.nodes[b].before);
    return result;
}

void selftest(double exponent) {
    Model m; m.dimension={0,1,1,2,3}; m.spaces.resize(5);
    for (int i=0;i<5;++i) {
        vector<int> values=i==0?vector<int>{0}:i==1?vector<int>{0,1}:
            i==2?vector<int>{0,2}:i==3?vector<int>{0,1,2,3}:vector<int>{0,1,2,3,4,5,6,7};
        for (int x:values) m.spaces[i][0]|=1ULL<<x;
    }
    int cases=0;
    for (bool entry:{true,false}) for (bool zero:{true,false}) {
        m.nodes={{entry,false,0,0},{true,true,zero?0:1,zero?0:1},
                 {true,true,3,3},{false,!entry,4,4}};
        m.edges={{0,1},{1,2},{2,3}}; m.targets={{0,3}}; m.prepare(exponent);
        for (int label=0;label<5;++label) {
            auto proposal=expand(m,label,entry);
            vector<bool> none(4); double base=assignment_cost(m,label,none), best=base;
            for (int mask=0;mask<16;++mask) {
                vector<bool> choice(4); bool allowed=true;
                for (int i=0;i<4;++i) if (mask&(1<<i)) {
                    choice[i]=true; allowed=allowed && (entry?m.nodes[i].entry:m.nodes[i].exit);
                }
                if (allowed) best=min(best,assignment_cost(m,label,choice));
            }
            if (!proposal.valid || abs(base+proposal.delta-best)>1e-6)
                throw runtime_error("cut/brute-force control mismatch");
            ++cases;
        }
    }
    if (m.legal[1][2] || m.target(1,1)<m.penalty) throw runtime_error("illegal/zero target");
    if (m.target(0,4) != -m.price[3] || m.target(1,4)-m.target(0,4)<=0.)
        throw runtime_error("productive credit sign");
    if (2.*m.price[1]-m.price[2]<=0.) throw runtime_error("joint boundary control");
    m.nodes[0].entry=false; m.nodes[3].exit=false;
    if (!expand(m,0,true).valid) throw runtime_error("pinned target unary control");
    m.dimension.push_back(1); m.spaces.push_back(m.spaces[1]); m.prepare(exponent);
    if (m.legal[1][5] || m.legal[5][1]) throw runtime_error("equal-span ID adapter");
    cout<<"PASS_CUT_CONTROLS "<<cases<<" differing_labels zero_links forbidden_nesting joint_target_sign\n";
}

int main(int argc,char **argv) {
    try {
        if (argc!=3 && argc!=4) throw runtime_error("usage: exponent --selftest | exponent graph proposal");
        double exponent=stod(argv[1]);
        if (string(argv[2])=="--selftest") { selftest(exponent); return 0; }
        if (argc!=4) throw runtime_error("proposal path");
        ifstream source(argv[2]); Model m=input(source,exponent);
        for (bool entry:{true,false}) for (int label=0;label<int(m.spaces.size());++label) {
            auto proposal=expand(m,label,entry);
            cout<<"VISIT "<<(entry?"entry":"exit")<<" "<<label<<" "
                <<setprecision(17)<<proposal.delta<<" "<<proposal.valid<<endl;
            if (proposal.valid && proposal.delta < -1e-8) {
                ofstream out(argv[3]); out<<(entry?"entry":"exit")<<" "<<label<<"\n";
                for (int i=0;i<int(m.nodes.size());++i) if (proposal.switched[i]) out<<i<<"\n";
                if (!out) throw runtime_error("proposal write");
                cout<<"FLOAT_NOMINEE_ONLY\n"; return 0;
            }
        }
        cout<<"NO_FLOAT_NOMINEE_IN_FROZEN_TWO_SWEEPS\n";
        return 0;
    } catch (const exception &e) { cerr<<e.what()<<endl; return 2; }
}
