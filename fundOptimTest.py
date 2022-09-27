import pandas as pd
import numpy as np
from fundOptim import fundOptim

class fundOptimTest(fundOptim):
    
    def __init__(self, fileName, sheetName):
        fundOptim.__init__(self,fileName, sheetName)
        # rebalance period in days. Give zero for no rebalance
        self.rebalPeriod = [0,10,20,30,40,50,60,100]
        self.reoptimPeriod = [100,200,300,500]
        self.threshold = 5/100
        self.initDataPoints(0,0,-1,-1)
    
    def rebalance(self):
        """
        Function to rebalance the assets to its original weights
        """
        for i in range(self.n_var):
            # the excess sold is used to buy the deficient
            currentProp = self.assetGrowth[i,0]/np.sum(self.assetGrowth)
            self.assetGrowth[i,0]-= currentProp - self.weights[i]
    
    def assetGrowthCalc(self,i):
        """
        Function that calculates the asset growth

        Returns
        -------
        None.

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
        
        for i in range(len(self.reoptimPeriod)):
            self.portfolioValue = []
            temp = 0
            for j in range(0,len(self.wb),2*self.reoptimPeriod[i]):
                self.optimize(startIndex=j, endIndex=j+self.reoptimPeriod[i]-1)
                self.assetGrowth = np.ones((self.n_var,1))
                self.assetGrowth*=np.array(self.weights)
                endIndx = min(len(self.wb),j+2*self.reoptimPeriod[i]-1)
                for k in range(j+self.reoptimPeriod[i], endIndx):
                    self.assetGrowthCalc(k)
                temp+=np.sum(self.assetGrowth)
            
            self.portfolioValue.append(temp)
                    
        argmax = np.argmax(self.portfolioValue)
        print("Rebalance every {} days for return of {}".format(self.reoptimPeriod[argmax],
                                                                self.portfolioValue[argmax]))
        
    def test(self):
        """
        Funtion that sweeps time forward, recording the portfolio value. It 
        also rebalances periodically. Note that the weights of the assets are
        fixed and do not change with time.
        """
        endIndex = 2030 # this is approximately beg of 2019
        # running the initial optimization and getting the weights
        self.optimize(endIndex = endIndex)
        self.portfolioValue = []
        print(self.wb.iloc[endIndex+1,-1])
        for k in range(len(self.rebalPeriod)):
            self.assetGrowth = np.ones((self.n_var,1))
            self.assetGrowth*=np.array(self.weights)
            # print(np.sum(self.assetGrowth))
            
            for i in range(endIndex+1, len(self.wb)):
                # sweeping forward in time.
                self.assetGrowthCalc(i)                
                
                if self.rebalPeriod[k]==0:
                    continue
                elif (self.wb.iloc[i,-1] - self.wb.iloc[endIndex+1,-1]).days >= self.rebalPeriod[k]:
                    self.rebalance()
                    
            self.portfolioValue.append(np.sum(self.assetGrowth))
            
        argmax = np.argmax(self.portfolioValue)
        print("Rebalance every {} days for return of {}".format(self.rebalPeriod[argmax],
                                                                self.portfolioValue[argmax]))

test = fundOptimTest(r'C:\Users\abhij\naiveFundOptim\Daily_prices\portfolio.xlsx', 'Percent_change')
test.reOptimize()