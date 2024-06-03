import numpy as np
n=int(input().strip())

array=[]
while len(array) < n:
    input=input().strip()
    input=[int(element) for element in input.split(' ')]
    array+=input
array=array[:n]

results=np.zeros((n,n))
for i in range(n):
    for j in range(0,n-i):
        if i==0:
            results[j][j]=array[j]
        else:
            results[j][j+i]=max(array[j]-results[j+1][j+i], array[j+i]-results[j][j+i-1])
    
if results[0][n-1]>0:
    print("Player 1 wins")
elif results[0][n-1]<0:
    print("Player 2 wins")
else:
    print("Its a draw")