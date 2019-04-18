'''
Created on Apr 11, 2019

@author: NOOK
'''
import unittest
from numpy import cov
from numpy.linalg import inv
from numpy.random import randn
from numpy.testing import assert_almost_equal
from netCDF4 import Dataset
from TestUtilities import *
from TestSuite import testDataPath;
from polynomialfiltering.filters.controls.ConstantObservationErrorModel import ConstantObservationErrorModel
from polynomialfiltering.PythonUtilities import ignore, testcase
from TestData import TestData
from polynomialfiltering.PythonUtilities import assert_not_empty

class TestConstantObservationErrorModel(unittest.TestCase):
    '''@cdf : Dataset'''
    cdf = None;

    @classmethod
    def setUpClass(self):
        pass
    
    @classmethod
    def tearDownClass(self):
        pass
    
    def setUp(self):
        pass


    def tearDown(self):
        pass

    def test0Generate(self) -> None:
        path = testDataPath('testConstantObservationErrorModel.nc');
        print("Writing to: ", path)
        cdf = Dataset(path, "w", format="NETCDF4");
        
        iTest = 0;
        for e in [-1, 0] :
            group = createTestGroup(cdf, 'testScalar_%d' % iTest );
            iTest += 1;
            
            inputCovariance = randn(1,1);
            inputInverse = array([[1.0/inputCovariance[0,0]]]);
            
            element = array([e]);
            writeTestVariable(group, "element", element)
            writeTestVariable(group, 'inputCovariance', inputCovariance);
            writeTestVariable(group, 'inputInverse', inputInverse);
            
            x = inputCovariance[0,0];
            y = inputInverse[0,0];
            iE = int(element[0]);
            model = ConstantObservationErrorModel(x);
            Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
            assert_almost_equal(inputCovariance[0,0], Q)
            Q = model.getPrecisionMatrix(None, 0.0, array([0]), -1);
            assert_almost_equal(inputInverse[0,0], Q)

        iTest = 0;
        for e in [-1, 0] :
            group = createTestGroup(cdf, 'testMatrix_%d' % iTest );
            iTest += 1;
            
            inputCovariance = randn(1,1);
            inputInverse = array([[1.0/inputCovariance[0,0]]]);
            
            element = array([e]);
            writeTestVariable(group, "element", element)
            writeTestVariable(group, 'inputCovariance', inputCovariance);
            writeTestVariable(group, 'inputInverse', inputInverse);
            
            iE = int(element[0]);
            model = ConstantObservationErrorModel(inputCovariance, inputInverse);
            Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
            assert_almost_equal(inputCovariance[0,0], Q)
            Q = model.getPrecisionMatrix(None, 0.0, array([0]), -1);
            assert_almost_equal(inputInverse[0,0], Q)

        iTest = 0;
        for e in [-1, 0, 1, 2] :
            group = createTestGroup(cdf, 'testMatrixMatrix_%d' % iTest );
            iTest += 1;
            
            X = randn(100,3);
            inputCovariance = cov(X, rowvar=False);
            inputInverse = inv(inputCovariance);
            
            element = array([e]);
            writeTestVariable(group, "element", element)
            writeTestVariable(group, 'inputCovariance', inputCovariance);
            writeTestVariable(group, 'inputInverse', inputInverse);
            
            iE = int(element[0]);
            model = ConstantObservationErrorModel(inputCovariance);
            
            if (iE < 0) :
                Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputCovariance, Q)
                Q = model.getPrecisionMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputInverse, Q)
            else :
                Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputCovariance[iE,iE], Q)
                Q = model.getPrecisionMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputInverse[iE,iE], Q)
        cdf.close();

    @testcase
    def test1Scalar(self) -> None: 
        '''@testData : TestData'''
        '''@matches : List[str]'''
        '''@i : int'''
        '''@iE : int'''
        '''@inputCovariance : array'''
        '''@inputInverse : array'''
        '''@element : vector'''
        '''@x : float'''
        '''@Q : array'''
        '''@model : ConstantObservationErrorModel'''
        
        testData = TestData('testConstantObservationErrorModel.nc')
        matches = testData.getMatchingGroups('testScalar_')
        assert_not_empty(matches)
        for i in range(0, len(matches)) :
            element = testData.getGroupVariable(matches[i], 'element')
            inputCovariance = testData.getGroupVariable(matches[i], 'inputCovariance')
            inputInverse = testData.getGroupVariable(matches[i], 'inputInverse')
            iE = int(element[0]);
            x = inputCovariance[0,0]
            model = ConstantObservationErrorModel(x);
            Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
            assert_almost_equal(inputCovariance[0,0], Q)
            Q = model.getPrecisionMatrix(None, 0.0, array([0]), iE);
            assert_almost_equal(inputInverse[0,0], Q)        
        testData.close()

    @testcase
    def test2Matrix(self) -> None:
        '''@testData : TestData'''
        '''@matches : List[str]'''
        '''@i : int'''
        '''@iE : int'''
        '''@inputCovariance : array'''
        '''@inputInverse : array'''
        '''@element : vector'''
        '''@Q : array'''
        '''@model : ConstantObservationErrorModel'''
        
        testData = TestData('testConstantObservationErrorModel.nc')
        matches = testData.getMatchingGroups('testMatrix_')
        assert_not_empty(matches)
        for i in range(0, len(matches)) :
            element = testData.getGroupVariable(matches[i], 'element')
            inputCovariance = testData.getGroupVariable(matches[i], 'inputCovariance')
            inputInverse = testData.getGroupVariable(matches[i], 'inputInverse')
            iE = int(element[0]);
            model = ConstantObservationErrorModel(inputCovariance[0,0]);
            Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
            assert_almost_equal(inputCovariance[0,0], Q)
            Q = model.getPrecisionMatrix(None, 0.0, array([0]), iE);
            assert_almost_equal(inputInverse[0,0], Q)        
        testData.close()

    @testcase
    def test3MatrixMatrix(self) -> None:
        '''@testData : TestData'''
        '''@matches : List[str]'''
        '''@i : int'''
        '''@iE : int'''
        '''@inputCovariance : array'''
        '''@inputInverse : array'''
        '''@element : vector'''
        '''@Q : array'''
        '''@model : ConstantObservationErrorModel'''
        
        testData = TestData('testConstantObservationErrorModel.nc')
        matches = testData.getMatchingGroups('testMatrixMatrix_')
        assert_not_empty(matches)
        for i in range(0, len(matches)) :
            element = testData.getGroupVariable(matches[i], 'element')
            inputCovariance = testData.getGroupVariable(matches[i], 'inputCovariance')
            inputInverse = testData.getGroupVariable(matches[i], 'inputInverse')
            iE = int(element[0]);
            model = ConstantObservationErrorModel(inputCovariance, inputInverse);
            if (iE < 0) :
                Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputCovariance, Q)
                Q = model.getPrecisionMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputInverse, Q)        
            else :
                Q = model.getCovarianceMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputCovariance[iE, iE], Q)
                Q = model.getPrecisionMatrix(None, 0.0, array([0]), iE);
                assert_almost_equal(inputInverse[iE, iE], Q)        
        testData.close()

if __name__ == "__main__": 
    #import sys;sys.argv = ['', 'Test.testConstantObservationErrorModel']
    unittest.main()