//
//  KDTree.cpp
//  kd-tree
//
//  Created by 马子殷 on 7/9/17.
//  Copyright © 2017 马子殷. All rights reserved.
//

#include <algorithm>
#include <iostream>
#include <vector>
#include <sstream>

#include "KDTree.hpp"

template<int ndim>
KDTree<ndim>::KDTree(double **data, int ndata) {
    // Build KDTree with given col-wise data, length specified as ndata
    
    this->head = NULL;
    this->inv_ref = NULL;
    this->data = data;
    this->ndata = ndata;
    this->index = new int[ndata];
    for(int i=0; i<ndata; ++i) {
        this->index[i] = i;
    }
    this->buildTree();
}

template<int ndim>
KDTree<ndim>::~KDTree() {
    for(int i=0; i<this->ndata; ++i) {
        delete this->inv_ref[i];
    }
    delete[] this->inv_ref;
    this->inv_ref = NULL;
    this->head = NULL;
    delete[] this->index;
    this->index = NULL;
}

template <int ndim>
KDTree<ndim>::KDTree(const KDTree<ndim>& t) {
    throw "Not implemented!";
}

//template <int ndim>
//void KDTree<ndim>::recDeleteNode(KDTree::Node *n){
//    if(n == NULL)
//        return;
//    recDeleteNode(n->l);
//    recDeleteNode(n->r);
//    n->l = n->r = NULL;
//    delete n;
//}

template<int ndim>
void KDTree<ndim>::buildTree() {
    // Call rec procedure to build tree
    this->inv_ref = new Node*[this->ndata];
    this->head = this->recBuildTree(0, 0, this->ndata);
}

template<int ndim>
typename KDTree<ndim>::Node* KDTree<ndim>::recBuildTree(int dim, int start, int end) {
    if(end - start <= 0) {
        return NULL;
    }
    else if(end - start == 1) {
        Node* n = new Node{dim, start, this->data[dim][start], NULL, NULL, NULL};
        this->inv_ref[start] = n;
        return n;
    }
    
    int mid = this->median(dim, start, end);
    int next_dim = (dim + 1) % ndim;
    Node* l = recBuildTree(next_dim, start, mid);
    Node* r = recBuildTree(next_dim, mid + 1, end);
    Node* node  = new Node{dim, mid, this->data[dim][mid], l, r, NULL};
    if(l != NULL) {
        l->parent = node;
    }
    if(r != NULL) {
        r->parent = node;
    }
    this->inv_ref[mid] = node;
    return node;
}

template<int ndim>
int KDTree<ndim>::median(int dim, int start, int end) {
    // Rearrange this->index, so that data[:, index[start : end)] is in order, the median index is returned
    // Moreover, a less-equal : greater split is guaranteed
    
    //TODO: consider using O(n)
    double* row = this->data[dim];
    auto comp = [row](int a, int b) {
        return row[a] < row[b];
    };
    std::sort(this->index + start, this->index + end, comp);
    int ret = (start + end) / 2;
    while(ret < end - 1 && row[ret] == row[ret + 1]) {
        ret += 1;
    }
    return ret;
}

template<int ndim>
void KDTree<ndim>::print() {
    // Print the tree structure
    std::vector<Node *> vec {this->head};
    while(!vec.empty()) {
        std::vector<Node *> temp;
        std::cout << vec[0]->dim << ": ";
        for(Node *n : vec) {
            std::cout << this->printPoint(this->index[n->index]) << " ";
            if (n->l != NULL) {
                temp.push_back(n->l);
            }
            if (n->r != NULL) {
                temp.push_back(n->r);
            }
        }
        std::cout << std::endl;
        vec = temp;
    }
}

template<int ndim>
std::string KDTree<ndim>::printPoint(int i) {
    // Return string of a point with format "(dim0, dim1, ...)"
    std::ostringstream ss;
    ss << "(" << this->data[0][i];
    for(int dim=1; dim<ndim; ++dim) {
        ss << ',' << this->data[dim][i];
    }
    ss << ")";
    return ss.str();
}


template<int ndim>
typename KDTree<ndim>::Node* KDTree<ndim>::nearestNeighbour(std::array<double, ndim> &target, Node *start) {
    auto u_bound = std::array<double, ndim>();    // upper bound at each dimension
    auto l_bound = std::array<double, ndim>();
    for(int i=0; i<ndim; ++i) {
        u_bound[i] = INF;
        l_bound[i] = NEG_INF;
    }
    
    // Follow one path to 'optimal' leaf
    Node* p = start, last;
    while(p != NULL) {
        int dim = p->dim;
        if(target[dim] <= p->division) {         // go to smaller/euqal side
            u_bound[dim] = p->division;
            last = p;
            p = p->l;
        } else if(target[dim] > p->division) {  // go to greater side
            l_bound[dim] = p->division;
            last = p;
            p = p->r;
        }
    }
    
    double dist = INF, temp;
    Node *best = last, sibling, parent;
    // Back up from nearst leaf ('last')
    p = last;               // current focus
    while(true) {
        parent = p->parent;
        sibling = (parent->l == p) ? parent->r : parent->l;
        // if p is a better solution, substitue 'best'
        temp = this->norm_distance(p->index, target);
        if(temp < dist) {
            best = p;
        }
        // if sibling resides in sphere, consider sibling
        if(false  /*TODO:  */) {
            auto ret = this->nearestNeighbour(target, sibling);
            // TODO:
            
        }
        //TODO:
        
    }
}

template <int ndim>
bool KDTree<ndim>::intersect(std::array<double, ndim>& center, double dist, std::array<double, ndim>& u_bound, std::array<double, ndim>& l_bound, int dim) const {
    // This implementation applies to determing whether a sphere centered OUTSIDE a rect (while reside beside a dim) intersects with the rect defined by u_/l_bound.
    
    double min_dist = std::min(std::abs(center[dim] - l_bound[dim]), std::abs(center[dim] - u_bound[dim]));
    return min_dist >= dist;
}

template <int ndim>
double KDTree<ndim>::normDistance(int col, const std::array<double, ndim> &target)const {
    // return distance between data[:, col] and target, without sqrt or root
    // TODO: this is a weird pair of arguments...
    double dist = 0;
    for(int i=0; i<ndim; ++i) {
        double temp = this->data[i][col] - target[i];
        dist += temp * temp;
    }
    return dist;
}

void testKDTree() {
    double a1[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    double a2[] = {6, 4, 3, 4, 7, 3, 1, 8, 5};
    double **data = new double* [2];
    data[0] = a1;
    data[1] = a2;
    KDTree<2> kdt(data, 9);
    kdt.print();
}

