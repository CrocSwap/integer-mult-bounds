// Complete affine-basis-normalized 13-point census in F2^6.
// Tairitsu-Aya, substantial OpenAI Codex assistance. Apache-2.0.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Clock=std::chrono::steady_clock;
uint64_t extend(uint64_t coverage,int point,const int* previous,int count) {
    for(int i=0;i<count;++i) coverage|=uint64_t(1)<<(point^previous[i]);
    return coverage;
}
void control() {
    const std::array<int,14> known{0,2,18,26,10,11,15,63,59,56,60,28,20,16};
    uint64_t coverage=1;
    for(int i=0;i<14;++i) coverage=extend(coverage,known[i],known.data(),i);
    if(coverage!=~uint64_t(0)) throw std::runtime_error("fourteen-point positive control");
    const std::array<int,13> near{0,1,2,4,8,16,32,3,5,30,46,54,57};
    coverage=1;
    for(int i=0;i<13;++i) coverage=extend(coverage,near[i],near.data(),i);
    if(__builtin_popcountll(coverage)!=63) throw std::runtime_error("thirteen-point near-cover control");
}
struct Census {
    std::array<int,13> points{0,1,2,4,8,16,32};
    std::vector<int> options;
    std::array<uint64_t,65> histogram{};
    std::array<int,13> witness{};
    uint64_t count=0,nodes=0;
    int best=0;
    bool expired=false;
    double seconds;
    Clock::time_point start=Clock::now();
    explicit Census(double deadline):seconds(deadline) {
        if(!(seconds>0)) throw std::runtime_error("invalid deadline");
        for(int p=0;p<64;++p)
            if(std::find(points.begin(),points.begin()+7,p)==points.begin()+7) options.push_back(p);
        if(options.size()!=57) throw std::runtime_error("wrong remaining domain");
    }
    double elapsed() const { return std::chrono::duration<double>(Clock::now()-start).count(); }
    void walk(int index,int first,uint64_t coverage) {
        if(expired) return;
        if((++nodes&65535)==0 && elapsed()>=seconds) {expired=true;return;}
        if(index==13) {
            ++count; int size=__builtin_popcountll(coverage);++histogram[size];
            if(size>best) {best=size;witness=points;}
            return;
        }
        int needed=13-index;
        for(int j=first;j+needed<=int(options.size());++j) {
            points[index]=options[j];uint64_t next=extend(coverage,points[index],points.data(),index);
            walk(index+1,j+1,next);
            if(expired) return;
        }
    }
    void run() {
        uint64_t initial=1;
        for(int i=0;i<7;++i) for(int j=0;j<i;++j) initial|=uint64_t(1)<<(points[i]^points[j]);
        walk(7,0,initial);
        std::cout<<"{\"status\":\""<<(expired?"TIMEOUT":"EXHAUSTED")<<"\",\"normalized_sets\":"<<count
                 <<",\"maximum_coverage\":"<<best<<",\"histogram\":{";
        bool comma=false;
        for(int size=0;size<=64;++size) if(histogram[size]) {
            std::cout<<(comma?",":"")<<"\""<<size<<"\":"<<histogram[size];comma=true;
        }
        std::cout<<"},\"maximum_witness\":[";
        for(int i=0;i<13;++i) std::cout<<(i?",":"")<<witness[i];
        std::cout<<"],\"elapsed_seconds\":"<<elapsed()<<"}"<<std::endl;
    }
};
int main(int argc,char** argv) {
    try {
        if(argc!=2) throw std::runtime_error("arguments: positive_deadline_seconds");
        control();Census census(std::stod(argv[1]));census.run();return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<std::endl;return 2;}
}
