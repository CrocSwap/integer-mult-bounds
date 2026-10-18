// Complete-domain RGS/direct-difference cross-check. ywz65/Codex, Apache-2.0.
// Credits PR2134 (1337isnot1337) for the predecessor RGS approach and witness.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>
using A=std::array<int,6>;
std::array<int,13> word{},best{};
A counts{};
std::map<A,std::array<uint64_t,64>> hist;
uint64_t complete=0,eligible=0; int maximum=-1;
void visit(int depth,int used){
 if(depth==13){
  if(used!=6)return; ++complete;
  int odd=0;for(int c:counts)odd+=c%2;
  if(odd!=3)return; ++eligible;
  std::array<int,14> p{};
  for(int i=0;i<13;++i)p[i+1]=p[i]^(1<<word[i]);
  uint64_t cover=0;
  for(int i=0;i<14;++i)for(int j=i+1;j<14;++j)cover|=uint64_t(1)<<(p[i]^p[j]);
  cover&=~uint64_t(1);int n=0;for(uint64_t b=cover;b;b&=b-1)++n;
  A profile=counts;std::sort(profile.begin(),profile.end());++hist[profile][n];
  if(n>maximum){maximum=n;best=word;}
  return;
 }
 for(int label=0;label<=std::min(used,5);++label){word[depth]=label;++counts[label];visit(depth+1,std::max(used,label+1));--counts[label];}
}
int main(){visit(0,0);std::cout<<"{\"complete\":"<<complete<<",\"eligible\":"<<eligible<<",\"maximum\":"<<maximum<<",\"word\":[";
for(int i=0;i<13;++i)std::cout<<(i?",":"")<<best[i];std::cout<<"],\"profiles\":[";bool first=true;
for(auto& [profile,h]:hist){if(!first)std::cout<<",";first=false;std::cout<<"{\"counts\":[";for(int i=0;i<6;++i)std::cout<<(i?",":"")<<profile[i];std::cout<<"],\"histogram\":{";bool f=true;for(int k=0;k<64;++k)if(h[k]){if(!f)std::cout<<",";f=false;std::cout<<"\""<<k<<"\":"<<h[k];}std::cout<<"}}";}
std::cout<<"]}\n";}
