// Exact weighted balls in M_2(F2[S4]). Apache-2.0.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace {
using Perm = std::array<unsigned, 4>;
struct State {
    std::array<std::uint32_t, 4> a{};
    bool operator==(const State& other) const { return a == other.a; }
};
struct Hash {
    std::size_t operator()(const State& s) const {
        std::uint64_t h = 1469598103934665603ULL;
        for (auto x : s.a) { h ^= x; h *= 1099511628211ULL; }
        return static_cast<std::size_t>(h);
    }
};
struct Call { unsigned u, v, cost, group_index; };
constexpr std::size_t CAP = 2000000;
using Ball = std::unordered_map<State, unsigned char, Hash>;
std::array<Perm, 24> group{};
std::array<std::array<std::array<std::uint32_t, 256>, 3>, 24> lut{};
std::array<Call, 18> calls{};

void need(bool b, const char* why) { if (!b) throw std::runtime_error(why); }
unsigned index(const Perm& p) {
    auto it = std::find(group.begin(), group.end(), p);
    need(it != group.end(), "permutation index");
    return static_cast<unsigned>(it - group.begin());
}
Perm compose(const Perm& a, const Perm& b) {
    Perm c{};
    for (unsigned i=0; i<4; ++i) c[i]=a[b[i]];
    return c;
}
void init() {
    Perm p{0,1,2,3};
    unsigned k=0;
    do {
        need(k<24, "bounded permutation inventory");
        group[k++]=p;
    } while (std::next_permutation(p.begin(), p.end()));
    need(k==24, "group order");
    for (unsigned g=0; g<24; ++g)
        for (unsigned chunk=0; chunk<3; ++chunk)
            for (unsigned mask=0; mask<256; ++mask) {
                std::uint32_t x=0;
                for (unsigned bit=0; bit<8; ++bit)
                    if ((mask>>bit)&1U)
                        x ^= std::uint32_t{1} << index(compose(group[g],group[chunk*8+bit]));
                lut[g][chunk][mask]=x;
            }
    k=0;
    for (unsigned label=0; label<3; ++label)
        for (unsigned u=1; u<4; ++u)
            for (unsigned v=1; v<4; ++v) {
                unsigned x=u&v;
                if (((x&1U)^((x>>1)&1U))!=0) {
                    need(k<calls.size(), "bounded call inventory");
                    Perm s{0,1,2,3}; std::swap(s[label],s[label+1]);
                    calls[k++]={u,v,label==1 ? 1U : 2U,index(s)};
                }
            }
    need(k==18, "call inventory");
}
std::uint32_t translate(std::uint32_t x, unsigned g) {
    return lut[g][0][x&255U] ^ lut[g][1][(x>>8)&255U] ^ lut[g][2][x>>16];
}
State step(State s, const Call& c) {
    const unsigned g=c.group_index;
    for (unsigned col=0; col<2; ++col) {
        std::uint32_t x=0;
        for (unsigned row=0; row<2; ++row)
            if ((c.v>>row)&1U) x ^= s.a[2*row+col];
        x ^= translate(x,g);
        for (unsigned row=0; row<2; ++row)
            if ((c.u>>row)&1U) s.a[2*row+col] ^= x;
    }
    return s;
}
State target_times(State s, unsigned w0, unsigned w1) {
    for (unsigned col=0; col<2; ++col) {
        s.a[col]=translate(s.a[col],w0);
        s.a[2+col]=translate(s.a[2+col],w1);
    }
    return s;
}
void build(unsigned radius, Ball& ball, std::vector<std::vector<State>>& layers) {
    State e{{1,0,0,1}};
    ball.reserve(CAP); ball.emplace(e,0); layers[0].push_back(e);
    for (unsigned cost=1; cost<=radius; ++cost) {
        for (const auto& c : calls) {
            if (c.cost>cost) continue;
            for (const auto& s : layers[cost-c.cost]) {
                State t=step(s,c);
                if (ball.find(t)==ball.end()) {
                    need(ball.size()<CAP, "state capacity exhausted; no exclusion certified");
                    ball.emplace(t,static_cast<unsigned char>(cost));
                    layers[cost].push_back(t);
                }
            }
        }
        std::cerr << "layer " << cost << " " << layers[cost].size() << "\n";
    }
}
std::array<unsigned,24> direct_distances() {
    std::array<unsigned,24> d{}; d.fill(100); d[0]=0;
    // Bellman relaxation on 24 vertices, with positive integer edge costs.
    for (unsigned round=0; round<24; ++round)
        for (unsigned g=0; g<24; ++g)
            for (unsigned label=0; label<3; ++label) {
                Perm s{0,1,2,3}; std::swap(s[label],s[label+1]);
                unsigned h=index(compose(s,group[g]));
                d[h]=std::min(d[h],d[g]+(label==1 ? 1U : 2U));
            }
    return d;
}
unsigned cut_bound(const Perm& p) {
    unsigned q=0;
    for (unsigned i=0; i<4; ++i)
        for (unsigned j=i+1; j<4; ++j) q += p[i]>p[j] ? 1U : 0U;
    return q + (p[0]!=0 ? 1U : 0U) + (p[3]!=3 ? 1U : 0U);
}
void query(const Ball& ball, const std::vector<std::vector<State>>& layers,
           unsigned a, unsigned b, unsigned direct, unsigned lower) {
    unsigned best=100;
    std::uint64_t hits=0;
    for (unsigned cost=0; cost<layers.size(); ++cost)
        for (const auto& s : layers[cost]) {
            auto it=ball.find(target_times(s,a,b));
            if (it!=ball.end()) {
                ++hits;
                best=std::min(best,cost+static_cast<unsigned>(it->second));
            }
        }
    std::cout << '[' << a << ',' << b << ',' << direct << ',' << lower
              << ',' << best << ',' << hits << ']';
}
} // namespace

int main(int argc, char** argv) {
    try {
        unsigned radius=9;
        bool dump_small=false;
        need(argc<=2, "expected at most one argument");
        if (argc==2) {
            std::string arg=argv[1];
            dump_small=(arg=="--dump-small");
            if (dump_small) radius=4;
            else {
                need(arg.size()==1 && arg[0]>='1' && arg[0]<='9', "radius must be 1..9");
                radius=static_cast<unsigned>(arg[0]-'0');
            }
        }
        init(); Ball ball;
        std::vector<std::vector<State>> layers(radius+1);
        build(radius,ball,layers);
        auto distances=direct_distances();
        std::cout << "{\"radius\":" << radius << ",\"layers\":[";
        for (unsigned i=0; i<=radius; ++i) {
            if (i) std::cout << ',';
            std::cout << layers[i].size();
        }
        std::cout << "],\"states\":" << ball.size() << ",\"queries\":[";
        bool first=true;
        for (unsigned a=0; a<24; ++a)
            for (unsigned b=a; b<24; ++b) {
                unsigned direct=distances[a]+distances[b];
                unsigned lower=cut_bound(group[a])+cut_bound(group[b]);
                if (direct==lower) continue;
                if (!first) std::cout << ',';
                first=false;
                query(ball,layers,a,b,direct,lower);
            }
        std::cout << ']';
        if (dump_small) {
            std::cout << ",\"small_states\":[";
            first=true;
            for (unsigned cost=0; cost<=4; ++cost)
                for (const auto& s : layers[cost]) {
                    if (!first) std::cout << ',';
                    first=false;
                    std::cout << '[' << s.a[0] << ',' << s.a[1] << ','
                              << s.a[2] << ',' << s.a[3] << ',' << cost << ']';
                }
            std::cout << ']';
        }
        std::cout << "}\n";
        need(std::cout.good(), "receipt output failed");
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n'; return 1;
    }
}
