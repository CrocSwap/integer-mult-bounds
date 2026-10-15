// Independent colexicographic bit-combination census and XOR-set translations.
// Tairitsu-Aya, substantial OpenAI Codex assistance. Apache-2.0.
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

uint64_t shifted(uint64_t bits,unsigned vector) {
    constexpr std::array<uint64_t,6> lower={0x5555555555555555ULL,0x3333333333333333ULL,
        0x0f0f0f0f0f0f0f0fULL,0x00ff00ff00ff00ffULL,0x0000ffff0000ffffULL,0x00000000ffffffffULL};
    for(unsigned i=0;i<6;++i) if(vector&(1u<<i)) {
        unsigned stride=1u<<i;
        bits=((bits&lower[i])<<stride)|((bits&~lower[i])>>stride);
    }
    return bits;
}
uint64_t difference_set(uint64_t points) {
    uint64_t answer=0,pending=points;
    while(pending) {unsigned p=__builtin_ctzll(pending);pending&=pending-1;answer|=shifted(points,p);}
    return answer;
}
void controls() {
    uint64_t known=0;
    for(int point: {0,2,18,26,10,11,15,63,59,56,60,28,20,16}) known|=uint64_t(1)<<point;
    if(difference_set(known)!=~uint64_t(0)) throw std::runtime_error("fourteen-point positive control");
    uint64_t near=0;
    for(int point: {0,1,2,4,8,16,32,3,5,30,46,54,57}) near|=uint64_t(1)<<point;
    if(__builtin_popcountll(difference_set(near))!=63) throw std::runtime_error("thirteen-point near-cover control");
}
int main(int argc,char** argv) {
    try {
        if(argc!=2) throw std::runtime_error("arguments: positive_deadline_seconds");
        double seconds=std::stod(argv[1]);if(!(seconds>0)) throw std::runtime_error("invalid deadline");
        for(unsigned x=0;x<64;++x) for(unsigned y=0;y<64;++y)
            if(shifted(uint64_t(1)<<x,y)!=(uint64_t(1)<<(x^y))) throw std::runtime_error("XOR translation control");
        controls();
        uint64_t base=1;
        for(unsigned j=0;j<6;++j) base|=uint64_t(1)<<(1u<<j);
        std::vector<int> available;
        for(int p=0;p<64;++p) if(!(base&(uint64_t(1)<<p))) available.push_back(p);
        if(available.size()!=57) throw std::runtime_error("wrong basis complement");
        std::array<uint64_t,65> histogram{};
        uint64_t count=0,best_set=0,selection=63;
        int maximum=0;
        const auto start=std::chrono::steady_clock::now();
        auto elapsed=[&]() { return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count(); };
        bool expired=false;
        while(selection<(uint64_t(1)<<57)) {
            if((count&65535)==0 && elapsed()>=seconds) {expired=true;break;}
            uint64_t points=base,left=selection;
            while(left) {unsigned at=__builtin_ctzll(left);left&=left-1;points|=uint64_t(1)<<available[at];}
            uint64_t differences=difference_set(points);
            int size=__builtin_popcountll(differences);++histogram[size];++count;
            if(size>maximum) {maximum=size;best_set=points;}
            // Gosper's next combination: all 57-bit words with exactly six ones.
            uint64_t low=selection&-selection,raised=selection+low;
            selection=raised|(((selection^raised)>>2)/low);
        }
        std::cout<<"{\"status\":\""<<(expired?"TIMEOUT":"EXHAUSTED")<<"\",\"normalized_sets\":"<<count
                 <<",\"maximum_coverage\":"<<maximum<<",\"histogram\":{";
        bool comma=false;
        for(int size=0;size<=64;++size) if(histogram[size]) {
            std::cout<<(comma?",":"")<<"\""<<size<<"\":"<<histogram[size];comma=true;
        }
        std::cout<<"},\"maximum_witness\":[";comma=false;
        for(int p=0;p<64;++p) if(best_set&(uint64_t(1)<<p)) {std::cout<<(comma?",":"")<<p;comma=true;}
        std::cout<<"],\"elapsed_seconds\":"<<elapsed()<<"}"<<std::endl;
        return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<std::endl;return 2;}
}
