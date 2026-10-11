#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
#include "json.hpp"
using J=nlohmann::json;using G=std::array<long long,2>;
G mul_i(G a,int p){p=(p%4+4)%4;if(p==1)return {-a[1],a[0]};if(p==2)return {-a[0],-a[1]};if(p==3)return {a[1],-a[0]};return a;}
int parity(int x){return __builtin_parity((unsigned)x);}
int mv(const J&rows,int x){int z=0;for(int i=0;i<(int)rows.size();i++)z|=parity((int)rows[i]&x)<<i;return z;}
std::pair<std::vector<G>,int> run(const J&circ,int col,int h){int N=1<<h,den=0;std::vector<G> v(N,G{0,0});v[col]={1,0};for(auto&e:circ){std::string k=e[0];if(k=="P"){std::vector<G>w(N);for(int x=0;x<N;x++)w[mv(e[1],x)]=v[x];v.swap(w);}else if(k=="X"){std::vector<G>w(N);int q=e[1];for(int x=0;x<N;x++)w[x]=v[x^q];v.swap(w);}else if(k=="phase"){for(auto&a:v)a=mul_i(a,e[1]);}else if(k=="D"){for(int x=0;x<N;x++){int p=0;for(int i=0;i<h;i++)if(x>>i&1){p+=(int)e[2][i];p+=2*parity(((int)e[1][i]>>(i+1))&(x>>(i+1)));}v[x]=mul_i(v[x],p);}}else if(k=="C"){int q=e[1],s=e[2];std::vector<G>w(N);for(int x=0;x<N;x++){auto[a,b]=v[x];auto[c,d]=v[x^q];w[x]={a-s*b+c+s*d,b+s*a+d-s*c};}v.swap(w);den++;}else throw std::runtime_error(k);while(den&&std::all_of(v.begin(),v.end(),[](G a){return !(a[0]&1)&&!(a[1]&1);})){for(auto&a:v){a[0]/=2;a[1]/=2;}den--;}}return {v,den};}
int main(int argc,char**argv){J inp;std::ifstream(argv[1])>>inp;int total=0;for(auto&p:inp){int h=p["h"],N=1<<h;for(int col=0;col<N;col++){auto[a,ad]=run(p["actual"],col,h);auto[b,bd]=run(p["expected"],col,h);for(int x=0;x<N;x++){if(ad<bd){a[x][0]*=1LL<<(bd-ad);a[x][1]*=1LL<<(bd-ad);}if(bd<ad){b[x][0]*=1LL<<(ad-bd);b[x][1]*=1LL<<(ad-bd);}if(a[x]!=b[x])throw std::runtime_error("column mismatch");}}total+=N;std::cout<<"PASS frame "<<p["frame"]<<" columns "<<N<<'\n';}std::cout<<"PASS total columns "<<total<<'\n';}
