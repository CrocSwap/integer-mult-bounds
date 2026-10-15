// Independent complete even-block partition census; no restricted-growth DFS.
// Full difference sets use bitset translations, not source-pair accumulation.
// Tairitsu-Aya, substantial OpenAI Codex assistance. Apache-2.0.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

uint64_t translate(uint64_t v,unsigned x) {
    if(x&1) v=((v&0x5555555555555555ULL)<<1)|((v&0xAAAAAAAAAAAAAAAAULL)>>1);
    if(x&2) v=((v&0x3333333333333333ULL)<<2)|((v&0xCCCCCCCCCCCCCCCCULL)>>2);
    if(x&4) v=((v&0x0F0F0F0F0F0F0F0FULL)<<4)|((v&0xF0F0F0F0F0F0F0F0ULL)>>4);
    if(x&8) v=((v&0x00FF00FF00FF00FFULL)<<8)|((v&0xFF00FF00FF00FF00ULL)>>8);
    if(x&16) v=((v&0x0000FFFF0000FFFFULL)<<16)|((v&0xFFFF0000FFFF0000ULL)>>16);
    if(x&32) v=(v<<32)|(v>>32);
    return v;
}

struct Census {
    int n,length;
    std::array<int,16> word{};
    uint64_t words=0,full_words=0,profile_four=0,profile_six=0;
    int best=0, profile=0;
    std::vector<uint64_t> complete;
    std::chrono::steady_clock::time_point start=std::chrono::steady_clock::now();
    Census(int a,int b):n(a),length(b) {}

    void endpoint() {
        ++words;
        profile_four+=(profile==4);profile_six+=(profile==6);
        uint64_t points=1;unsigned point=0;
        for(int j=0;j<length-1;++j) {point^=1u<<word[j];points|=uint64_t(1)<<point;}
        point^=1u<<word.at(static_cast<size_t>(length-1));
        if(point) throw std::runtime_error("even-block word failed restoration");
        const uint64_t full=n==6?~uint64_t(0):(uint64_t(1)<<(1<<n))-1;
        uint64_t differences=0, pending=points;
        while(pending) {
            unsigned p=__builtin_ctzll(pending);pending&=pending-1;
            differences |= translate(points,p);
            if(differences==full) break;
        }
        best=std::max(best,__builtin_popcountll(differences));
        if(differences==full) {
            ++full_words;uint64_t code=0;
            for(int j=0;j<length;++j) code|=uint64_t(word[j])<<(3*j);
            complete.push_back(code);
        }
    }

    void partition(uint32_t unassigned,int label,int twos,int fours,int sixes) {
        if(!unassigned) {
            if(label!=n || twos || fours || sixes) throw std::runtime_error("wrong partition profile");
            endpoint();return;
        }
        int first=__builtin_ctz(unassigned);
        uint32_t root=uint32_t(1)<<first, rest=unassigned^root;
        if(twos) choose(rest,1,root,unassigned,label,twos-1,fours,sixes);
        if(fours) choose(rest,3,root,unassigned,label,twos,fours-1,sixes);
        if(sixes) choose(rest,5,root,unassigned,label,twos,fours,sixes-1);
    }

    void choose(uint32_t options,int need,uint32_t block,uint32_t unassigned,
                int label,int twos,int fours,int sixes) {
        if(!need) {
            uint32_t bits=block;
            while(bits) {int p=__builtin_ctz(bits);bits&=bits-1;word[p]=label;}
            partition(unassigned^block,label+1,twos,fours,sixes);return;
        }
        while(__builtin_popcount(options)>=need) {
            uint32_t bit=options & -options;options^=bit;
            choose(options,need-1,block|bit,unassigned,label,twos,fours,sixes);
        }
    }

    void run() {
        uint32_t all=(uint32_t(1)<<length)-1;
        if(length==2*n) {profile=2;partition(all,0,n,0,0);}
        else if(length==2*n+2) {profile=4;partition(all,0,n-1,1,0);}
        else if(length==2*n+4) {
            profile=4;partition(all,0,n-2,2,0);
            profile=6;partition(all,0,n-1,0,1);
        } else throw std::runtime_error("unsupported exact multiplicity domain");
    }

    void finish(const std::string& path) {
        std::sort(complete.begin(),complete.end());
        if(std::adjacent_find(complete.begin(),complete.end())!=complete.end())
            throw std::runtime_error("partition enumeration duplicated a word");
        std::ifstream old(path,std::ios::binary);
        if(old.good()) throw std::runtime_error("output already exists");
        std::ofstream out(path,std::ios::binary);
        if(!out) throw std::runtime_error("cannot create audit output");
        for(uint64_t code:complete) for(int j=0;j<8;++j) out.put(char((code>>(8*j))&255));
        if(!out) throw std::runtime_error("audit output failed");
        double duration=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        std::cout<<"{\"status\":\"EXHAUSTED\",\"n\":"<<n<<",\"unit_steps\":"<<length
                 <<",\"unit_words\":"<<words<<",\"full_coverage_unit_words\":"<<full_words
                 <<",\"max_unit_coverage\":"<<best<<",\"profile_max_four\":"<<profile_four
                 <<",\"profile_max_six\":"<<profile_six<<",\"elapsed_seconds\":"<<duration<<"}"<<std::endl;
    }
};

int main(int argc,char** argv) {
    try {
        for(unsigned a=0;a<64;++a) for(unsigned b=0;b<64;++b)
            if(translate(uint64_t(1)<<a,b)!=(uint64_t(1)<<(a^b)))
                throw std::runtime_error("XOR translation truth-table control");
        if(argc!=4) throw std::runtime_error("arguments: n W NEW_OUTPUT");
        int n=std::stoi(argv[1]),w=std::stoi(argv[2]);
        if(n<2 || n>6 || w>16 || w<2*n || w%2) throw std::runtime_error("invalid census domain");
        Census census(n,w);census.run();census.finish(argv[3]);return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<std::endl;return 2;}
}
