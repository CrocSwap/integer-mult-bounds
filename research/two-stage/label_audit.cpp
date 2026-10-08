// Exact rational containment checks for the PR24 positive-frame producer.
// Zhihao Chen (jacklightChen), with OpenAI Codex assistance. Apache-2.0.
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
using U=uint32_t;using V=uint64_t;
#include "binary_io.hpp"
using Row=std::array<int,64>;
using Mat=std::vector<Row>;
int main(int argc,char**argv){
 assert(argc==3);std::ifstream f(argv[1],std::ios::binary);U hd[4];read_array(f,hd);
 U h=hd[0],v=hd[1],n=hd[2],q=hd[3];assert(h<64);
 std::vector<std::array<U,2>>args(n);std::vector<V>core(n),cover(n);
 std::vector<U>roots(q),kind(q);std::vector<uint8_t>active(n);
 readv(f,args);readv(f,core);readv(f,cover);readv(f,roots);readv(f,kind);readv(f,active);
 std::ifstream g(argv[2],std::ios::binary);U gh[2];read_array(g,gh);assert(gh[0]==h&&gh[1]==n);
 std::vector<U>ranks(n);std::vector<V>forced(n);std::vector<int8_t>sy(V(n)*h);
 readv(g,ranks);readv(g,forced);readv(g,sy);
 auto basis=[&](U x,bool envelope){
  Mat B(h);if(!args[x][0]){for(U i=0;i<h;i++)B[i][0]=(core[x]>>i)&1;return B;}
  if(envelope){int d=3-popcount64(core[x]);assert(d>0);U k=0;
   for(U j=0;j<h;j++)if((cover[x]>>j&1)&&!(core[x]>>j&1)){
    B[j][k]=d;for(U i=0;i<h;i++)if(core[x]>>i&1)B[i][k]=1;k++;
   }return B;
  }
  int d=3-popcount64(forced[x]);assert(d==1||d==2);Row sums{};
  for(U i=0;i<h;i++){int t=sy[V(x)*h+i];if(t>1)sums[t-2]++;if(t<-1)sums[-t-2]--;}
  for(U i=0;i<h;i++){int t=sy[V(x)*h+i];if(t==1)B[i]=sums;
   else if(t>1)B[i][t-2]=d;else if(t<-1)B[i][-t-2]=-d;
  }return B;
 };
 auto contained=[&](const Mat&B,U y){
  U first=0;while(!(forced[y]>>first&1))first++;
  Row sum{};for(U i=0;i<h;i++)for(U j=0;j<h;j++)sum[j]+=B[i][j];
  for(U j=0;j<h;j++)assert(sum[j]==3*B[first][j]);
  std::array<int,66>where;where.fill(-1);Row zero{};
  for(U i=0;i<h;i++){int t=sy[V(y)*h+i];
   if(t==0)assert(B[i]==zero);
   else if(t==1)assert(B[i]==B[first]);
   else {int k=std::abs(t),sign=t>0?1:-1;
    if(where[k]<0)where[k]=i;
    else {int w=where[k],s=sy[V(y)*h+w]>0?1:-1;
     for(U j=0;j<h;j++)assert(sign*B[i][j]==s*B[w][j]);}
   }
  }
 };
 V arcs=0,envelopes=0;
 for(U x=1;x<n;x++)if(active[x]){
  if(args[x][0]){
   contained(basis(x,true),x);envelopes++;
   for(U y:args[x]){contained(basis(y,false),x);arcs++;}
  }
 }
 // Target side labels imply the exact target-line orthogonality constraint.
 for(U j=0;j<q;j++){
  U x=roots[j];Mat B=basis(x,false);
  if(kind[j])assert(ranks[x]==h-1);
  else {V bad=((V(1)<<h)-1)^cover[x];assert(popcount64(bad)==2);
   for(U k=0;k<h;k++){int z=0;for(U i=0;i<h;i++)if(bad>>i&1)z+=B[i][k];assert(z==0);}
  }
 }
 std::cout<<"{\"h\":"<<h<<",\"exact_envelopes\":"<<envelopes
 <<",\"exact_dependency_inclusions\":"<<arcs<<",\"output_frames\":"<<q
 <<",\"complement_orientation_by_exact_duality\":true}"<<std::endl;
}
