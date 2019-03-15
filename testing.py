import os

f1 = open('norm_results.txt', 'tr')
f2 = open('reference_result.txt', 'tr')


l1 = f1.readlines()
l2 = f2.readlines()

s1 = set(l1)
s2 = set(l2)

for i in (s1^s2):
    print(i)
