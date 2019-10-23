/*
This code is adapted from Boyar and Peralta's algorithm which can be found here: https://github.com/rub-hgi/shorter_linear_slps_for_mds_matrices
While the structure of the codes remain unchanged, we have made several changes to the original file:
1. Changing the criteria to RNBP, A1 and A2 as described in the paper attached
2. The format of the input file
3. Some small changes to the 'reachable' function so that the calculation is more efficient

In order to run this program, you need to compile it with C++11 or newer. Also, you need to input 2 arguments:
TIME_LIMIT - The amount of time (in seconds) allowed to run the program
OPTION - The algorithm to be compiled 
        OPTION=1 - RNBP
        OPTION=2 - A1
        OPTION=3 - A2
An example command will be:
        g++ -std=c++11 -o main_globalopt.out -D OPTION=1 -D TIME_LIMIT=1000 main_globalopt.cpp

To run the program, we feed the matrix into the program:
        ./main_globalopt.out < ./test/testmat.txt

An example of an input matrix will be:
15 15
0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
0 0 1 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 1 0 0 0 0 0
1 0 1 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 1 0 0 0 1 0 1 0 0
0 0 0 0 0 0 0 0 0 1 1 0 1 0 0
1 0 0 0 0 0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 1 0 1
0 0 0 0 1 0 0 0 0 0 0 0 1 0 0
0 0 0 0 1 0 0 0 1 0 0 0 1 0 0
0 0 0 0 0 1 0 1 0 0 0 0 0 0 0
*/


#include <math.h>
#include <ctype.h>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <time.h>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>
#include <random>


using namespace std;

const int MaxBaseSize=1000;
const bool PRINTROWS=true;
        
#define SIZE 32
#define LOOP_SIZE 100
#define LARGE 100000
#define computeSum(table,table_size,s) s=0; for(int sum_i=0; sum_i<table_size; sum_i++) s+=table[sum_i];

#ifndef OPTION
#define OPTION -1
#endif

#ifndef TIME_LIMIT
#define TIME_LIMIT -1
#endif

int NumInputs;
int NumTargets;
int XorCount;
long long int Target[MaxBaseSize];
int Dist[MaxBaseSize]; //distance from current base to Target[i]
int NDist[MaxBaseSize]; //what Dist would be if NewBase was added
long long int Base[MaxBaseSize];
string Program[MaxBaseSize];
int BaseSize;
int TargetsFound;
int InitDist[MaxBaseSize]; // storing the initial distance
long long int NewBase; //global variable containing a candidate new base
mt19937 rand_generator;

struct Element
{
    int parent_i;
    int parent_j;
    int newDist[SIZE];
};

void InitBase(); // refresh the base for subsequent rounds
void ReadTargetMatrix();
bool is_base(long long int x);
int NewDistance(int u); //calculates the distance from the base to Target[u]
void TotalDistance(); //returns the sum of distances to targets
bool reachable(long long int T, int K, int S);
bool EasyMove(); //if any two bases add up to a target, pick them
void PickNewBaseElement();
void refreshDist(); // refresh the distance to the targets for subsequent rounds
int RNBP(Element AllElements[], int counter); // RNBP
int A1(Element AllElements[], int counter); // A1
int A2(Element AllElements[], int counter); // A2
int calculateDist(int A[],int length);
int calculateNorm(int A[],int length);
bool filtering(int tempDist[], vector<int> filter_indices);

int main(int argc, char *argv[]) {
    // reading the target matrix in text file
    // setting up the distance
    ReadTargetMatrix();
    // Large value for initialization
    int BestCount = LARGE;
    clock_t start = clock();
    int best_time;
    // Number of rounds
    while ((clock()-start)/CLOCKS_PER_SEC < TIME_LIMIT) {
        XorCount = 0;
        // refreshing the distance and base for subsequent rounds
        refreshDist();
        InitBase();

        // main loop
        while (TargetsFound < NumTargets) {
            if (!EasyMove()) PickNewBaseElement();
        }

        // Once all the targets have been found, print out
        if (TargetsFound == NumTargets)
        {
            cout << "SLP Heuristic XorCount: " << XorCount << endl;
        }
        if (XorCount < BestCount)
        {
            cout << "Accumulated Time: " << (clock()-start)/CLOCKS_PER_SEC << endl;
            best_time = (clock()-start)/CLOCKS_PER_SEC;
            BestCount = XorCount;
            for (int j = 0; j < XorCount; j++) {
                cout << Program[NumInputs + j] << endl;
            }
        }
    }
    // check if it is stablized
    if (best_time < ((clock()-start)/2)/CLOCKS_PER_SEC) cout << "Stable" << endl;
    else cout << "Unstable" << endl;

    return 0;
}

void InitBase() {
    TargetsFound = 0;
    Base[0] = 1;
    Program[0] = "x0";
    stringstream ss;
    string s;
    for (int i = 1; i < NumInputs; i++) {
        ss << i;
        s = ss.str();
        Base[i] = 2*Base[i-1];
        Program[i] = "x" + s;
        ss.str("");
    }
    BaseSize = NumInputs; //initial base is just the xi's
    for (int i = 0; i < NumTargets; i++) {
        if (Dist[i] == 0) {
            TargetsFound++;
        }
    }
}

void TotalDistance() { //returns the sum of distances to targets
    int D = 0;
    int t;
    for (int i = 0; i < NumTargets; i++) {
        t = NewDistance(i);
        NDist[i] = t;
    }
}

bool EasyMove() {
    int t;
    bool foundone = false;

    //see if anything in the distance vector is 1
    for(int i = 0; i < NumTargets; i++) {
        if (Dist[i] == 1) {
            foundone = true;
            t = i;
            break;
        }
    }
    if (!foundone) {
        return false;
    }
    //update Dist array
    NewBase = Target[t];
    for (int u = 0; u < NumTargets; u++) {
        Dist[u] = NewDistance(u);
    }
    //update Base with NewBase
    Base[BaseSize] = NewBase;
    //find which lines in Base caused this
    string a,b;
    for (int i = 0; i < BaseSize; i++) {
        for (int j = i + 1; j < BaseSize; j++) {
            if ((Base[i] ^ Base[j]) == Target[t]) {
                a = Program[i].substr(0, Program[i].find(" "));
                b = Program[j].substr(0, Program[j].find(" "));
                break;
            }
        }
    }
    stringstream ss;
    string s1;
    ss << t;
    s1 = ss.str();
    ss.str("");
    Program[BaseSize] = "y" + s1 + " = " + a + " + " + b;
    BaseSize++;
    XorCount++;
    TargetsFound++;
    return true;
}

// PickNewBaseElement is only called when there are no 1's in Dist[]
void PickNewBaseElement() {
    // Allocate memory for all possible bases
    Element* AllElements = new Element[BaseSize*(BaseSize-1)];
    int counter = 0; // counter to track last element

    for (int i = 0; i < BaseSize - 1; i++) {
        for (int j = i+1; j < BaseSize; j++) {
            NewBase = Base[i] ^ Base[j];
            TotalDistance(); //this calculates NDist[]

            // Putting in the data into the array
            for (int k = 0; k < NumTargets; k++)
            {
                AllElements[counter].newDist[k] = NDist[k];
            }
            AllElements[counter].parent_i = i;
            AllElements[counter].parent_j = j;
            counter++;
        }
    }
    int chosen;
    // selecting the best pair to XOR
    if (OPTION == 1) chosen = RNBP(AllElements,counter);
    else if (OPTION == 2) chosen = A1(AllElements,counter);
    else if (OPTION == 3) chosen = A2(AllElements,counter);
    

    // Update using the result returned by the criteria
    int bestparent_i = AllElements[chosen].parent_i;
    int bestparent_j = AllElements[chosen].parent_j;
    Base[BaseSize] = Base[bestparent_i] ^ Base[bestparent_j];

    // Update the Dist Array
    for (int i = 0; i < NumTargets; i++) {
        Dist[i] = AllElements[chosen].newDist[i];
    }


    string a = Program[bestparent_i].substr(0, Program[bestparent_i].find(" "));
    string b = Program[bestparent_j].substr(0, Program[bestparent_j].find(" "));
    stringstream ss;
    string s2;
    ss << XorCount;
    s2 = ss.str();
    ss.str("");
    Program[BaseSize] = "t" + s2 + " = " + a + " + " + b;
    BaseSize++;
    XorCount++;

    // free up the memory
    free(AllElements);

    return;
}
// Original BP random criteria
int RNBP(Element AllElements[], int counter)
{
    // initialization
    int bestDist = LARGE;
    int bestNorm = -1*LARGE;
    int currentDist, currentNorm;
    vector<int> candidates;
    for (int i = 0; i < counter; i++)
    {
        currentDist = calculateDist(AllElements[i].newDist,NumTargets);
        currentNorm = calculateNorm(AllElements[i].newDist,NumTargets);
        if ((currentDist < bestDist) || (currentDist == bestDist && currentNorm > bestNorm))
        {
            // Updating the best distance and norm
            bestDist = currentDist;
            bestNorm = currentNorm;
            // clear previous candidates
            candidates.clear();
            // inputting the new candidates
            candidates.push_back(i);
        }
        else if (currentDist == bestDist && currentNorm == bestNorm)
        {
            // equal candidates
            candidates.push_back(i);
        }
    }

    // randomly choose one of the candidates
    rand_generator.seed(time(0));
    uniform_int_distribution<int> rand_distribution(0,candidates.size()-1);
    int rand_num = rand_distribution(rand_generator);
    return candidates[rand_num];
}

int A1(Element AllElements[], int counter)
{
    // Applying the Filter
    int nearest = 1; // change this to relax the filter of nearest targets
    int filter_dist; // keep track of the largest distance that will pass through the filter
    vector<int> filter_indices; // keep track of the indices of Target that satisfy the filter

    // sort the distance array
    int sorted_dist[NumTargets-TargetsFound];
    int next_index = 0;
    for (int i = 0; i < NumTargets; i++)
    {
        if (Dist[i] == 0) continue;
        sorted_dist[next_index++] = Dist[i];
    }
    sort(sorted_dist,sorted_dist+NumTargets-TargetsFound);

    // indices that can pass through the filter
    filter_dist = sorted_dist[min(nearest-1,NumTargets-TargetsFound-1)]; // largest distance that will pass through the filter
    for (int i = 0; i < NumTargets; i++)
    {

        if (Dist[i] <= filter_dist && Dist[i] > 0) 
        {
            filter_indices.push_back(i);
        }
    }

    // initialization
    int bestDist = LARGE;
    int bestNorm = -1*LARGE;
    int currentDist, currentNorm;
    vector<int> candidates;


    for (int i = 0; i < counter; i++)
    {
        // Filtering
        if (!filtering(AllElements[i].newDist, filter_indices)) continue;
        // Normal BP rand
        currentDist = calculateDist(AllElements[i].newDist,NumTargets);
        currentNorm = calculateNorm(AllElements[i].newDist,NumTargets);
        if ((currentDist < bestDist) || (currentDist == bestDist && currentNorm > bestNorm))
        {
            // Updating the best distance and norm
            bestDist = currentDist;
            bestNorm = currentNorm;
            // clear previous candidates
            candidates.clear();
            // inputting the new candidates
            candidates.push_back(i);
        }
        else if (currentDist == bestDist && currentNorm == bestNorm)
        {
            // equal candidates
            candidates.push_back(i);
        }
    }

    // randomly choose one of the candidates
    rand_generator.seed(time(0));
    uniform_int_distribution<int> rand_distribution(0,candidates.size()-1);
    int rand_num = rand_distribution(rand_generator);
    return candidates[rand_num];
}


// BP rand with the filter of choosing the nearest target
int A2(Element AllElements[], int counter)
{
    // Applying the Filter
    int nearest = 1; // change this to relax the filter of nearest targets
    int filter_dist; // keep track of the largest distance that will pass through the filter
    vector<int> filter_indices; // keep track of the indices of Target that satisfy the filter

    // sort the distance array
    int sorted_dist[NumTargets-TargetsFound];
    int next_index = 0;
    for (int i = 0; i < NumTargets; i++)
    {
        if (Dist[i] == 0) continue;
        sorted_dist[next_index++] = Dist[i];
    }
    sort(sorted_dist,sorted_dist+NumTargets-TargetsFound);

    // indices that can pass through the filter
    filter_dist = sorted_dist[min(nearest-1,NumTargets-TargetsFound-1)]; // largest distance that will pass through the filter
    for (int i = 0; i < NumTargets; i++)
    {

        if (Dist[i] <= filter_dist && Dist[i] > 0) 
        {
            filter_indices.push_back(i);
        }
    }

    // initialization
    int bestDist = LARGE;
    int currentDist;
    vector<int> candidates;


    for (int i = 0; i < counter; i++)
    {
        // Filtering
        if (!filtering(AllElements[i].newDist, filter_indices)) continue;
        // Normal BP rand
        currentDist = calculateDist(AllElements[i].newDist,NumTargets);
        if (currentDist < bestDist)
        {
            // Updating the best distance and norm
            bestDist = currentDist;
            // clear previous candidates
            candidates.clear();
            // inputting the new candidates
            candidates.push_back(i);
        }
        else if (currentDist == bestDist)
        {
            // equal candidates
            candidates.push_back(i);
        }
    }
    // randomly choose one of the candidates
    rand_generator.seed(time(0));
    uniform_int_distribution<int> rand_distribution(0,candidates.size()-1);
    int rand_num = rand_distribution(rand_generator);
    return candidates[rand_num];
}


bool filtering(int tempDist[], vector<int> filter_indices)
{
    for (int i = 0; i < filter_indices.size(); i++)
    {
        // if any of the acceptable distance is reduced, return true immediately
        if (tempDist[filter_indices[i]] < Dist[filter_indices[i]]) return true;
    }
    return false;
}

 
int calculateDist(int A[],int length)
{
    int s = 0;
    for (int i = 0; i < length; i++) s += A[i];
    return s;
}
int calculateNorm(int A[],int length)
{
    int s = 0;
    for (int i = 0; i < length; i++) s += A[i]*A[i];
    return s;
}

void refreshDist(){
    for(int k = 0; k < 32; k++) Dist[k] = InitDist[k];
}

void ReadTargetMatrix() {
    cin >> NumTargets;
    cin >> NumInputs;
    //check that NumInputs is < wordsize
    if (NumInputs >= 8*sizeof(long long int)) {
        cout << "too many inputs" << endl;
        exit(0);
    }

    int bit;
    for (int i = 0; i < NumTargets; i++) { //read row i
        long long int PowerOfTwo  = 1;
        Target[i] = 0;
        Dist[i] = -1; //initial distance from Target[i] is Hamming weight - 1
        for (int j = 0; j < NumInputs; j++) {
            cin >> bit;
            if (bit) {
                Dist[i]++;
                Target[i] = Target[i] + PowerOfTwo;
            }
            PowerOfTwo = PowerOfTwo * 2;
        }
    }
    // Update the InitDist for subsequent rounds
    for (int k = 0; k < 32; k++) InitDist[k] = Dist[k];
}

bool is_base(long long int x) {
    //sanity check, shouldn't ask if 0 is base
    if (x==0) {
        cout << "asking if 0 is in Base " << endl;
        exit(0);
    }

    for (int i = 0; i < BaseSize; i++) {
        if (x == Base[i]) {
            return true;
        }
    }
    return false;
}

// Distance is 1 less than the number of elements
// in the base that I need to add in order to get Target[u].
// The next function calculates the distance from the base,
// augmented by NewBase, to Target[u]. Uses the following observations:
// Adding to the base can only decrease distance.
// Also, since NewBase is the sum of two old base
// elements, the distance from the augmented base
// to Target[u] can decrease at most by 1. If the
// the distance decreases, then NewBase must be one
// of the summands.

int NewDistance(int u) {
    //if Target[u] is in augmented base return 0;
    if (is_base(Target[u]) || (NewBase == Target[u])) {
        return 0;
    }

    // Try all combinations of Dist[u]-1 base elements until one sums
    // to Target[u] + NewBase. If this is true, then Target[u] is the
    // sum of Dist[u] elements in the augmented base, and therefore
    // the distance decreases by 1.

    if (reachable(Target[u] ^ NewBase, Dist[u] - 1, NumInputs)) {
        return (Dist[u]-1);
    } else {
        return Dist[u]; //keep old distance
    }
}



//return true if T is the sum of K elements among Base[S..BaseSize-1]
bool reachable(long long int T, int K, int S) {
    if (__builtin_popcount(T) <= K)
    {
        return true;
    }
    if (S > BaseSize-1) {
        return false; //exceeded count
    }

    if (K==0) {
        return false; //this is probably not reached
    }

    if (K==1) {
        for (int i=S; i < BaseSize; i++) if (T == Base[i]) {
            return true;
        }
        return false;
    }
    
    //consider those sums containing Base[S]
    if (reachable(T^Base[S], K-1, S+1)) {
        return true;
    }

    //consider those sums not containing Base[S]
    if (reachable(T, K, S+1)) {
        return true;
    }


    //not found
    return false;
}
