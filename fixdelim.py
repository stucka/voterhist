#!/usr/bin/python
f1 = open('DailyVoterBase_Delimited.txt', 'r')
f2 = open('DelimV2.txt', 'w')
mycount=-1
for line in f1:
    f2.write(line.replace('"', ''))
    mycount+=1
f1.close()
f2.close()
print "Processed " + str(mycount) + " rows of data, not counting header."
