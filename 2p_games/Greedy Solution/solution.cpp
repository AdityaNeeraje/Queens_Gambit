#include<bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }
    vector<vector<int>> dp(n, vector<int>(n, 0));
    for (int i = 0; i < n; i++) {
        for (int j=0; j + i < n; j++){
            if (i==0){
                dp[j][j]=a[j];
            }            
            else{
                dp[j][j+i]=max(a[j]-dp[j+1][j+i], a[j+i]-dp[j][j+i-1]);
            }
        }
    }
    if (dp[0][n-1]>0){
        cout << "Player 1 wins" << endl;
    }
    else if (dp[0][n-1]==0){
        cout << "Its a draw" << endl;
    }
    else {
        cout << "Player 2 wins" << endl;
    }
}