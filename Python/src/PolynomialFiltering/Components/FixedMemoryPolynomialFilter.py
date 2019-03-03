'''
Created on Feb 18, 2019

@author: NOOK
'''

from typing import Tuple
from abc import abstractmethod

from numpy import array, copy, diag, ones, zeros, transpose, matrix
from numpy.linalg.linalg import solve, inv
from scipy.special import binom

from PolynomialFiltering.Main import AbstractFilter

class FixedMemoryFilter(AbstractFilter) :
    
    def __init__(self, order : int, memorySize=51 ) -> None:
        super().__init__();  # TODO name
        self.order = order;
        if (order < 0 or order > 5) :
            raise ValueError("Polynomial orders < 1 or > 5 are not supported; order %d" % order)
        self.L = memorySize;
        self.n = 0
        self.n0 = memorySize;
        self.t0 = None;
        self.t = None;
        self.Z = None;
        self.tRing = zeros([memorySize]);
        self.yRing = zeros([memorySize]);
        
    def getN(self)->int:
        return self.n
    
    def getTau(self) -> float:
        return self.tau
    
    def getTime(self) -> array:
        return self.t
    
    def getState(self, t : float) -> array:
        dt = self.tRing - t;
        Tn = self._getTn(dt);
        Tnt = transpose(Tn)
        TntTn = Tnt @ Tn;
        TntYn = Tnt @ self.yRing
        self.Z = solve(TntTn, TntYn);
        return self.Z;
    
    def add(self, t : float, y : array, observationId : str = ''):
        self.t = t;
        self.tRing[ self.n % self.L ] = t;    
        self.yRing[ self.n % self.L ] = y;
        self.n += 1;    

    
    def _getTn(self, dt : array ) -> array:
        Tn = zeros( [dt.shape[0], self.order+1] );
        Tn[:,0] = 1.0;
        C = copy(dt);
        fact = 1.0
        for i in range(1, self.order+1) :
            fact /= i;
            Tn[:,i] = C*fact;
            C *= dt;
        return Tn;



if __name__ == '__main__':
#     dt = -0.1;
#     F = zeros([6,6]);
#     for i in range(0,F.shape[0]) : 
#         for j in range(i,F.shape[1]) :
#             F[i,j] = binom(j,i) * dt**(j-i);
#     print(F);
#     M = zeros([1, F.shape[0]]);
#     M[0,0] = 1;
#     print(M)
#     print( M @ F )
    fixed = FixedMemoryFilter(3, 11);
    dt = zeros([11]);
    for d in range(0, 11) :
        dt[d] = -d * 0.1;
    Tn = fixed._getTn(dt);
    TntYn = transpose(Tn) @ dt;
    TntTn = transpose(Tn) @ Tn;
    print(solve(TntTn, TntYn) )
    print( inv(TntTn) @ TntYn)
    iR = diag(0.1*ones([11]));
    TntiRTn = transpose(Tn) @ iR @ Tn;
    TntiRYn = transpose(Tn) @ iR @ dt;
    print(solve(TntiRTn, TntiRYn) )
    print(inv(TntiRTn)@TntiRYn )
    