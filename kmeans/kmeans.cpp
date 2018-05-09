#include <cstdio>
#include <vector>
#include <cmath>
using namespace std;

class Point {
public:
  float x, y;
  int cluster, previous_cluster;
  Point(float x, float y){
    this->x = x;
    this->y = y;
    this->previous_cluster = -1;
    this->cluster = -2;
  }
};

class Cluster {
public:
  float x, y, totalX, totalY, points;
  Cluster(float x, float y){
    this->x = x;
    this->y = y;
  }
};

int main(){
  vector<Point*> puntos;
  vector<Cluster*> clusters;

  puntos.push_back(new Point(1, 1));
  puntos.push_back(new Point(1, 0));
  puntos.push_back(new Point(0, 2));
  puntos.push_back(new Point(2, 4));
  puntos.push_back(new Point(3, 5));

  clusters.push_back(new Cluster(1, 1));
  clusters.push_back(new Cluster(0, 2));

  printf("points:\n");
  for(int i=0; i<puntos.size(); i++){
    printf(" x:%0.1f\ty:%0.1f\n", puntos[i]->x, puntos[i]->y);
  }
  printf("\nclusters:\n");
  for(int i=0; i<clusters.size(); i++){
    printf(" x:%0.1f\ty:%0.1f\n", clusters[i]->x, clusters[i]->y);
  }

  for(int iteration=0; iteration<10; iteration++){
    bool points_same_clusters = true;
    for(int punto=0; punto<puntos.size(); punto++){
      printf("distance from %0.1f,%0.1f\n", puntos[punto]->x, puntos[punto]->y);
      double min = 999999;
      int closestCluster;
      for(int cluster=0; cluster<clusters.size(); cluster++){
        float differenceX = puntos[punto]->x - clusters[cluster]->x;
        float differenceY = puntos[punto]->y - clusters[cluster]->y;
        float distance = sqrt(pow(differenceX,2)+pow(differenceY,2));
        printf(" to %0.1f,%0.1f = %0.1f\n", clusters[cluster]->x, clusters[cluster]->y, distance);
        if(distance<min){
          min = distance;
          closestCluster = cluster;
        }
      }
      puntos[punto]->previous_cluster = puntos[punto]->cluster;
      puntos[punto]->cluster = closestCluster;
      if(puntos[punto]->previous_cluster != closestCluster) points_same_clusters = false;
      printf(" closestCluster:%d, previous cluster:%d\n", closestCluster, puntos[punto]->previous_cluster);
      clusters[closestCluster]->totalX += puntos[punto]->x;
      clusters[closestCluster]->totalY += puntos[punto]->y;
      clusters[closestCluster]->points++;
    }
    printf("\nnew cluster positions:\n");
    for(int cluster=0; cluster<clusters.size(); cluster++){
      clusters[cluster]->x = clusters[cluster]->totalX / clusters[cluster]->points;
      clusters[cluster]->y = clusters[cluster]->totalY / clusters[cluster]->points;
      printf(" cluster %d -> %0.1f,%0.1f\n", cluster, clusters[cluster]->x, clusters[cluster]->y);
      clusters[cluster]->totalX = 0;
      clusters[cluster]->totalY = 0;
      clusters[cluster]->points = 0;
    }
    printf("\n_______________________\n");
    if(points_same_clusters) iteration = 10;  // end
  }

  return 0;
}
