#include <cstdio>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <list>
using namespace std;

vector<string> split(string s, string separator){
  vector<string> result;
  string toAdd;
  size_t foundPos = s.find_first_of(separator);
  if(foundPos==string::npos){
    result.push_back(s);
    return result;
  }
  while(foundPos!=string::npos){
    toAdd = s.substr(0, foundPos);
    result.push_back(toAdd);
    s = s.substr(foundPos+1, s.size());
    foundPos = s.find_first_of(separator);
    if(foundPos==string::npos) result.push_back(s);
  }
  return result;
}

class Node {
public:
  string id, label;
  bool visited=0;
  vector<string> connections;
  Node(string id, string label){
    this->id=id; this->label=label;
  }
  void addEdge(string id){
    this->connections.push_back(id);
  }
};

bool hasCyclesDepthFS(map<string, Node*> pages, string origin){
    map<string, Node*>::iterator it = pages.begin();
    while(it != pages.end()){
        it->second->visited=0;
        it++;
    }
    list<Node*> l;
    l.push_back( pages[origin] );
    while(!l.empty()){
        Node* node = l.back();
        printf(" visiting %s, id:%s\n", node->label.c_str(), node->id.c_str());
        node->visited = 1;
        l.pop_back();
        for(int i=0; i<node->connections.size(); i++){
          if( pages.find(node->connections[i])==pages.end() ){
            // printf(" %s doesn't exist!\n", node->connections[i].c_str());
            continue;
          }
          if( pages[node->connections[i]]->visited==1 ){
              return true;
          } else {
              l.push_back( pages[node->connections[i]] );
          }
        }
    }
    return false;
}

bool hasCyclesBreadthFS(map<string, Node*> pages, string origin){
    map<string, Node*>::iterator it = pages.begin();
    while(it != pages.end()){
        it->second->visited=0;
        it++;
    }
    list<Node*> l;
    l.push_back( pages[origin] );
    while(!l.empty()){
        Node* node = l.front();
        printf(" visiting %s, id:%s\n", node->label.c_str(), node->id.c_str());
        node->visited = 1;
        l.pop_front();
        for(int i=0; i<node->connections.size(); i++){
          if( pages.find(node->connections[i])==pages.end() ){
            // printf(" %s doesn't exist!\n", node->connections[i].c_str());
            continue;
          }
          if( pages[node->connections[i]]->visited==1 ){
              return true;
          } else {
              l.push_back( pages[node->connections[i]] );
          }
        }
    }
    return false;
}

int main(){
  ifstream nodos("nodos_se.csv");
  string line, id, label;
  map<string, Node*> pages;
  nodos>>line;
  while(nodos>>line){
    vector<string> atributes = split(line, ",");
    id=atributes[0]; label=atributes[1];
    if(id!="" && label!=""){
      // printf("id:%s\tlabel:%s\n", id.c_str(), label.c_str());
      if(pages.find(id)==pages.end()){
        pages[id] = new Node(id, label);
      }
    }
  }
  string source, target;
  ifstream edges("edges.csv");
  int notFound = 0;
  edges >> line;
  while(edges>>line){
    vector<string> atributes = split(line, ",");
    source=atributes[0]; target=atributes[1];
    // printf("source: %s\ttarget:%s\n", source.c_str(), target.c_str());
    if(pages.find(source)!=pages.end()){
      // printf("%s exists\n", source.c_str());
      pages[source]->addEdge(target);
    } else {
      notFound++;
    }
  }
  printf("edges not found:%d\n", notFound);

  printf("Breadth First: %s\n", hasCyclesBreadthFS(pages, /*it->first*/"34767149008")?"true":"false");
  printf("Depth First: %s\n", hasCyclesDepthFS(pages, /*it->first*/"34767149008")?"true":"false");
  return 0;
}
