#include <bits/stdc++.h>
#include <json.hpp>
using namespace std;using J=nlohmann::json;using Row=bitset<1024>;using Gate=pair<int,int>;
int main(int ac,char**av){J z;ifstream(av[1])>>z;int v=z["v"],n=2*v+z["R"].get<int>(),lo=2*v;vector<Row> initial(n);for(int i=0;i<n;i++)initial[i][i]=1;int old=0;for(auto e:z["C"]){int d=e[1];for(int s:e[2]){initial[d]^=initial[s];old++;}}
int best=old;J runs=J::array();mt19937 rng(20261011);for(int run=0;run<30;run++){auto rows=initial;vector<Gate> ops;vector<int>cols;for(int i=lo;i<n;i++)cols.push_back(i);if(run==1)reverse(cols.begin(),cols.end());else if(run>1)shuffle(cols.begin(),cols.end(),rng);auto add=[&](int d,int s){rows[d]^=rows[s];ops.push_back({d,s});};vector<bool>fixed(n);bool okay=true;
for(int step=0;step<n-lo;step++){int col=cols[step];if(run>=10){long long bc=LLONG_MAX;int bi=step;for(int k=step;k<n-lo;k++){int c=cols[k],pc=-1,pw=10000,fan=0;for(int i=lo;i<n;i++)if(!fixed[i]&&rows[i][c]){int w=rows[i].count();if(w<pw){pw=w;pc=i;}fan++;}long long cost=(long long)max(0,fan-1)*max(0,pw-1)+(pc==c?0:3);if(cost<bc){bc=cost;bi=k;}}swap(cols[step],cols[bi]);col=cols[step];}
int pivot=-1,weight=10000;for(int i=lo;i<n;i++)if(!fixed[i]&&rows[i][col]){int w=rows[i].count()+(i==col?0:3);if(w<weight){weight=w;pivot=i;}}if(pivot<0){okay=false;break;}if(pivot!=col){if(fixed[col])throw runtime_error("fixed");add(col,pivot);add(pivot,col);add(col,pivot);}for(int i=lo;i<n;i++)if(i!=col&&rows[i][col])add(i,col);fixed[col]=true;}
if(!okay)throw runtime_error("singular");for(int i=lo;i<n;i++)for(int j=0;j<lo;j++)if(rows[i][j])add(i,j);for(int i=0;i<n;i++)if(rows[i].count()!=1||!rows[i][i])throw runtime_error("notI");runs.push_back({{"run",run},{"cost",ops.size()}});cout<<run<<" "<<ops.size()<<endl;
if((int)ops.size()<best){best=ops.size();reverse(ops.begin(),ops.end());J C=J::array();for(auto[d,s]:ops)C.push_back({1,d,J::array({s})});auto w=z;w["C"]=C;ofstream(av[2])<<w.dump();}
}
ofstream(av[3])<<J({{"original",old},{"best",best},{"runs",runs}}).dump(2);
}
