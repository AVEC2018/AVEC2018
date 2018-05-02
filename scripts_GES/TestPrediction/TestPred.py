import GlobalsVars as v
from GSMatching import gsOpen, gsMatch
import sys
sys.path.append("../Utils/")
from ConcArff import concGs, concRec
from FeatsNorm import normFeatures
from PostTreats import postTreatTest
from PredUtils import unimodalPredPrep, cccCalc
from Print import printValTest
sys.path.append(v.labLinearPath)
from liblinearutil import train, predict
import numpy as np
import scipy as sp
import timeit

#Unimodal prediction on Test partition
def unimodalPredTest(gs, c, tr, te, de, medf, nDim):
	gsTe = np.array(gs['test'])[:,nDim]
	gsDe = np.array(gs['dev'])[:,nDim]
	gsTr = np.array(gs['train'])[:,nDim]
	#We apply the median filter if necessary
	if (medf == 1) :
		tr = sp.signal.medfilt(tr)
		te = sp.signal.medfilt(te)
		de = sp.signal.medfilt(de)
	#Options for liblinear
	options = "-s "+str(v.sVal)+" -c "+str(c)+" -B 1 -q"
	#We learn the model on train
	model = train(gsTr,tr,options)
	#We predict on test data
	predTest = np.array(predict(gsTe,te,model,"-q"))[0]
	predDev = np.array(predict(gsDe,de,model,"-q"))[0]
	#We calculate the correlation and store it
	cccTest = cccCalc(np.array(predTest),gsTe)
	cccDev = cccCalc(np.array(predDev),gsDe)
	return cccTest, predTest, cccDev, predDev
#Fin unimodalPredictionDev

#Predict on test the best values found with Dev and print the results
def predictTest():
	for nDim in range(len(v.bAudio)):
		#Value/wSize/wStep/Delay/Complexity/MedianFilter/MethodMatching/BiasUse/ScaleUse/BiasValue/ScaleValue
		wSize = v.bAudio[nDim][1]
		wStep = v.bAudio[nDim][2]
		dl = v.bAudio[nDim][3]
		c = v.bAudio[nDim][4]
		medF = v.bAudio[nDim][5]
		method = v.bAudio[nDim][6]
		biasB = v.bAudio[nDim][7]
		scaleB = v.bAudio[nDim][8]
		bias = v.bAudio[nDim][9]
		scale = v.bAudio[nDim][10]
		#Var for storing differents CCC
		ccc = []
		#Concatenation of Gold Standards
		concGs()
		print(v.goodColor+"Test prediction in progress..."+v.endColor)
		#Concatenation of ARFF data
		concRec(wSize, wStep)
		#Normalisation of Features
		normFeatures(wSize, wStep)
		#We open the files for the unimodal prediction
		[tr,de, te] = unimodalPredPrep(wSize, wStep)
		#We open the files for the Gold Standard Matching
		[art, vat, dt] = gsOpen(wSize,wStep)
		#We matche GoldStandards with parameters(wStep/fsize) and stock them
		gs = gsMatch(method, dl, wSize, wStep, art, vat, dt)
		#DEV
		#We do the prediction on Dev/Test
		[cccTest, predTest, cccDev, predDev] = unimodalPredTest(gs, c, tr, te, de, medF, nDim)
		#Post-treatement
		[cccTest, cccDev] = postTreatTest(gs, predTest, cccTest, predDev, cccDev, bias, scale, biasB, scaleB, nDim)
		#We store the results
		ccc = [nDim, round(cccDev,2), round(cccTest,2), round(wSize,2), round(wStep,2), round(dl,2), c, medF, method, biasB, scaleB, bias, scale]
		printValTest(ccc)
#End predictTest

predictTest()