import pandas as pd
import numpy as np
from fundOptim import fundOptim
import sys

class fundOptimTest(fundOptim):
    
    def __init__(self, fileName, sheetName):
        fundOptim.__init__(self,fileName, sheetName)
        # rebalance period in days. Give zero for no rebalance
        self.rebalPeriod = [0,10,20,30,40,50,60,100]
        self.reoptimPeriod = [700,1000,1200]
        self.threshold = 5/100
        self.initDataPoints(0,0,-1,-1)
        self.priceDf = pd.read_excel(r'C:\Users\abhij\naiveFundOptim\Daily_prices\portfolio.xlsx', 
                                    sheet_name='Price')
    
    def rebalance(self, i):
        """
        Function to rebalance the assets to its original weights
        """
        currentProp = self.assetGrowth/np.sum(self.assetGrowth)
        buyOrder = (- currentProp + self.weights)*\
                    np.reshape(np.array(self.priceDf.iloc[i-1, 0:-1]), (self.n_var,1))
        sellMask = np.where(buyOrder>200, 1, 0)
        self.assetGrowth-= (currentProp - self.weights)*sellMask
    
    def assetGrowthCalc(self,i):
        """
        Function that calculates the asset growth
        """
        for j in range(self.n_var):
            self.assetGrowth[j,0]=self.assetGrowth[j,0]*(1+self.wb.iloc[i,j])
    
    def reOptimize(self):
        """
        Function that reoptimizes periodically. The optimize function is run
        and the asset weights are updated. The function runs one period where 
        the weight is optimized and the next period the growth is monitored.
        This is then repeated until the end of observation points.
        """
        self.gainsDict={}
        self.portfolioValue = []
        
        for i in range(len(self.reoptimPeriod)):     
            
            temp = 0
            temp2={}
            
            for j in range(0,len(self.wb),2*self.reoptimPeriod[i]):
                
                self.optimize(startIndex=j, endIndex=j+self.reoptimPeriod[i]-1)
                self.assetGrowth = np.ones((self.n_var,1))
                self.assetGrowth*=np.array(self.weights)
                endIndx = min(len(self.wb),j+2*self.reoptimPeriod[i])
                
                for k in range(j+self.reoptimPeriod[i], endIndx):
                    self.assetGrowthCalc(k)
                    
                # subtracting -1 because we are interested in the gains and 
                # not the absoulte vaue of the invested amount
                temp+=np.sum(self.assetGrowth)-1
                temp2[self.wb.iloc[j,-1]] = np.sum(self.assetGrowth)-1
            
            self.gainsDict[self.reoptimPeriod[i]] = temp2
            self.portfolioValue.append(temp)
                    
        argmax = np.argmax(self.portfolioValue)
        print("Reoptimize every {} days for return of {}".format(self.reoptimPeriod[argmax],
                                                                self.portfolioValue[argmax]))
        
    def test(self, testPeriod_index):
        """
        Funtion that sweeps time forward, recording the portfolio value. It 
        also rebalances periodically. Note that the weights of the assets are
        fixed and do not change with time.

        Parameters
        ----------
        testPeriod_index : int
            This is the row index which indicates the last point to be used in the optimization routine.

        """
        # running the initial optimization and getting the weights
        self.optimize(endIndex = testPeriod_index)
        self.portfolioValue = []
        print(self.wb.iloc[testPeriod_index+1,-1])
        for k in range(len(self.rebalPeriod)):
            self.assetGrowth = np.ones((self.n_var,1))
            self.assetGrowth*=np.array(self.weights)
            # print(np.sum(self.assetGrowth))
            
            for i in range(testPeriod_index+1, len(self.wb)):
                # sweeping forward in time.
                self.assetGrowthCalc(i)                
                
                if self.rebalPeriod[k]==0:
                    continue
                elif (self.wb.iloc[i,-1] - self.wb.iloc[testPeriod_index+1,-1]).days >= self.rebalPeriod[k]:
                    self.rebalance(i)
                    
            self.portfolioValue.append(np.sum(self.assetGrowth))
            
        argmax = np.argmax(self.portfolioValue)
        print("Rebalance every {} days for return of {}".format(self.rebalPeriod[argmax],
                                                                self.portfolioValue[argmax]))
        print(self.portfolioValue)
        print(self.weights)

if __name__ == "__main__":
    """
    This file takes 3 arguments to work:
    Excel file name (string): The master excel file which contains the daily percent change of asset price.
    Sheet name (string): The sheet name which contains the data
    Index (int): This is the row number which denotes the row index from which algorithm testing should begin
    
    Please make sure to have \\ in the address of the excel file
    """
    file_name = sys.argv[1]
    sheet_name = sys.argv[2]
    index = sys.argv[3]
    test = fundOptimTest(fileName=file_name, sheetName=sheet_name)
    test.test(testPeriod_index=index)