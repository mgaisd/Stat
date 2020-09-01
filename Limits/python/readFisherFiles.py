#python script to compile all the information about Fisher tests for all 55 signals


# path to files: on "root://cmseos.fnal.gov//store/user/cfallon/condorTest/SVJ_mZprime{}_mDark{}_rinv{}_alpha{}".format(mZ, mD, rI, aD)


import os

pae = "region paramVal alt params"

eosArea = "root://cmseos.fnal.gov//store/user/cfallon/biasStudies/"

delCmd = "rm -f tempFisher.txt"
for isAlt in (False, True):
	for region in ("highCut","lowCut","highSVJ2","lowSVJ2"):
		for mZ in range(1500,4600,100):
			mZ = str(mZ)
			if isAlt:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_alt_{}_2018.txt tempFisher.txt".format(mZ, "20", "03", "peak", region)
			else:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_{}_2018.txt tempFisher.txt".format(mZ, "20", "03", "peak", region)
			os.system(cmd)
			fisherFile = open("tempFisher.txt","r")
			order = 0
			for line in fisherFile:
				if "Order is" in line:
					order = line[9]
				if ((line[0] == order) and (not (line[-3:-1] in "sufficient"))):
					pae += region + " " + mZ + " " + str(isAlt) + " " + line
					continue
				elif ((line[0] == order) and (isAlt == True)):
					pae += region + " " + mZ + " " + str(isAlt) + " " + line
					continue
			fisherFile.close()
			os.system(delCmd)

		for mD in (1,5,10,20,30,40,50,60,70,80,90,100):
			mD = str(mD)
			if isAlt:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_alt_{}_2018.txt tempFisher.txt".format("3000", mD, "03", "peak", region)
			else:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_{}_2018.txt tempFisher.txt".format("3000", mD, "03", "peak", region)
			os.system(cmd)
			fisherFile = open("tempFisher.txt","r")
			order = 0
			for line in fisherFile:
				if "Order is" in line:
					order = line[9]
				if ((line[0] == order) and (not (line[-3:-1] in "sufficient"))):
					pae += region + " " + mD + " " + str(isAlt) + " " + line
					continue
				elif ((line[0] == order) and (isAlt == True)):
					pae += region + " " + mZ + " " + str(isAlt) + " " + line
					continue
			fisherFile.close()
			os.system(delCmd)

		for rI in ("0","01","02","03","04","05","06","07","08","09","1"):
			if isAlt:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_alt_{}_2018.txt tempFisher.txt".format("3000", "20", rI, "peak", region)
			else:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_{}_2018.txt tempFisher.txt".format("3000", "20", rI, "peak", region)
			os.system(cmd)
			fisherFile = open("tempFisher.txt","r")
			order = 0
			for line in fisherFile:
				if "Order is" in line:
					order = line[9]
				if ((line[0] == order) and (not (line[-3:-1] in "sufficient"))):
					pae += region + " " + rI + " " + str(isAlt) + " " + line
					continue
				elif ((line[0] == order) and (isAlt == True)):
					pae += region + " " + mZ + " " + str(isAlt) + " " + line
					continue
			fisherFile.close()
			os.system(delCmd)

		for aD in ("low","peak","high"):
			if isAlt:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_alt_{}_2018.txt tempFisher.txt".format("3000", "20", "03", aD, region)
			else:
				cmd = "xrdcp "+eosArea+"SVJ_mZprime{}_mDark{}_rinv{}_alpha{}/FisherTest_{}_2018.txt tempFisher.txt".format("3000", "20", "03", aD, region)
			os.system(cmd)
			fisherFile = open("tempFisher.txt","r")
			order = 0
			for line in fisherFile:
				if "Order is" in line:
					order = line[9]
				if ((line[0] == order) and (not (line[-3:-1] in "sufficient"))):
					pae += region + " " + aD + " " + str(isAlt) + " " + line
					continue
				elif ((line[0] == order) and (isAlt == True)):
					pae += region + " " + mZ + " " + str(isAlt) + " " + line
					continue
			fisherFile.close()
			os.system(delCmd)

print(pae)
