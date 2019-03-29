#! /usr/bin/env python
import sys
import os
import commands
import string
import optparse

#masses = ["3000"]

#vec1 = ("1000", "20", "03", "02")
#vec2 = ("2000", "20", "03", "02")
#vec3 = ("3000", "20", "03", "02")
#vec4 = ("4000", "20", "03", "02")
#vec5 = ("3000", "1", "03", "02")
#vec6 = ("3000", "50", "03", "02")
#vec7 = ("3000", "100", "03", "02")
#vec8 = ("3000", "20", "01", "02")
#vec9 = ("3000", "20", "05", "02")
#vec10 = ("3000", "20", "07", "02")
#vec11 = ("3000", "20", "03", "01")
#vec12 = ("3000", "20", "03", "05")
#vec13 = ("3000", "20", "03", "1")

#points = [vec1, vec2, vec3, vec4, vec5, vec6, vec7, vec8, vec9, vec10, vec11, vec12, vec13]

vec1 = ("500", "20", "03", "peak")
vec2 = ("600", "20", "03", "peak")
vec3 = ("700", "20", "03", "peak")
vec4 = ("800", "20", "03", "peak")
vec5 = ("900", "20", "03", "peak")
vec6 = ("1000", "20", "03", "peak")
vec7 = ("1100", "20", "03", "peak")
vec8 = ("1200", "20", "03", "peak")
vec9 = ("1300", "20", "03", "peak")
vec10 = ("1400", "20", "03", "peak")
vec11 = ("1500", "20", "03", "peak")
vec12 = ("1600", "20", "03", "peak")
vec13 = ("1700", "20", "03", "peak")
vec14 = ("1800", "20", "03", "peak")
vec15 = ("1900", "20", "03", "peak")
vec16 = ("2000", "20", "03", "peak")
vec17 = ("2100", "20", "03", "peak")
vec18 = ("2200", "20", "03", "peak")
vec19 = ("2300", "20", "03", "peak")
vec20 = ("2400", "20", "03", "peak")
vec21 = ("2500", "20", "03", "peak")
vec22 = ("2600", "20", "03", "peak")
vec23 = ("2700", "20", "03", "peak")
vec24 = ("2800", "20", "03", "peak")
vec25 = ("2900", "20", "03", "peak")
vec26 = ("3000", "20", "03", "peak")
vec27 = ("3100", "20", "03", "peak")
vec28 = ("3200", "20", "03", "peak")
vec29 = ("3300", "20", "03", "peak")
vec30 = ("3400", "20", "03", "peak")
vec31 = ("3500", "20", "03", "peak")
vec32 = ("3600", "20", "03", "peak")
vec33 = ("3700", "20", "03", "peak")
vec34 = ("3800", "20", "03", "peak")
vec35 = ("3900", "20", "03", "peak")
vec36 = ("4000", "20", "03", "peak")
vec37 = ("4100", "20", "03", "peak")
vec38 = ("4200", "20", "03", "peak")
vec39 = ("4300", "20", "03", "peak")
vec40 = ("4400", "20", "03", "peak")
vec41 = ("4500", "20", "03", "peak")

points = [vec1, vec2, vec3, vec4, vec5, vec6, vec7, vec8, vec9, vec10, vec11, vec12, vec13, vec14, vec15, vec16, vec17, vec18, vec19, vec20, vec21,vec22, vec23, vec24, vec25, vec26, vec27, vec28, vec29, vec30, vec31, vec32, vec33, vec34, vec35, vec36, vec37, vec38, vec39, vec40, vec41]

points = [vec26]

def getLimits(optdir, post):
      
   i = 0;

   for item in points:
         
      mZprime=item[0]
      mDark=item[1]
      rinv=item[2]
      alpha=item[3]

      filename = "%s/SVJ_mZprime%s_mDark%s_rinv%s_alpha%s/asymptotic_mZprime%s_mDark%s_rinv%s_alpha%s%s.log" % \
(optdir, mZprime, mDark, rinv, alpha, mZprime, mDark, rinv, alpha, post)
      os.system(("grep \"r < \" %s| awk '/Observed Limit/{f=1}f'") % (filename))
      os.system(("grep \"r < \" %s| awk '{print $5}' >> a%s") % (filename, i))
      
      print ("grep \"r < \" %s| awk '{print $5}' >> a%i") % (filename, i)  
    
      count=0
      with open (('a%i' % i), 'rb') as f:
         for line in f:
            count += 1
            
      if(count < 2):
         os.system("echo '0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n' >> a%i" % i)
      i = 1 + i
 
   os.system("echo 'y_observed" + post + "        '>> left")
   os.system("echo 'y_down_points2" + post + "    '>> left")
   os.system("echo 'y_down_points1" + post + "    '>> left")
   os.system("echo 'y_vals" + post + "            '>> left")
   os.system("echo 'y_up_points1" + post + "      '>> left")
   os.system("echo 'y_up_points2" + post + "      '>> left")
   
   for i in xrange(len(points)):
         os.system("echo ' '>>commas")
         os.system("echo ' '>>right")
         
   os.system("rm data/limit"+post + ".txt")
   print "rm data/limit"+post + ".txt"
   #os.system("paste left a0 commas a1 commas a2 commas a3 commas a4 commas a5 commas a6 commas a7 commas a8 commas a9 commas a10 commas a11 commas a12 commas a13 commas a14 commas a15 commas a16 commas a17 commas a18 commas a19 commas a20 commas a21 commas a22 commas a23 commas a24 commas a25 commas a26 commas a27 commas a28 commas a29 commas a30 commas a31 commas a32 commas a33 commas a34 commas a35 commas a36 commas a37 commas a38 commas a39 commas a40 right  > data/limit" + post + ".txt")
   os.system("paste left a0 right  > data/limit" + post + ".txt")
   #print "paste left a0 commas a1 commas a2 commas a3 commas a4 commas a5 commas a6 commas a7 commas a8 commas a9 commas a10 commas a11 commas a12 commas a13 commas a14 commas a15 commas a16 commas a17 commas a18 commas a19 commas a20 commas a21 commas a22 commas a23 commas a24 commas a25 commas a26 commas a27 commas a28 commas a29 commas a30 commas a31 commas a32 commas a33 commas a34 commas a35 commas a36 commas a37 commas a38 commas a39 commas a40 right > data/limit" + post + ".txt"
   
   print "paste left a0 right > data/limit" + post + ".txt"
   os.system("more data/limit"+post + ".txt")

   os.system("rm -rf left right commas a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 a16 a17 a18 a19 a20 a21 a22 a23 a24 a25 a26 a27 a28 a29 a30 a31 a32 a33 a34 a35 a36 a37 a38 a39 a40")
      
