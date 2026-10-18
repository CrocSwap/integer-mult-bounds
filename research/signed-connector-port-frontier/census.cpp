// Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
// Literal chronological state enumeration. No arithmetic or hash approximation.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>
using V=std::array<int,5>;
using Roots=std::array<V,2>;
struct Event {char kind; int op,sign,root;};
struct Pair {int first=-1,last=-1,sign=0;};
const int target[3][3]={{1,1,1},{1,1,-1},{1,-1,0}};
int main() {
 std::array<uint64_t,64> counts{};
 std::array<uint64_t,8> restored_by_source{};
 std::array<std::vector<Event>,64> witness;
 uint64_t total=0, restored=0, feasible=0;
 for(int ports=0;ports<8;++ports) {
  std::array<int,6> source={0,1,2,3,4,5};
  do {
   for(int placement=0;placement<1024;++placement) {
    if(__builtin_popcount((unsigned)placement)!=4) continue;
    for(int plus=0;plus<16;++plus) {
     if(__builtin_popcount((unsigned)plus)!=2) continue;
     ++total;
     std::array<Roots,11> state{};
     state[0][0][0]=1; state[0][1][1]=1;
     std::array<Event,10> events{};
     int si=0,ti=0;
     for(int t=0;t<10;++t) {
      state[t+1]=state[t];
      if((placement>>t)&1) {
       int sign=((plus>>ti++)&1)?1:-1;
       for(int k=0;k<5;++k) state[t+1][0][k]+=sign*state[t][1][k];
       events[t]={'R',1,sign,0};
      } else {
       int ev=source[si++], j=ev/2, sign=(ev%2)?-1:1, root=(ports>>j)&1;
       state[t+1][root][2+j]+=sign;
       events[t]={'B',j,sign,root};
      }
     }
     if(state[10]!=state[0]) continue;
     ++restored; ++restored_by_source[ports];
     Pair reads[3][2];
     for(int i=0;i<3;++i) for(int root=0;root<2;++root) {
      for(int l=0;l<10 && reads[i][root].first<0;++l) for(int r=l+1;r<11;++r) {
       const V &a=state[l][root], &b=state[r][root];
       if(a[0]!=b[0] || a[1]!=b[1]) continue;
       for(int sign: {-1,1}) {
        bool ok=true;
        for(int j=0;j<3;++j) if(sign*(b[2+j]-a[2+j])!=target[i][j]) ok=false;
        if(ok) {reads[i][root]={l,r,sign};break;}
       }
       if(reads[i][root].first>=0) break;
      }
     }
     bool any=false;
     for(int ap=0;ap<8;++ap) {
      bool ok=true;
      for(int i=0;i<3;++i) if(reads[i][(ap>>i)&1].first<0) ok=false;
      if(!ok) continue;
      any=true; int mask=ports+(ap<<3); ++counts[mask];
      if(!witness[mask].empty()) continue;
      for(int gap=0;gap<11;++gap) {
       for(int i=0;i<3;++i) {
        int root=(ap>>i)&1; const Pair &p=reads[i][root];
        if(gap==p.first) witness[mask].push_back({'A',i,-p.sign,root});
        if(gap==p.last) witness[mask].push_back({'A',i,p.sign,root});
       }
       if(gap<10) witness[mask].push_back(events[gap]);
      }
     }
     if(any) ++feasible;
    }
   }
  } while(std::next_permutation(source.begin(),source.end()));
 }
 std::cout<<"{\n\"source_traces\":"<<total<<",\n\"restored_traces\":"<<restored<<",\n\"feasible_traces\":"<<feasible<<",\n\"restored_by_source\":[";
 for(int i=0;i<8;++i) std::cout<<(i?",":"")<<restored_by_source[i];
 std::cout<<"],\n\"counts\":[";
 for(int i=0;i<64;++i) std::cout<<(i?",":"")<<counts[i];
 std::cout<<"],\n\"witnesses\":[\n";
 bool comma=false;
 for(int mask=0;mask<64;++mask) if(counts[mask]) {
  if(comma) std::cout<<",\n"; comma=true;
  std::cout<<"{\"mask\":"<<mask<<",\"word\":[";
  bool comma2=false;
  for(const auto &e:witness[mask]) {if(comma2)std::cout<<",";comma2=true;
   std::cout<<"[\""<<e.kind<<"\","<<e.op<<","<<e.sign<<","<<e.root<<"]";
  }
  std::cout<<"]}";
 }
 std::cout<<"\n]}\n";
}
