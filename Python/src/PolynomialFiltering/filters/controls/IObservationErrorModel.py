''' PolynomialFiltering.filters.controls.IObservationErrorModel
 (C) Copyright 2019 - Blue Lightning Development, LLC.
 D. F. Linton. support@BlueLightningDevelopment.com

 SPDX-License-Identifier: MIT
 See separate LICENSE file for full text
'''

from abc import ABC, abstractmethod

from numpy import array
from numpy import array as vector;

from PolynomialFiltering.Main import AbstractFilterWithCovariance

class IObservationErrorModel(ABC):
    def __init__(self):
        pass

    @abstractmethod # pragma: no cover
    def getPrecisionMatrix(self, f : AbstractFilterWithCovariance, t : float, y : vector, observationId : int) -> array:
        pass
    
    @abstractmethod # pragma: no cover
    def getCovarianceMatrix(self, f : AbstractFilterWithCovariance, t : float, y : vector, observationId : int) -> array:
        pass

