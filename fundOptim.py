import pandas as pd
import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

class MPT (Problem):
    def __init__(self,n_var,x_lbounds,x_ubounds,cov_matrix,mean_rtrns):
        super().__init__(n_var = n_var, n_obj = 1, n_constr = 2, 
                         xl = x_lbounds, xu = x_ubounds)
        self.mean_rtrns = mean_rtrns
        self.cov_matrix = cov_matrix
    
    def _evaluate(self, X, out, *args, **kwargs):
        f1 = np.diag(np.matmul(np.matmul(X,self.cov_matrix),
                               np.transpose(X))).reshape([100,1])
        f2 = np.matmul(X,self.mean_rtrns).reshape([100,1])
        
        epsilon = (10**-3)
        sum_wts = np.sum(X,axis=1)
        g1 = (1-epsilon)-sum_wts
        g2= sum_wts-(1+epsilon)
        out["F"] = np.column_stack([f1/f2])
        out["G"] = np.column_stack([g1,g2])

class fundOptim:
    
    def __init__(self,fileName,sheetName):
        self.wb = pd.read_excel(fileName,
                           sheet_name =sheetName)
        self.wb.iloc[:,-1] = pd.to_datetime(self.wb.iloc[:,-1])
        self.wb.iloc[:,-1] = self.wb.iloc[:,-1].to_numpy()
    
    def initDataPoints(self,startIndex,startCol,endIndex,endCol):
        """
        Function that initializes the mean and covariance matrix depending
        on the start and end date of the observations. This is needed to 
        re-evaluate the weights if necessary.

        Parameters
        ----------
        startIndex : int
            index that denotes the start of the observation.
        endIndex : int (default = -1)
            index that denotes the end of the observation.

        """
        self.mnthly_rtrns = self.wb.iloc[startIndex:endIndex, startCol:endCol] 
        self.n_var = self.mnthly_rtrns.shape[1]
        self.mnthly_rtrns = self.mnthly_rtrns.to_numpy()
        self.cov_matrix = np.cov(self.mnthly_rtrns.astype(float), 
                                 rowvar = False)
        self.mean_rtrns = np.mean(self.mnthly_rtrns, axis = 0).\
            reshape([self.n_var,1])
        self.x_ubounds = 0.3 * np.ones(self.n_var)
        self.x_lbounds = np.zeros(self.n_var)
        self.xi = (1/self.n_var)* np.ones([1,self.n_var]) +\
            np.random.randn(100,self.n_var)
        self.algorithm = NSGA2(pop_size = 100, sampling = self.xi)
        self.problem = MPT(n_var=self.n_var,x_lbounds = self.x_lbounds,
                           x_ubounds=self.x_ubounds, 
                           cov_matrix= self.cov_matrix,
                           mean_rtrns=self.mean_rtrns)      
    
    def optimize(self,startIndex=0,startCol=0,
                 endIndex=-1, endCol=-1):
        """       
        Function that calculates the weights of the assets based on the modern
        portfolio theory.
        Parameters
        ----------
        startIndex : int (default = 0)
            index that denotes the start of the observation.
        startCol : int (default = 0)
            index that denotes the start of column of the observation.
        endIndex : int (default = -1)
            index that denotes the end of the observation.
        endCol : int (default = -2)
            index that denotes the end of column of the observation.
        """
        self.initDataPoints(startIndex,startCol,endIndex,endCol)        
        self.result = minimize(self.problem, self.algorithm, ("n_gen",200),
                               verbose = True, seed = 1)
        self.weights = self.result.X.reshape([self.n_var,1])

# fo = fundOptim(r'C:\Users\abhij\naiveFundOptim\Daily_prices\portfolio.xlsx', 'Percent_change')
# fo.optimize(0,0, endIndex=950)