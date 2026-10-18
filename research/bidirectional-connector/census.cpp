// Exact two-dirty-root census. conorholds with Codex assistance. Apache-2.0.
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <string>
#include <vector>
using Word = std::vector<int>;
struct Result { uint64_t words=0,placements=0,assignments=0,universal=0,three_readout=0; std::array<uint64_t,33> hist{}; };
int parity(int x) {return __builtin_popcount(unsigned(x))&1;}
int mv(const std::array<int,2>& g,int v){return parity(g[0]&v)|(parity(g[1]&v)<<1);}
int bitfirst(uint32_t x){return __builtin_ctz(x);}
uint32_t differences(uint32_t points){uint32_t out=0;for(uint32_t a=points;a;a&=a-1)for(uint32_t b=points;b;b&=b-1)out|=uint32_t(1)<<(bitfirst(a)^bitfirst(b));return out;}
bool three(const std::array<uint32_t,4>& present,int missing) {
 for(uint32_t a=present[1];a;a&=a-1)for(uint32_t b=present[2];b;b&=b-1)
  if(present[3]&(uint32_t(1)<<(missing^bitfirst(a)^bitfirst(b))))return true;
 return false;
}
void controls() {
 const int ops[16][3]={{0,0,1},{1,0,0},{0,1,1},{1,1,0},{0,2,0},{1,0,0},{0,0,0},{0,3,0},{1,1,0},{0,1,0},{1,0,0},{0,4,1},{1,1,0},{0,3,1},{0,2,1},{0,4,1}};
 int roots[2]={32,64};std::array<uint32_t,4> present{};present[1]=present[2]=1;
 for(const auto& op:ops){if(op[0])roots[op[1]]^=roots[1-op[1]];else roots[op[2]]^=1<<op[1];for(int p=0;p<2;++p)present[roots[p]>>5]|=uint32_t(1)<<(roots[p]&31);}
 if(roots[0]!=32||roots[1]!=64||__builtin_popcount(differences(present[1])|differences(present[2])|differences(present[3]))!=32)std::abort();
 present={0,1,1,uint32_t(1)<<7};if(!three(present,7))std::abort();present[3]=0;if(three(present,7))std::abort();
}
Result census(int t,bool triple) {
 Result r; int length=10+int(triple); Word source,counts(5),directions;
 std::vector<Word> ds;
 for(int bits=0;bits<(1<<t);++bits){std::array<int,2> g{1,2};Word d;for(int i=0;i<t;++i){int p=(bits>>i)&1;d.push_back(p);g[p]^=g[1-p];}if(g==std::array<int,2>{1,2})ds.push_back(d);}
 std::function<void(int)> source_rec;
 source_rec=[&](int opened){
  if(int(source.size())==length){
   if(triple ? counts[0]!=3 : opened!=5)return;
   ++r.words;
   for(const auto& dirs:ds){
    Word skeleton; std::array<int,2> g{1,2}; std::vector<std::array<int,2>> frames;
    std::function<void(int,int)> merge;
    merge=[&](int bi,int ci){
     if(bi==length && ci==t){
      ++r.placements;
      std::array<std::vector<uint16_t>,5> options;
      for(int j=0;j<5;++j){
       Word at;for(int i=0;i<length;++i)if(source[i]==j)at.push_back(i);
       for(int bits=0;bits<(1<<at.size());++bits){int sum=0;uint16_t ports=0;
        for(size_t i=0;i<at.size();++i){int p=(bits>>i)&1;int normalized=0;for(int v=1;v<=3;++v)if(mv(frames[at[i]],v)==(1<<p))normalized=v;
         if(!normalized)std::abort();sum^=normalized;ports|=uint16_t(p)<<at[i];}
        if(sum==0)options[j].push_back(ports);
       }
       if(options[j].empty())return;
      }
      std::function<void(int,uint16_t)> assign;
      assign=[&](int j,uint16_t port_bits){
       if(j<5){for(auto option:options[j])assign(j+1,port_bits|option);return;}
       ++r.assignments;std::array<uint32_t,4> present{};int roots[2]={32,64};present[1]=present[2]=1;int index=0;
       for(int op:skeleton){if(op<0){int p=-op-1;roots[p]^=roots[1-p];}else{int p=(port_bits>>index)&1;roots[p]^=1<<op;++index;}
        for(int p=0;p<2;++p)present[roots[p]>>5]|=uint32_t(1)<<(roots[p]&31);}
       if(roots[0]!=32||roots[1]!=64)std::abort();
       uint32_t cover=differences(present[1])|differences(present[2])|differences(present[3]);int size=__builtin_popcount(cover);++r.hist[size];if(size==32)++r.universal;
       if(!triple && t==2 && size==31){int missing=bitfirst(~cover);
        if(three(present,missing))++r.three_readout;
       }
      };
      assign(0,0);return;
     }
     if(bi<length){skeleton.push_back(source[bi]);frames.push_back(g);merge(bi+1,ci);frames.pop_back();skeleton.pop_back();}
     if(ci<t){int p=dirs[ci];g[p]^=g[1-p];skeleton.push_back(-p-1);merge(bi,ci+1);skeleton.pop_back();g[p]^=g[1-p];}
    };
    merge(0,0);
   }
   return;
  }
  if(triple){
   if(counts[0]<3){counts[0]++;source.push_back(0);source_rec(opened);source.pop_back();counts[0]--;}
   for(int j=1;j<=std::min(4,opened+1);++j)if(counts[j]<2){counts[j]++;source.push_back(j);source_rec(std::max(opened,j));source.pop_back();counts[j]--;}
  }else for(int j=0;j<std::min(5,opened+1);++j)if(counts[j]<2){counts[j]++;source.push_back(j);source_rec(std::max(opened,j+1));source.pop_back();counts[j]--;}
 };
 source_rec(0);return r;
}
int main(int argc,char** argv){if(argc!=3){std::cerr<<"usage: census transfers triple(0/1)\n";return 2;}int t=std::stoi(argv[1]);bool triple=std::stoi(argv[2])!=0;if(t<0||t>4){std::cerr<<"domain 0<=t<=4\n";return 2;}controls();auto begin=std::chrono::steady_clock::now();auto r=census(t,triple);
 std::cout<<"{\"transfers\":"<<t<<",\"triple\":"<<(triple?"true":"false")<<",\"words\":"<<r.words<<",\"placements\":"<<r.placements<<",\"assignments\":"<<r.assignments<<",\"universal\":"<<r.universal<<",\"three_readout\":"<<r.three_readout<<",\"histogram\":[";for(int i=0;i<33;++i){if(i)std::cout<<',';std::cout<<r.hist[i];}std::cout<<"],\"controls\":3,\"elapsed_seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<"}\n";
}
