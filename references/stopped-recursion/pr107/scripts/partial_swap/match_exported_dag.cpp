// Copyright 2026 icekylinx. Licensed under Apache-2.0.
// Adapted with AI assistance from the archived partial-swap research producer.
// Underlying circuit modules: jacklightChen/integer-mult-bounds, PR7
// commit 6725c6a17b17871a35353fd29157f4ed851bc114; original credits retained.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
using U=uint32_t;using V=uint64_t;
#include "binary_io.hpp"
int main(int argc,char**argv){assert(argc==2||argc==3);std::ifstream f(argv[1],std::ios::binary);U hdr[4];read_array(f,hdr);U h=hdr[0],v=hdr[1],n=hdr[2],q=hdr[3];
std::vector<std::array<U,2>>args(n);std::vector<V>core(n),cover(n);std::vector<U>roots(q),kind(q);std::vector<uint8_t>active(n);readv(f,args);readv(f,core);readv(f,cover);readv(f,roots);readv(f,kind);readv(f,active);
std::vector<U>ranks(n),degree(n),begin(n+1);V c=0,inputs=0,loss=0;
for(U x=1;x<n;x++)if(active[x]){if(args[x][0]){c++;assert(args[x][0]<x&&args[x][1]<x);ranks[x]=popcount64(cover[x])-popcount64(core[x]);for(U y:args[x])degree[y]++;}else{ranks[x]=1;inputs++;}}
assert(inputs==v);for(U x:roots)degree[x]++;for(U x=1;x<n;x++)begin[x+1]=begin[x]+degree[x];
std::vector<U>uses(begin.back()),cursor(begin.begin(),begin.end()-1);for(U x=1;x<n;x++)if(active[x]&&args[x][0]){uses[cursor[args[x][0]]++]=2*x;uses[cursor[args[x][1]]++]=2*x+1;}for(U j=0;j<q;j++)uses[cursor[roots[j]]++]=(1U<<31)|j;
auto nd=[&](U e)->U{return e>>31?roots[e&0x7fffffff]:e/2;};
auto before=[&](U a,U b){U x=nd(a),y=nd(b);if(ranks[x]!=ranks[y])return ranks[x]<ranks[y];V ox=a>>31?V(n)+(a&0x7fffffff):x,oy=b>>31?V(n)+(b&0x7fffffff):y;return ox<oy;};
auto incl=[&](U a,U b){U x=nd(a),y=nd(b);return !(core[y]&~core[x])&&!(cover[x]&~cover[y]);};
auto adjacency=[&](U donor,auto&& action){for(U value:args[donor])for(U j=begin[value];j<begin[value+1];j++)if(before(donor*2,uses[j])&&incl(donor*2,uses[j]))if(action(j))return true;return false;};
std::vector<U>donors;for(U x=1;x<n;x++)if(active[x]&&args[x][0]&&adjacency(x,[](U){return true;}))donors.push_back(x);
std::vector<U>leftmatch(n),rightmatch(uses.size()),distance(n,UINT32_MAX),queue;V matches=0;U phase=0,inf=UINT32_MAX,shortest=inf;
while(true){queue.clear();shortest=inf;for(U x:donors){if(!leftmatch[x]){distance[x]=0;queue.push_back(x);}else distance[x]=inf;}for(U at=0;at<queue.size();at++){U x=queue[at];if(distance[x]>=shortest)continue;adjacency(x,[&](U j){U y=rightmatch[j];if(!y)shortest=distance[x]+1;else if(distance[y]==inf){distance[y]=distance[x]+1;queue.push_back(y);}return false;});}if(shortest==inf)break;
auto aug=[&](auto&&self,U x)->bool{bool ok=adjacency(x,[&](U j){U y=rightmatch[j];if((!y&&distance[x]+1==shortest)||(y&&distance[y]==distance[x]+1&&self(self,y))){leftmatch[x]=j+1;rightmatch[j]=x;return true;}return false;});if(!ok)distance[x]=inf;return ok;};V gained=0;for(U x:donors)if(!leftmatch[x]&&aug(aug,x)){matches++;gained++;}std::cerr<<"h="<<h<<" phase "<<++phase<<" length "<<shortest<<" gained "<<gained<<" total "<<matches<<"\n";assert(gained);}
std::vector<int64_t>hist(h+1);for(U x=1;x<n;x++)if(active[x]){assert(degree[x]);U r=ranks[x];if(args[x][0]){hist[r]+=degree[x]-1;hist[h-r]++;for(U y:args[x]){assert(r>=ranks[y]);hist[r-ranks[y]]++;}}else hist[1]+=degree[x];}
for(U j=0;j<q;j++){U r=ranks[roots[j]];if(kind[j]){hist[r]++;hist[h]++;loss+=r;}else{assert(r<=h-1);hist[h-1-r]++;hist[1]++;}}
V changed=0;for(U donor:donors)if(leftmatch[donor]){U e=uses[leftmatch[donor]-1],target=nd(e),value=e>>31?target:args[target][e&1];assert(value==args[donor][0]||value==args[donor][1]);if(value==args[donor][0])changed++;U ru=ranks[donor],rv=ranks[value],rt=ranks[target];assert(rt>=ru&&ru>=rv);hist[h-ru]--;hist[rv]--;hist[rt-rv]--;hist[rt-ru]++;}
V R=c+q-matches,sum=0;for(U r=0;r<=h;r++){assert(hist[r]>=0);sum+=r*hist[r];}assert(sum==h*R+2*loss);
if(argc==3){std::ofstream out(argv[2],std::ios::binary);U header[2]={n,U(matches)};write_array(out,header);for(U donor:donors)if(leftmatch[donor]){U edge[2]={donor,nd(uses[leftmatch[donor]-1])};write_array(out,edge);}assert(out);}
std::cout<<"{\"h\":"<<h<<",\"v\":"<<v<<",\"c\":"<<c<<",\"q\":"<<q<<",\"baseline_R\":"<<c+q<<",\"matched\":"<<matches<<",\"R\":"<<R<<",\"orientation_changes\":"<<changed<<",\"rank_sum\":"<<sum<<",\"loss\":"<<loss<<",\"histogram\":[";for(U r=0;r<=h;r++){if(r)std::cout<<",";std::cout<<hist[r];}std::cout<<"]}"<<std::endl;
}
