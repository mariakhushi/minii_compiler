t0 = 5
a = t0
t1 = 3
b = t1
t2 = a
t3 = b
t4 = t2 > t3
ifFalse t4 goto L0
t5 = a
t6 = b
t7 = t5 - t6
print t7
goto L1
label L0
t8 = b
t9 = a
t10 = t8 - t9
print t10
label L1
t11 = 0
i = t11
label L2
t12 = i
t13 = 3
t14 = t12 < t13
ifFalse t14 goto L3
t15 = i
print t15
t16 = i
t17 = 1
t18 = t16 + t17
i = t18
goto L2
label L3