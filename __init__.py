"""
This file serves as a read me file for this module. Use this class for
optimizing portfolio containing various funds. Note that the assets in
the portfolio can be anything, but this works better for funds. For stocks
it is adivsed to use Black-Litterman approach.

Please note that the excel file that is input to the module should be 
preferrably built using the dataBuilder module. If not, please put the date
column towards the end. The code has been optimized around this particular
setup. The module employs the Modern portfolio theory to optimize the 
weights of the assets in the portfolio. This is a naive optimization because
the expeceted returns of individual asset is taken to be the historical
mean returns of a given time period. This is very naive and performs on
par with S&P500 and OMX30. However, this is still better than blindly
investing "x" amount in each assets.
"""