// Complete bounded census. Tairitsu-Aya, OpenAI Codex assistance. Apache-2.0.
// Expand weight-two calls to singleton walks, then hide disjoint midpoints.
// No negative mathematical claim without a completed, independently checked census.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;
struct Search {
    int n, length, calls, remove, shard, shards, cut, maximum_count;
    double seconds;
    bool unit_only, timed_out = false, found = false;
    Clock::time_point start = Clock::now(), last = start;
    uint64_t nodes = 0, words = 0, full_words = 0, candidates = 0;
    uint64_t profile_four = 0, profile_six = 0;
    int best_unit = 0, best_screened = 0, max_eligible = 0;
    std::array<int, 6> counts{};
    std::array<int, 16> labels{}, prefixes{};
    std::vector<int> eligible, deleted, witness_steps, witness_prefixes, witness_unit, witness_deleted;
    std::vector<uint64_t> full_codes;

    Search(int nn, int ll, int kk, int ss, int ns, double tt, bool only)
        : n(nn), length(ll), calls(kk), remove(ll-kk), shard(ss), shards(ns),
          cut(std::min(6,ll)), maximum_count(ll-2*(nn-1)), seconds(tt), unit_only(only) {
        if (n<1 || n>6 || length<2*n || length>16 || length%2 || calls<1 ||
            remove<0 || 2*remove>length || shard<0 || shard>=shards || seconds<=0)
            throw std::runtime_error("invalid finite search domain");
    }

    double elapsed() const { return std::chrono::duration<double>(Clock::now()-start).count(); }
    uint64_t full() const { return n==6 ? ~uint64_t(0) : (uint64_t(1)<<(1<<n))-1; }
    bool adjacent(int a, int b) const { return (a+1)%length==b || (b+1)%length==a; }

    void report(const std::string &status) const {
        std::cout << "{\"status\":\""<<status<<"\",\"n\":"<<n
                  <<",\"unit_steps\":"<<length<<",\"target_calls\":"<<calls
                  <<",\"shard\":"<<shard<<",\"shards\":"<<shards
                  <<",\"elapsed_seconds\":"<<elapsed()<<",\"nodes\":"<<nodes
                  <<",\"unit_words\":"<<words<<",\"full_coverage_unit_words\":"<<full_words
                  <<",\"profile_max_four\":"<<profile_four<<",\"profile_max_six\":"<<profile_six
                  <<",\"tested_deletion_sets\":"<<candidates<<",\"max_unit_coverage\":"<<best_unit
                  <<",\"max_screened_retained_coverage\":"<<best_screened
                  <<",\"max_individually_removable\":"<<max_eligible;
        auto list = [](const char* name, const std::vector<int>& values) {
            std::cout << ",\""<<name<<"\":[";
            for (size_t i=0;i<values.size();++i) std::cout<<(i?",":"")<<values[i];
            std::cout << "]";
        };
        list("witness_steps",witness_steps); list("witness_prefixes",witness_prefixes);
        list("witness_unit_labels",witness_unit); list("deleted_prefix_indices",witness_deleted);
        std::cout << "}" << std::endl;
    }

    void save_witness(uint32_t hidden) {
        int begin=0;
        while (hidden & (uint32_t(1)<<begin)) ++begin;
        int here=begin;
        witness_steps.clear(); witness_prefixes.clear();
        do {
            witness_prefixes.push_back(prefixes[here]^prefixes[begin]);
            int next=(here+1)%length;
            while (hidden & (uint32_t(1)<<next)) next=(next+1)%length;
            witness_steps.push_back(prefixes[here]^prefixes[next]);
            here=next;
        } while(here!=begin);
        int weight=0, parity=0;
        for (int step:witness_steps) {
            int w=__builtin_popcount(unsigned(step));
            if(w<1 || w>2) throw std::runtime_error("invalid reconstructed call");
            weight+=w; parity^=step;
        }
        if (int(witness_steps.size())!=calls || weight!=length || parity)
            throw std::runtime_error("reconstructed word does not match its bill");
        witness_unit.assign(labels.begin(),labels.begin()+length);
        witness_deleted=deleted;
        found=true;
    }

    void choose_deletions(int offset, uint32_t hidden) {
        if(found || timed_out) return;
        if(int(deleted.size())==remove) {
            ++candidates;
            uint64_t coverage=1;
            for(int i=0;i<length;++i) if(!(hidden&(uint32_t(1)<<i)))
                for(int j=0;j<i;++j) if(!(hidden&(uint32_t(1)<<j)))
                    coverage |= uint64_t(1)<<(prefixes[i]^prefixes[j]);
            best_screened=std::max(best_screened,__builtin_popcountll(coverage));
            if(coverage==full()) save_witness(hidden);
            return;
        }
        int need=remove-int(deleted.size());
        for(int k=offset;k+need<=int(eligible.size());++k) {
            int v=eligible[k]; bool bad=false;
            for(int old:deleted) if(adjacent(v,old)) bad=true;
            if(bad) continue;
            deleted.push_back(v);
            choose_deletions(k+1,hidden|(uint32_t(1)<<v));
            deleted.pop_back();
            if(found) return;
        }
    }

    void retained_screen() {
        std::array<int,64> multiplicity{};
        for(int i=0;i<length;++i)
            for(int j=0;j<i;++j) ++multiplicity[prefixes[i]^prefixes[j]];
        eligible.clear(); deleted.clear();
        for(int v=0;v<length;++v) {
            // Hiding q_v merges its preceding and following singleton calls.
            if(labels[(v+length-1)%length]==labels[v]) continue;
            bool loses=false;
            for(int j=0;j<length;++j) if(j!=v) {
                int d=prefixes[v]^prefixes[j];
                if(--multiplicity[d]==0 && d) loses=true;
            }
            for(int j=0;j<length;++j) if(j!=v) ++multiplicity[prefixes[v]^prefixes[j]];
            if(!loses) eligible.push_back(v);
        }
        max_eligible=std::max(max_eligible,int(eligible.size()));
        if(int(eligible.size())>=remove) choose_deletions(0,0);
    }

    void dfs(int pos, int seen, int parity, uint64_t coverage) {
        if(found || timed_out) return;
        ++nodes;
        if((nodes & 131071)==0) {
            auto now=Clock::now();
            if(std::chrono::duration<double>(now-start).count()>=seconds) {timed_out=true;return;}
            if(std::chrono::duration<double>(now-last).count()>=10) {report("RUNNING");last=now;}
        }
        if(pos==cut && shards>1) {
            uint64_t code=1469598103934665603ULL;
            for(int i=0;i<cut;++i) {code^=unsigned(labels[i]+1);code*=1099511628211ULL;}
            if(int(code%unsigned(shards))!=shard) return;
        }
        if(pos==length) {
            if(seen!=n || parity) return;
            for(int i=0;i<n;++i) if(counts[i]<2 || counts[i]%2) return;
            ++words;
            int largest=*std::max_element(counts.begin(),counts.begin()+n);
            profile_four+=(largest==4);profile_six+=(largest==6);
            best_unit=std::max(best_unit,__builtin_popcountll(coverage));
            if(coverage==full()) {
                ++full_words;
                uint64_t code=0;
                for(int i=0;i<length;++i) code|=uint64_t(labels[i])<<(3*i);
                full_codes.push_back(code);
                if(!unit_only) retained_screen();
            }
            return;
        }
        for(int lab=0;lab<std::min(seen+1,n);++lab) {
            if(counts[lab]>=maximum_count) continue;
            ++counts[lab];
            int required=0;
            for(int i=0;i<n;++i) required+=counts[i]?counts[i]+(counts[i]&1):2;
            if(required<=length) {
                labels[pos]=lab;
                int next=parity^(1<<lab);
                uint64_t changed=coverage;
                if(pos+1<length) {
                    prefixes[pos+1]=next;
                    for(int j=0;j<=pos;++j) changed|=uint64_t(1)<<(next^prefixes[j]);
                }
                dfs(pos+1,std::max(seen,lab+1),next,changed);
            }
            --counts[lab];
            if(found || timed_out) return;
        }
    }

    void run() {
        dfs(0,0,0,1);
        report(found?"FOUND":timed_out?"TIMEOUT":"EXHAUSTED");
    }

    void write_codes(const std::string &path) {
        std::ifstream prior(path,std::ios::binary);
        if(prior.good()) throw std::runtime_error("output already exists");
        std::sort(full_codes.begin(),full_codes.end());
        std::ofstream out(path,std::ios::binary);
        if(!out) throw std::runtime_error("cannot create full-cover output");
        for(uint64_t code:full_codes)
            for(int i=0;i<8;++i) out.put(char((code>>(8*i))&255));
        if(!out) throw std::runtime_error("full-cover output failed");
    }
};

uint64_t coverage(const std::vector<int>& points) {
    uint64_t bits=1;
    for(int a:points) for(int b:points) bits|=uint64_t(1)<<(a^b);
    return bits;
}

void selftest() {
    std::vector<int> old={2,16,8,16,1,4,48,4,3,4,32,8,4,16};
    std::vector<int> unit,hidden,points={0}; int q=0;
    for(int step:old) {
        std::vector<int> bits;
        for(int j=0;j<6;++j) if(step&(1<<j)) bits.push_back(j);
        for(size_t j=0;j<bits.size();++j) {
            unit.push_back(bits[j]); q^=1<<bits[j]; points.push_back(q);
            if(j+1<bits.size()) hidden.push_back(int(unit.size()));
        }
    }
    points.pop_back();
    std::vector<int> retained;
    for(int i=0;i<16;++i) if(std::find(hidden.begin(),hidden.end(),i)==hidden.end()) retained.push_back(points[i]);
    if(unit.size()!=16 || hidden.size()!=2 || q || coverage(retained)!=~uint64_t(0))
        throw std::runtime_error("retained fourteen-call positive control");
    Search tiny(3,6,5,0,1,30,false);tiny.run();
    if(!tiny.found) throw std::runtime_error("three-source five-call positive control");
    Search count(6,12,12,0,1,30,true);count.run();
    if(count.timed_out || count.words!=10395 || count.best_unit!=49)
        throw std::runtime_error("10395-word six-source singleton census control");
    std::cout<<"{\"status\":\"PASS_SELFTEST\",\"retained_fourteen_call_control\":true}"<<std::endl;
}

int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="selftest") {selftest();return 0;}
        if(argc!=9) throw std::runtime_error("arguments: n W k shard shards seconds search|unit NEW_OUTPUT");
        Search job(std::stoi(argv[1]),std::stoi(argv[2]),std::stoi(argv[3]),std::stoi(argv[4]),
                   std::stoi(argv[5]),std::stod(argv[6]),std::string(argv[7])=="unit");
        job.run();job.write_codes(argv[8]);return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<std::endl;return 2;}
}
