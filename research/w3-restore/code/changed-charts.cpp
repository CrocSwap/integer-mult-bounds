// Exact projector charts derived from the actual candidate and baseline words.
// Prepared with substantial OpenAI Codex assistance; Apache-2.0.
#include <algorithm>
#include <cstddef>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#include <json.hpp>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;using J=nlohmann::json;using Q=boost::multiprecision::cpp_rational;using Z=boost::multiprecision::cpp_int;using M=vector<vector<Q>>;
J ld(string p){ifstream f(p);if(!f)throw runtime_error("missing "+p);J j;f>>j;return j;}
Q rat(J j){return j.is_string()?Q(j.get<string>()):Q(j.get<long long>());}M eye(int n){M a(n,vector<Q>(n));for(int i=0;i<n;i++)a[i][i]=1;return a;}M tr(M a){M b(a[0].size(),vector<Q>(a.size()));for(int i=0;i<a.size();i++)for(int j=0;j<a[0].size();j++)b[j][i]=a[i][j];return b;}M mul(M a,M b){M c(a.size(),vector<Q>(b[0].size()));for(int i=0;i<a.size();i++)for(int k=0;k<b.size();k++)if(a[i][k]!=0)for(int j=0;j<b[0].size();j++)c[i][j]+=a[i][k]*b[k][j];return c;}
Z maxnum=1,maxden=1;void admit(Q q){Z n=abs(numerator(q)),d=denominator(q);maxnum=max(maxnum,n);maxden=max(maxden,d);if(n>=(Z(1)<<80)||d>=(Z(1)<<80))throw runtime_error("finite prime guard exceeded");}
M inverse(M a,int &ops,Q &det){int n=a.size();M b=eye(n);det=1;ops=0;for(int k=0;k<n;k++){int t=k;while(t<n&&a[t][k]==0)t++;if(t==n)throw runtime_error("singular");if(t!=k){swap(a[k],a[t]);swap(b[k],b[t]);det=-det;ops++;}Q p=a[k][k];admit(p);det*=p;if(p!=1){ops++;for(int j=0;j<n;j++){a[k][j]/=p;b[k][j]/=p;admit(a[k][j]);admit(b[k][j]);}}for(int i=0;i<n;i++)if(i!=k&&a[i][k]!=0){ops++;Q c=a[i][k];admit(c);for(int j=0;j<n;j++){a[i][j]-=c*a[k][j];b[i][j]-=c*b[k][j];admit(a[i][j]);admit(b[i][j]);}}}if(a!=eye(n))throw runtime_error("inverse failure");return b;}
M nullspace(M a){int n=a[0].size(),row=0;vector<int>piv;for(int col=0;col<n&&row<a.size();col++){int t=row;while(t<a.size()&&a[t][col]==0)t++;if(t==a.size())continue;swap(a[row],a[t]);Q p=a[row][col];admit(p);for(auto &q:a[row]){q/=p;admit(q);}for(int i=0;i<a.size();i++)if(i!=row){Q c=a[i][col];for(int j=0;j<n;j++)a[i][j]-=c*a[row][j];}piv.push_back(col);row++;}if(row!=a.size())throw runtime_error("basis rank failure");M out;for(int free=0;free<n;free++)if(find(piv.begin(),piv.end(),free)==piv.end()){vector<Q>v(n);v[free]=1;for(int i=0;i<row;i++)v[piv[i]]=-a[i][free];out.push_back(v);}return out;}
J mj(M a){J out=J::array();for(auto r:a){J z=J::array();for(Q q:r)z.push_back(q.str());out.push_back(z);}return out;}

M sub(M a,M b){for(int i=0;i<a.size();i++)for(int j=0;j<a[i].size();j++)a[i][j]-=b[i][j];return a;}
M independent_columns(M a){int m=a.size(),n=a[0].size(),row=0;vector<int> piv;M copy=a;for(int c=0;c<n&&row<m;c++){int k=row;while(k<m&&a[k][c]==0)k++;if(k==m)continue;swap(a[k],a[row]);Q p=a[row][c];for(int j=c;j<n;j++)a[row][j]/=p;for(int i=row+1;i<m;i++){Q b=a[i][c];for(int j=c;j<n;j++)a[i][j]-=b*a[row][j];}piv.push_back(c);row++;}M out(m);for(int i=0;i<m;i++)for(int c:piv)out[i].push_back(copy[i][c]);return out;}
M kernel_general(M a){int m=a.size(),n=a[0].size(),row=0;vector<int>piv;for(int col=0;col<n&&row<m;col++){int t=row;while(t<m&&a[t][col]==0)t++;if(t==m)continue;swap(a[row],a[t]);Q p=a[row][col];for(auto&q:a[row])q/=p;for(int i=0;i<m;i++)if(i!=row){Q c=a[i][col];for(int j=0;j<n;j++)a[i][j]-=c*a[row][j];}piv.push_back(col);row++;}M out;for(int free=0;free<n;free++)if(find(piv.begin(),piv.end(),free)==piv.end()){vector<Q>v(n);v[free]=1;for(int i=0;i<row;i++)v[piv[i]]=-a[i][free];out.push_back(v);}return out;}
struct Ev{int op,a,b,c,r,z;};
int main(int ac,char**av){if(ac!=4)throw runtime_error("usage: charts EXPORT CANDIDATE OUT");string base=av[1],candidate=av[2],output=av[3];J fs=ld(base+"/frames.json")["frames"];J nf=ld(candidate+"/COHORT249-FRAMES.json"),ini=ld(candidate+"/COHORT249-INITIAL.json"),fin=ld(candidate+"/COHORT249-FINAL.json");for(auto it=nf.begin();it!=nf.end();++it)fs[it.key()]=it.value();M G=eye(24);for(auto&r:G)for(auto&q:r)q-=Q(1)/9;map<int,M>projectors;auto proj=[&](int f)->M{if(projectors.count(f))return projectors[f];int d=fs.at(to_string(f))["dim"];if(d==24)return projectors[f]=eye(24);if(!d)return projectors[f]=M(24,vector<Q>(24));M B;for(auto row:fs.at(to_string(f))["B"]){vector<Q>r;for(auto x:row)r.push_back(rat(x));B.push_back(r);}int ops;Q det;M BG=mul(B,G), gram=mul(BG,tr(B)), inv=inverse(gram,ops,det);return projectors[f]=mul(mul(tr(B),inv),BG);};set<tuple<int,int,int>>pairs,oldpairs;int endpoints=0;
auto events=[&](string path){ifstream f(path,ios::binary);if(!f)throw runtime_error("missing word");f.seekg(0,ios::end);size_t size=f.tellg();f.seekg(0);if(size%sizeof(Ev))throw runtime_error("word shape");vector<Ev>v(size/sizeof(Ev));f.read((char*)v.data(),size);return v;};
for(auto e:events(base+"/COHORT249-RECORDS.bin"))if(e.op==0&&e.r)oldpairs.insert({e.b,e.c,e.r});
for(auto e:events(candidate+"/COHORT249-RECORDS.bin"))if(e.op==0&&e.r&&!oldpairs.count({e.b,e.c,e.r}))pairs.insert({e.b,e.c,e.r});
J oldstate=ld(base+"/249-states.json");int v=oldstate["v"],n=oldstate["n"];
for(int a=2*v;a<n;a++){string role=to_string(a);int before=ini[role],after=fin[role];if(before!=oldstate["initial"][role].get<int>()||after!=oldstate["final"][role].get<int>()){int rank=fs.at(to_string(after))["dim"].get<int>()-fs.at(to_string(before))["dim"].get<int>();pairs.insert({before,after,rank});endpoints++;}}

int maxops=0,checked=0;J charts=J::array();for(auto[before,after,r]:pairs){M E=sub(proj(after),proj(before));if(mul(E,E)!=E)throw runtime_error("not projector");M C=independent_columns(E);if(C[0].size()!=r)throw runtime_error("rank mismatch");M K=kernel_general(E);if(K.size()!=24-r)throw runtime_error("nullity mismatch");for(int i=0;i<24;i++)for(auto&v:K)C[i].push_back(v[i]);int ops;Q det;M inv=inverse(C,ops,det),want=eye(24);for(int i=r;i<24;i++)want[i][i]=0;if(mul(mul(inv,E),C)!=want||mul(C,inv)!=eye(24))throw runtime_error("chart identity");maxops=max(maxops,ops);charts.push_back({{"before",before},{"after",after},{"rank",r},{"basis",mj(C)},{"inverse",mj(inv)},{"factors",ops},{"determinant",det.str()}});checked++;if(checked%50==0)cout<<"checked "<<checked<<"/"<<pairs.size()<<" maxfactors "<<maxops<<endl;}
if(maxops>548)throw runtime_error("factor budget exceeded");J receipt={{"status","PASS_EXACT_CHANGED_ENDPOINT_AND_MOVE_CHARTS"},{"retired_endpoints",endpoints},{"unique_projectors_checked",checked},{"max_factors",maxops},{"max_numerator",maxnum.str()},{"max_denominator",maxden.str()},{"all_entries_below_two_to_80",true}};ofstream(output+"/COMBINED-CHART-AUDIT.json")<<receipt.dump(2)<<endl;ofstream(output+"/COMBINED-CHARTS.json")<<charts.dump()<<endl;cout<<receipt.dump(2)<<endl;}
