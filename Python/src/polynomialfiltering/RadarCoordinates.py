'''
Created on Feb 9, 2019

@author: NOOK
'''

from abc import ABC
from numpy import array, zeros, diag, transpose
from numpy import array as vector
from math import sqrt, sin, cos, atan2, pi

class RadarCoordinates(ABC):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def dAERdENU(self, E : vector, N : vector, U : vector) -> array:
        D =  array([
            [N[0]/(E[0]**2 + N[0]**2), -(E[0]/(E[0]**2 + N[0]**2)), 0],
            [-((E[0]*U[0])/(sqrt(2 + E[0]**2 + N[0])*(2 + E[0]**2 + N[0] + U[0]**2))),-U[0]/(2.*sqrt(2 + E[0]**2 + N[0])*(2 + E[0]**2 + N[0] + U[0]**2)),sqrt(2 + E[0]**2 + N[0])/(2 + E[0]**2 + N[0] + U[0]**2)],
            [E[0]/sqrt(E[0]**2 + N[0]**2 + U[0]**2), N[0]/sqrt(E[0]**2 + N[0]**2 + U[0]**2), U[0]/sqrt(E[0]**2 + N[0]**2 + U[0]**2)]
            ])
        return D
    
    def dENUdAER(self, A : vector, E : vector, R : vector) -> array:
        D = array([
            [R[0]*cos(A[0])*cos(E[0]), -R[0]*sin(A[0])*sin(E[0]), cos(E[0])*sin(A[0])],
            [-R[0]*cos(E[0])*sin(A[0]), -R[0]*cos(A[0])*sin(E[0]),cos(E[0])*cos(A[0])],
            [0, R[0]*cos(E[0]), sin(E[0])]
            ])
        return D
    
    def AER2ENU(self, A, E, R) -> array:
        ENU = zeros([len(A), 3])
        ENU[0, 0] = R[0] * cos(E[0]) * sin(A[0])
        ENU[0, 1] = R[0] * cos(E[0]) * cos(A[0])
        ENU[0, 2] = R[0] * sin(E[0])
        if (len(A) > 1) :
            ENU[1, 0] = self.d1EastdAER1(A, E, R)
            ENU[1, 1] = self.d1NorthdAER1(A, E, R)
            ENU[1, 2] = self.d1UpdAER1(A, E, R)
            if (len(A) > 2) :
                ENU[2, 0] = self.d2EastdAER2(A, E, R)
                ENU[2, 1] = self.d2NorthdAER2(A, E, R)
                ENU[2, 2] = self.d2UpdAER2(A, E, R)
                if (len(A) > 3) :
                    ENU[3, 0] = self.d3EastdAER3(A, E, R)
                    ENU[3, 1] = self.d3NorthdAER3(A, E, R)
                    ENU[3, 2] = self.d3UpdAER3(A, E, R)
                    if (len(A) > 4) :
                        ENU[4, 0] = self.d4EastdAER4(A, E, R)
                        ENU[4, 1] = self.d4NorthdAER4(A, E, R)
                        ENU[4, 2] = self.d4UpdAER4(A, E, R)
                        if (len(A) > 5) :
                            ENU[5, 0] = self.d5EastdAER5(A, E, R)
                            ENU[5, 1] = self.d5NorthdAER5(A, E, R)
                            ENU[5, 2] = self.d5UpdAER5(A, E, R)
        return ENU
    
    def ENU2AER(self, E : vector, N : vector, U : vector) -> array:
        AER = zeros([len(E), 3])
        AER[0, 0] = atan2( E[0], N[0] ) % (2*pi)
        AER[0, 1] = atan2( U[0], sqrt(E[0]**2 + N[0]**2) )
        AER[0, 2] = sqrt(E[0]**2 + N[0]**2 + U[0]**2)
        if (len(E) > 1) :
            AER[1, 0] = self.d1AzimuthdENU1(E, N, U)
            AER[1, 1] = self.d1ElevationdENU1(E, N, U)
            AER[1, 2] = self.d1RangedENU1(E, N, U)
            if (len(E) > 2) :
                AER[2, 0] = self.d2AzimuthdENU2(E, N, U)
                AER[2, 1] = self.d2ElevationdENU2(E, N, U)
                AER[2, 2] = self.d2RangedENU2(E, N, U)
                if (len(E) > 3) :
                    AER[3, 0] = self.d3AzimuthdENU3(E, N, U)
                    AER[3, 1] = self.d3ElevationdENU3(E, N, U)
                    AER[3, 2] = self.d3RangedENU3(E, N, U)
                    if (len(E) > 4) :
                        AER[4, 0] = self.d4AzimuthdENU4(E, N, U)
                        AER[4, 1] = self.d4ElevationdENU4(E, N, U)
                        AER[4, 2] = self.d4RangedENU4(E, N, U)
                        if (len(E) > 5) :
                            AER[5, 0] = self.d5AzimuthdENU5(E, N, U)
                            AER[5, 1] = self.d5ElevationdENU5(E, N, U)
                            AER[5, 2] = self.d5RangedENU5(E, N, U)
        return AER
    
    '''
    public RealMatrix ENU2AER( RealVector E, RealVector N, RealVector U ) {
        RealMatrix AER = new Array2DRowRealMatrix( E.getDimension(), 3 );
        AER.setEntry(0,  0, Math.atan2(N.getEntry(0), E.getEntry(0)));  // azimuth
        AER.setEntry(0,  1, Math.atan2(U.getEntry(0), Math.sqrt(POW(E.getEntry(0),2) + POW(N.getEntry(0),2))));
        AER.setEntry(0,  2, Math.sqrt(POW(E.getEntry(0),2) + POW(N.getEntry(0),2) + POW(U.getEntry(0),2)));
        if (E.getDimension() > 1) {
            AER.setEntry(1, 0, d1AzimuthdENU1(E, N, U));
            AER.setEntry(1, 1, d1ElevationdENU1(E, N, U));
            AER.setEntry(1, 2, d1RangedENU1(E, N, U));
            if (E.getDimension() > 2) {
                AER.setEntry(2, 0, d2AzimuthdENU2(E, N, U));
                AER.setEntry(2, 1, d2ElevationdENU2(E, N, U));
                AER.setEntry(2, 2, d2RangedENU2(E, N, U));
                if (E.getDimension() > 3) {
                    AER.setEntry(3, 0, d3AzimuthdENU3(E, N, U));
                    AER.setEntry(3, 1, d3ElevationdENU3(E, N, U));
                    AER.setEntry(3, 2, d3RangedENU3(E, N, U));
                    if (E.getDimension() > 4) {
                        AER.setEntry(4, 0, d4AzimuthdENU4(E, N, U));
                        AER.setEntry(4, 1, d4ElevationdENU4(E, N, U));
                        AER.setEntry(4, 2, d4RangedENU4(E, N, U));
                        if (E.getDimension() > 5) {
                            AER.setEntry(5, 0, d5AzimuthdENU5(E, N, U));
                            AER.setEntry(5, 1, d5ElevationdENU5(E, N, U));
                            AER.setEntry(5, 2, d5RangedENU5(E, N, U));
                        }
                    }
                }
            }
        }
        return AER;
    }
    
    '''

    def d1AzimuthdENU1(self, E : vector, N : vector, U : vector) -> array:
        return (N[0]*E[1]-E[0]*N[1])/(E[0]**2+N[0]**2);

    def d2AzimuthdENU2(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-2*(N[0]*E[1]-E[0]*N[1])*(E[0]*E[1]+N[0]*N[1])+(E[0]**2+N[0]**2)*(N[0]*E[2]-E[0]*N[2]))/(E[0]**2+N[0]**2)**2;

    def d3AzimuthdENU3(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return ((6*E[0]**2*N[0]-2*N[0]**3)*E[1]**3-6*E[0]*(E[0]**2-3*N[0]**2)*E[1]**2*N[1]+2*(E[0]**3-3*E[0]*N[0]**2)*N[1]**3+3*N[1]*((E[0]**4-N[0]**4)*E[2]+2*E[0]*N[0]*(E[0]**2+N[0]**2)*N[2])+3*E[1]*(2*N[0]*(-3*E[0]**2+N[0]**2)*N[1]**2-2*E[0]*N[0]*(E[0]**2+N[0]**2)*E[2]+(E[0]**4-N[0]**4)*N[2])-(E[0]**2+N[0]**2)**2*(-(N[0]*E[3])+E[0]*N[3]))/(E[0]**2+N[0]**2)**3;

    def d4AzimuthdENU4(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (24*E[0]*N[0]*(-E[0]**2+N[0]**2)*E[1]**4+24*(E[0]**4-6*E[0]**2*N[0]**2+N[0]**4)*E[1]**3*N[1]+24*E[0]*N[0]*(-E[0]**2+N[0]**2)*N[1]**4+12*(E[0]**2+N[0]**2)*N[1]**2*((-3*E[0]**2*N[0]+N[0]**3)*E[2]+E[0]*(E[0]**2-3*N[0]**2)*N[2])-12*E[1]**2*(12*E[0]*N[0]*(-E[0]**2+N[0]**2)*N[1]**2+(E[0]**2+N[0]**2)*((-3*E[0]**2*N[0]+N[0]**3)*E[2]+E[0]*(E[0]**2-3*N[0]**2)*N[2]))+4*(E[0]**2+N[0]**2)**2*N[1]*((E[0]-N[0])*(E[0]+N[0])*E[3]+2*E[0]*N[0]*N[3])+4*E[1]*(-6*(E[0]**4-6*E[0]**2*N[0]**2+N[0]**4)*N[1]**3-6*(E[0]**2+N[0]**2)*N[1]*((E[0]**3-3*E[0]*N[0]**2)*E[2]-N[0]*(-3*E[0]**2+N[0]**2)*N[2])+(E[0]**2+N[0]**2)**2*(-2*E[0]*N[0]*E[3]+(E[0]-N[0])*(E[0]+N[0])*N[3]))-(E[0]**2+N[0]**2)**2*(6*E[0]*N[0]*E[2]**2+6*(-E[0]**2+N[0]**2)*E[2]*N[2]-6*E[0]*N[0]*N[2]**2+(E[0]**2+N[0]**2)*(-(N[0]*E[4])+E[0]*N[4])))/(E[0]**2+N[0]**2)**4;
 
    def d5AzimuthdENU5(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (24*(5*E[0]**4*N[0]-10*E[0]**2*N[0]**3+N[0]**5)*E[1]**5-120*E[0]*(E[0]**4-10*E[0]**2*N[0]**2+5*N[0]**4)*E[1]**4*N[1]-24*(E[0]**5-10*E[0]**3*N[0]**2+5*E[0]*N[0]**4)*N[1]**5-60*(E[0]**2+N[0]**2)*N[1]**3*((E[0]**4-6*E[0]**2*N[0]**2+N[0]**4)*E[2]+4*E[0]*(E[0]-N[0])*N[0]*(E[0]+N[0])*N[2])+60*E[1]**3*(-4*(5*E[0]**4*N[0]-10*E[0]**2*N[0]**3+N[0]**5)*N[1]**2+4*E[0]*N[0]*(-E[0]**4+N[0]**4)*E[2]+(E[0]**6-5*E[0]**4*N[0]**2-5*E[0]**2*N[0]**4+N[0]**6)*N[2])+20*(E[0]**2+N[0]**2)**2*N[1]**2*((-3*E[0]**2*N[0]+N[0]**3)*E[3]+E[0]*(E[0]**2-3*N[0]**2)*N[3])-20*E[1]**2*(-12*(E[0]**5-10*E[0]**3*N[0]**2+5*E[0]*N[0]**4)*N[1]**3-9*(E[0]**2+N[0]**2)*N[1]*((E[0]**4-6*E[0]**2*N[0]**2+N[0]**4)*E[2]+4*E[0]*(E[0]-N[0])*N[0]*(E[0]+N[0])*N[2])+(E[0]**2+N[0]**2)**2*((-3*E[0]**2*N[0]+N[0]**3)*E[3]+E[0]*(E[0]**2-3*N[0]**2)*N[3]))+5*(E[0]**2+N[0]**2)**2*N[1]*(-6*(E[0]**3-3*E[0]*N[0]**2)*E[2]**2+12*N[0]*(-3*E[0]**2+N[0]**2)*E[2]*N[2]+6*(E[0]**3-3*E[0]*N[0]**2)*N[2]**2+(E[0]**4-N[0]**4)*E[4]+2*E[0]*N[0]*(E[0]**2+N[0]**2)*N[4])+5*E[1]*(24*(5*E[0]**4*N[0]-10*E[0]**2*N[0]**3+N[0]**5)*N[1]**4-36*(E[0]**2+N[0]**2)*N[1]**2*(4*E[0]*N[0]*(-E[0]**2+N[0]**2)*E[2]+(E[0]**4-6*E[0]**2*N[0]**2+N[0]**4)*N[2])-8*(E[0]**2+N[0]**2)**2*N[1]*((E[0]**3-3*E[0]*N[0]**2)*E[3]-N[0]*(-3*E[0]**2+N[0]**2)*N[3])+(E[0]**2+N[0]**2)**2*(-6*N[0]*(-3*E[0]**2+N[0]**2)*E[2]**2-12*E[0]*(E[0]**2-3*N[0]**2)*E[2]*N[2]+6*N[0]*(-3*E[0]**2+N[0]**2)*N[2]**2-2*E[0]*N[0]*(E[0]**2+N[0]**2)*E[4]+(E[0]**4-N[0]**4)*N[4]))-(E[0]**2+N[0]**2)**3*(-10*N[2]*((E[0]-N[0])*(E[0]+N[0])*E[3]+2*E[0]*N[0]*N[3])+10*E[2]*(2*E[0]*N[0]*E[3]+(-E[0]**2+N[0]**2)*N[3])+(E[0]**2+N[0]**2)*(-(N[0]*E[5])+E[0]*N[5])))/(E[0]**2+N[0]**2)**5;

    def d1ElevationdENU1(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-(U[0]*(E[0]*E[1]+N[0]*N[1]))+S*U[1])/(sqrt(S)*(S+U[0]**2));

    def d2ElevationdENU2(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-2*(S+U[0]**2)*(E[0]*E[1]+N[0]*N[1])*(-(U[0]*(E[0]*E[1]+N[0]*N[1]))+S*U[1])-4*S*(-(U[0]*(E[0]*E[1]+N[0]*N[1]))+S*U[1])*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])+2*S*(S+U[0]**2)*(-(U[0]*E[1]**2)-U[0]*N[1]**2+E[0]*E[1]*U[1]+N[0]*N[1]*U[1]-U[0]*(E[0]*E[2]+N[0]*N[2])+S*U[2]))/(2.*S**1.5*(S+U[0]**2)**2);

    def d3ElevationdENU3(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-6*(S+U[0]**2)*(E[0]*E[1]+N[0]*N[1])*(-2*(S+U[0]**2)*(E[0]*E[1]+N[0]*N[1])*(-(U[0]*(E[0]*E[1]+N[0]*N[1]))+S*U[1])-4*S*(-(U[0]*(E[0]*E[1]+N[0]*N[1]))+S*U[1])*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])+2*S*(S+U[0]**2)*(-(U[0]*E[1]**2)-U[0]*N[1]**2+E[0]*E[1]*U[1]+N[0]*N[1]*U[1]-U[0]*(E[0]*E[2]+N[0]*N[2])+S*U[2]))-8*S*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-2*(S+U[0]**2)*(E[0]*E[1]+N[0]*N[1])*(-(U[0]*(E[0]*E[1]+N[0]*N[1]))+S*U[1])-4*S*(-(U[0]*(E[0]*E[1]+N[0]*N[1]))+S*U[1])*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])+2*S*(S+U[0]**2)*(-(U[0]*E[1]**2)-U[0]*N[1]**2+E[0]*E[1]*U[1]+N[0]*N[1]*U[1]-U[0]*(E[0]*E[2]+N[0]*N[2])+S*U[2]))+4*S*(S+U[0]**2)*(2*E[0]*(4*E[0]**2+N[0]**2)*U[0]*E[1]**3+2*N[0]*(E[0]**2+4*N[0]**2)*U[0]*N[1]**3-(3*E[0]**4+8*N[0]**4-6*N[0]**2*U[0]**2+E[0]**2*(11*N[0]**2+U[0]**2))*N[1]**2*U[1]-E[1]**2*(-2*N[0]*(10*E[0]**2+N[0]**2)*U[0]*N[1]+(8*E[0]**4+E[0]**2*(11*N[0]**2-6*U[0]**2)+N[0]**2*(3*N[0]**2+U[0]**2))*U[1])+S*N[1]*(-4*N[0]*U[0]*U[1]**2+2*E[0]*N[0]*U[0]*E[2]-U[0]*(3*E[0]**2+N[0]**2+3*U[0]**2)*N[2]+2*N[0]*(2*S+3*U[0]**2)*U[2])+E[1]*(2*E[0]*(E[0]**2+10*N[0]**2)*U[0]*N[1]**2-2*E[0]*N[0]*(5*S-7*U[0]**2)*N[1]*U[1]+S*(-4*E[0]*U[0]*U[1]**2-U[0]*(E[0]**2+3*(N[0]**2+U[0]**2))*E[2]+2*E[0]*N[0]*U[0]*N[2]+2*E[0]*(2*S+3*U[0]**2)*U[2]))+S*(-2*S*U[1]**3+U[1]*(-((3*S+U[0]**2)*(E[0]*E[2]+N[0]*N[2]))-2*S*U[0]*U[2])+(S+U[0]**2)*(-(U[0]*(E[0]*E[3]+N[0]*N[3]))+S*U[3]))))/(4.*S**2.5*(S+U[0]**2)**3);

    def d4ElevationdENU4(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-3*U[0]*(-(S**3*(8*E[0]**4-24*E[0]**2*N[0]**2+3*N[0]**4))+S**2*(8*E[0]**4+36*E[0]**2*N[0]**2-7*N[0]**4)*U[0]**2+S*N[0]**2*(16*E[0]**2-5*N[0]**2)*U[0]**4-N[0]**2*(-4*E[0]**2+N[0]**2)*U[0]**6)*E[1]**4+3*U[0]*(S**3*(3*E[0]**4-24*E[0]**2*N[0]**2+8*N[0]**4)+S**2*(7*E[0]**4-36*E[0]**2*N[0]**2-8*N[0]**4)*U[0]**2+S*E[0]**2*(5*E[0]**2-16*N[0]**2)*U[0]**4+E[0]**2*(E[0]**2-4*N[0]**2)*U[0]**6)*N[1]**4-12*S*N[0]*(-(S**3*(3*E[0]**2-2*N[0]**2))+3*S**2*(E[0]**2-4*N[0]**2)*U[0]**2+S*(7*E[0]**2+2*N[0]**2)*U[0]**4+E[0]**2*U[0]**6)*N[1]**3*U[1]-12*E[0]*E[1]**3*(N[0]*U[0]*(-5*S**3*(4*E[0]**2-3*N[0]**2)-5*S**2*(2*E[0]**2-5*N[0]**2)*U[0]**2+(-8*E[0]**4+5*E[0]**2*N[0]**2+13*N[0]**4)*U[0]**4+(-2*E[0]**2+3*N[0]**2)*U[0]**6)*N[1]+S*(S**3*(2*E[0]**2-3*N[0]**2)-3*S**2*(4*E[0]**2-N[0]**2)*U[0]**2+S*(2*E[0]**2+7*N[0]**2)*U[0]**4+N[0]**2*U[0]**6)*U[1])-6*S*N[1]**2*(-2*S*U[0]*(3*S**2*(E[0]**2-4*N[0]**2)+2*S*(E[0]**2+6*N[0]**2)*U[0]**2-E[0]**2*U[0]**4)*U[1]**2+(S+U[0]**2)*(E[0]*U[0]*(-3*S**2*(E[0]**2-4*N[0]**2)+2*(-2*E[0]**4+E[0]**2*N[0]**2+3*N[0]**4)*U[0]**2-(E[0]**2-2*N[0]**2)*U[0]**4)*E[2]-N[0]*U[0]*(3*S**2*(3*E[0]**2-2*N[0]**2)+2*S*(6*E[0]**2+N[0]**2)*U[0]**2+3*E[0]**2*U[0]**4)*N[2]+S*(E[0]**6-2*N[0]**6+6*N[0]**4*U[0]**2-E[0]**2*(3*N[0]**4-6*N[0]**2*U[0]**2+U[0]**4))*U[2]))+6*E[1]**2*(U[0]*(-3*S**3*(4*E[0]**4-27*E[0]**2*N[0]**2+4*N[0]**4)-3*S**2*(6*E[0]**4-23*E[0]**2*N[0]**2+6*N[0]**4)*U[0]**2-S*(8*E[0]**4-47*E[0]**2*N[0]**2+8*N[0]**4)*U[0]**4+(-2*E[0]**4+11*E[0]**2*N[0]**2-2*N[0]**4)*U[0]**6)*N[1]**2+2*S*N[0]*(-3*S**3*(4*E[0]**2-N[0]**2)+3*S**2*(14*E[0]**2-N[0]**2)*U[0]**2+(8*E[0]**4+E[0]**2*N[0]**2-7*N[0]**4)*U[0]**4+(2*E[0]**2-N[0]**2)*U[0]**6)*N[1]*U[1]+S*(-2*S*U[0]*(3*S**2*(4*E[0]**2-N[0]**2)-2*S*(6*E[0]**2+N[0]**2)*U[0]**2+N[0]**2*U[0]**4)*U[1]**2+(S+U[0]**2)*(E[0]*U[0]*(-3*S**2*(2*E[0]**2-3*N[0]**2)+2*S*(E[0]**2+6*N[0]**2)*U[0]**2+3*N[0]**2*U[0]**4)*E[2]+N[0]*U[0]*(-3*S**2*(4*E[0]**2-N[0]**2)-2*(3*E[0]**4+E[0]**2*N[0]**2-2*N[0]**4)*U[0]**2+(-2*E[0]**2+N[0]**2)*U[0]**4)*N[2]+S*(2*E[0]**6+3*E[0]**4*N[0]**2-N[0]**6-6*S*E[0]**2*U[0]**2+N[0]**2*U[0]**4)*U[2])))-4*S**2*N[1]*(-6*S*N[0]*(S**2-6*S*U[0]**2+U[0]**4)*U[1]**3+3*(S+U[0]**2)*U[1]*(E[0]*N[0]*(-3*S**2+6*S*U[0]**2+U[0]**4)*E[2]+(E[0]**6-2*N[0]**6+6*N[0]**4*U[0]**2-E[0]**2*(3*N[0]**4-6*N[0]**2*U[0]**2+U[0]**4))*N[2]-2*S*N[0]*U[0]*(3*S-U[0]**2)*U[2])+(S+U[0]**2)**2*(-(E[0]*N[0]*U[0]*(3*S+U[0]**2)*E[3])+U[0]*(E[0]**4-2*N[0]**4+E[0]**2*(-N[0]**2+U[0]**2))*N[3]+S*N[0]*(S-U[0]**2)*U[3]))-4*E[1]*(3*E[0]*N[0]*U[0]*(5*S**3*(3*E[0]**2-4*N[0]**2)+5*S**2*(5*E[0]**2-2*N[0]**2)*U[0]**2+S*(13*E[0]**2-8*N[0]**2)*U[0]**4+(3*E[0]**2-2*N[0]**2)*U[0]**6)*N[1]**3-3*S*E[0]*(3*S**3*(E[0]**2-4*N[0]**2)-3*S**2*(E[0]**2-14*N[0]**2)*U[0]**2+(-7*E[0]**4+E[0]**2*N[0]**2+8*N[0]**4)*U[0]**4-(E[0]**2-2*N[0]**2)*U[0]**6)*N[1]**2*U[1]-3*S*N[1]*(-2*S*E[0]*N[0]*U[0]*(15*S**2-10*S*U[0]**2-U[0]**4)*U[1]**2+(S+U[0]**2)*(N[0]*U[0]*(-3*S**2*(4*E[0]**2-N[0]**2)-2*(3*E[0]**4+E[0]**2*N[0]**2-2*N[0]**4)*U[0]**2+(-2*E[0]**2+N[0]**2)*U[0]**4)*E[2]+E[0]*U[0]*(3*S**2*(E[0]**2-4*N[0]**2)+2*S*(2*E[0]**2-3*N[0]**2)*U[0]**2+(E[0]**2-2*N[0]**2)*U[0]**4)*N[2]+S*E[0]*N[0]*(3*S**2-6*S*U[0]**2-U[0]**4)*U[2]))+S**2*(-6*S*E[0]*(S**2-6*S*U[0]**2+U[0]**4)*U[1]**3-3*(S+U[0]**2)*U[1]*((2*E[0]**6+3*E[0]**4*N[0]**2-N[0]**6-6*S*E[0]**2*U[0]**2+N[0]**2*U[0]**4)*E[2]+E[0]*N[0]*(3*S**2-6*S*U[0]**2-U[0]**4)*N[2]+2*S*E[0]*U[0]*(3*S-U[0]**2)*U[2])+(S+U[0]**2)**2*(U[0]*(-2*E[0]**4-E[0]**2*N[0]**2+N[0]**4+N[0]**2*U[0]**2)*E[3]-E[0]*N[0]*U[0]*(3*S+U[0]**2)*N[3]+S*E[0]*(S-U[0]**2)*U[3])))+S**2*(24*S**2*U[0]*(S-U[0]**2)*U[1]**4+12*S*(S+U[0]**2)*U[1]**2*(U[0]*(3*S-U[0]**2)*(E[0]*E[2]+N[0]*N[2])-S*(S-3*U[0]**2)*U[2])+4*S*(S+U[0]**2)**2*U[1]*(-((S-U[0]**2)*(E[0]*E[3]+N[0]*N[3]))-2*S*U[0]*U[3])+(S+U[0]**2)**2*(-3*U[0]*(-2*E[0]**4-E[0]**2*N[0]**2+N[0]**4+N[0]**2*U[0]**2)*E[2]**2-3*U[0]*(E[0]**4-2*N[0]**4+E[0]**2*(-N[0]**2+U[0]**2))*N[2]**2-6*S*N[0]*(S-U[0]**2)*N[2]*U[2]+6*E[0]*E[2]*(N[0]*U[0]*(3*S+U[0]**2)*N[2]-S*(S-U[0]**2)*U[2])+S*(-6*S*U[0]*U[2]**2+(S+U[0]**2)*(-(U[0]*(E[0]*E[4]+N[0]*N[4]))+S*U[4])))))/(S**3.5*(S+U[0]**2)**4);
 
    def d5ElevationdENU5(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-3*E[0]*U[0]*(5*S**4*(8*E[0]**4-40*E[0]**2*N[0]**2+15*N[0]**4)-20*S**3*(4*E[0]**4+15*E[0]**2*N[0]**2-10*N[0]**4)*U[0]**2+2*S**2*(4*E[0]**4-90*E[0]**2*N[0]**2+95*N[0]**4)*U[0]**4+20*S*N[0]**2*(-5*E[0]**2+4*N[0]**2)*U[0]**6+5*N[0]**2*(-4*E[0]**2+3*N[0]**2)*U[0]**8)*E[1]**5-3*N[0]*U[0]*(5*S**4*(15*E[0]**4-40*E[0]**2*N[0]**2+8*N[0]**4)+20*S**3*(10*E[0]**4-15*E[0]**2*N[0]**2-4*N[0]**4)*U[0]**2+2*S**2*(95*E[0]**4-90*E[0]**2*N[0]**2+4*N[0]**4)*U[0]**4+20*S*E[0]**2*(4*E[0]**2-5*N[0]**2)*U[0]**6+5*E[0]**2*(3*E[0]**2-4*N[0]**2)*U[0]**8)*N[1]**5+15*S*(S**4*(3*E[0]**4-24*E[0]**2*N[0]**2+8*N[0]**4)+20*S**3*N[0]**2*(3*E[0]**2-4*N[0]**2)*U[0]**2-10*S**2*(E[0]**4-10*E[0]**2*N[0]**2-4*N[0]**4)*U[0]**4+4*E[0]**2*(-2*E[0]**4+3*E[0]**2*N[0]**2+5*N[0]**4)*U[0]**6-E[0]**2*(E[0]**2-4*N[0]**2)*U[0]**8)*N[1]**4*U[1]+15*E[1]**4*(N[0]*U[0]*(-15*S**4*(8*E[0]**4-12*E[0]**2*N[0]**2+N[0]**4)-20*S**3*(2*E[0]**4-17*E[0]**2*N[0]**2+2*N[0]**4)*U[0]**2-2*S**2*(40*E[0]**4-130*E[0]**2*N[0]**2+19*N[0]**4)*U[0]**4-4*S*(10*E[0]**4-31*E[0]**2*N[0]**2+4*N[0]**4)*U[0]**6+(-8*E[0]**4+24*E[0]**2*N[0]**2-3*N[0]**4)*U[0]**8)*N[1]+S*(S**4*(8*E[0]**4-24*E[0]**2*N[0]**2+3*N[0]**4)-20*S**3*E[0]**2*(4*E[0]**2-3*N[0]**2)*U[0]**2+10*S**2*(4*E[0]**4+10*E[0]**2*N[0]**2-N[0]**4)*U[0]**4+4*S*N[0]**2*(5*E[0]**2-2*N[0]**2)*U[0]**6-N[0]**2*(-4*E[0]**2+N[0]**2)*U[0]**8)*U[1])+30*S*N[1]**3*(2*S*N[0]*U[0]*(-5*S**3*(3*E[0]**2-4*N[0]**2)-5*S**2*(E[0]**2+8*N[0]**2)*U[0]**2+S*(11*E[0]**2+4*N[0]**2)*U[0]**4+E[0]**2*U[0]**6)*U[1]**2+(S+U[0]**2)*(-(E[0]*N[0]*U[0]*(5*S**3*(3*E[0]**2-4*N[0]**2)+5*S**2*(5*E[0]**2-2*N[0]**2)*U[0]**2+S*(13*E[0]**2-8*N[0]**2)*U[0]**4+(3*E[0]**2-2*N[0]**2)*U[0]**6)*E[2])+U[0]*(S**3*(3*E[0]**4-24*E[0]**2*N[0]**2+8*N[0]**4)+S**2*(7*E[0]**4-36*E[0]**2*N[0]**2-8*N[0]**4)*U[0]**2+S*E[0]**2*(5*E[0]**2-16*N[0]**2)*U[0]**4+E[0]**2*(E[0]**2-4*N[0]**2)*U[0]**6)*N[2]-S*N[0]*(-(S**3*(3*E[0]**2-2*N[0]**2))+3*S**2*(E[0]**2-4*N[0]**2)*U[0]**2+S*(7*E[0]**2+2*N[0]**2)*U[0]**4+E[0]**2*U[0]**6)*U[2]))-30*E[1]**3*(E[0]*U[0]*(-5*S**4*(4*E[0]**4-41*E[0]**2*N[0]**2+18*N[0]**4)-10*S**3*(3*E[0]**4-22*E[0]**2*N[0]**2+17*N[0]**4)*U[0]**2-2*S**2*(9*E[0]**4-115*E[0]**2*N[0]**2+65*N[0]**4)*U[0]**4-2*S*(5*E[0]**4-54*E[0]**2*N[0]**2+31*N[0]**4)*U[0]**6+(-2*E[0]**4+21*E[0]**2*N[0]**2-12*N[0]**4)*U[0]**8)*N[1]**2-2*S*E[0]*N[0]*(5*S**4*(4*E[0]**2-3*N[0]**2)-10*S**3*(11*E[0]**2-3*N[0]**2)*U[0]**2-10*S**2*(E[0]**2-6*N[0]**2)*U[0]**4-2*S*(5*E[0]**2-9*N[0]**2)*U[0]**6+(-2*E[0]**2+3*N[0]**2)*U[0]**8)*N[1]*U[1]+S*(-2*S*E[0]*U[0]*(5*S**3*(4*E[0]**2-3*N[0]**2)-5*S**2*(8*E[0]**2+N[0]**2)*U[0]**2+S*(4*E[0]**2+11*N[0]**2)*U[0]**4+N[0]**2*U[0]**6)*U[1]**2+(S+U[0]**2)*(U[0]*(-(S**3*(8*E[0]**4-24*E[0]**2*N[0]**2+3*N[0]**4))+S**2*(8*E[0]**4+36*E[0]**2*N[0]**2-7*N[0]**4)*U[0]**2+S*N[0]**2*(16*E[0]**2-5*N[0]**2)*U[0]**4-N[0]**2*(-4*E[0]**2+N[0]**2)*U[0]**6)*E[2]+E[0]*N[0]*U[0]*(-5*S**3*(4*E[0]**2-3*N[0]**2)-5*S**2*(2*E[0]**2-5*N[0]**2)*U[0]**2+(-8*E[0]**4+5*E[0]**2*N[0]**2+13*N[0]**4)*U[0]**4+(-2*E[0]**2+3*N[0]**2)*U[0]**6)*N[2]+S*E[0]*(S**3*(2*E[0]**2-3*N[0]**2)-3*S**2*(4*E[0]**2-N[0]**2)*U[0]**2+S*(2*E[0]**2+7*N[0]**2)*U[0]**4+N[0]**2*U[0]**6)*U[2])))-10*S**2*N[1]**2*(-6*S*(S**3*(E[0]**2-4*N[0]**2)-5*S**2*(E[0]**2-8*N[0]**2)*U[0]**2-5*S*(E[0]**2+4*N[0]**2)*U[0]**4+E[0]**2*U[0]**6)*U[1]**3-3*(S+U[0]**2)*U[1]*(E[0]*(3*S**3*(E[0]**2-4*N[0]**2)-3*S**2*(E[0]**2-14*N[0]**2)*U[0]**2+(-7*E[0]**4+E[0]**2*N[0]**2+8*N[0]**4)*U[0]**4-(E[0]**2-2*N[0]**2)*U[0]**6)*E[2]-3*N[0]*(-(S**3*(3*E[0]**2-2*N[0]**2))+3*S**2*(E[0]**2-4*N[0]**2)*U[0]**2+S*(7*E[0]**2+2*N[0]**2)*U[0]**4+E[0]**2*U[0]**6)*N[2]+2*S*U[0]*(3*S**2*(E[0]**2-4*N[0]**2)+2*S*(E[0]**2+6*N[0]**2)*U[0]**2-E[0]**2*U[0]**4)*U[2])+(S+U[0]**2)**2*(E[0]*U[0]*(-3*S**2*(E[0]**2-4*N[0]**2)+2*(-2*E[0]**4+E[0]**2*N[0]**2+3*N[0]**4)*U[0]**2-(E[0]**2-2*N[0]**2)*U[0]**4)*E[3]-N[0]*U[0]*(3*S**2*(3*E[0]**2-2*N[0]**2)+2*S*(6*E[0]**2+N[0]**2)*U[0]**2+3*E[0]**2*U[0]**4)*N[3]+S*(E[0]**6-2*N[0]**6+6*N[0]**4*U[0]**2-E[0]**2*(3*N[0]**4-6*N[0]**2*U[0]**2+U[0]**4))*U[3]))+10*E[1]**2*(3*N[0]*U[0]*(5*S**4*(18*E[0]**4-41*E[0]**2*N[0]**2+4*N[0]**4)+10*S**3*(17*E[0]**4-22*E[0]**2*N[0]**2+3*N[0]**4)*U[0]**2+2*S**2*(65*E[0]**4-115*E[0]**2*N[0]**2+9*N[0]**4)*U[0]**4+2*S*(31*E[0]**4-54*E[0]**2*N[0]**2+5*N[0]**4)*U[0]**6+(12*E[0]**4-21*E[0]**2*N[0]**2+2*N[0]**4)*U[0]**8)*N[1]**3-3*S*(3*S**4*(4*E[0]**4-27*E[0]**2*N[0]**2+4*N[0]**4)-30*S**3*(E[0]**4-12*E[0]**2*N[0]**2+N[0]**4)*U[0]**2-10*S**2*(5*E[0]**4-11*E[0]**2*N[0]**2+5*N[0]**4)*U[0]**4-2*S*(5*E[0]**4-32*E[0]**2*N[0]**2+5*N[0]**4)*U[0]**6+(-2*E[0]**4+11*E[0]**2*N[0]**2-2*N[0]**4)*U[0]**8)*N[1]**2*U[1]-3*S*N[1]*(-2*S*N[0]*U[0]*(15*S**3*(6*E[0]**2-N[0]**2)-5*S**2*(22*E[0]**2+N[0]**2)*U[0]**2+(-10*E[0]**4+E[0]**2*N[0]**2+11*N[0]**4)*U[0]**4+(-2*E[0]**2+N[0]**2)*U[0]**6)*U[1]**2+(S+U[0]**2)*(3*E[0]*N[0]*U[0]*(-5*S**3*(4*E[0]**2-3*N[0]**2)-5*S**2*(2*E[0]**2-5*N[0]**2)*U[0]**2+(-8*E[0]**4+5*E[0]**2*N[0]**2+13*N[0]**4)*U[0]**4+(-2*E[0]**2+3*N[0]**2)*U[0]**6)*E[2]+U[0]*(3*S**3*(4*E[0]**4-27*E[0]**2*N[0]**2+4*N[0]**4)+3*S**2*(6*E[0]**4-23*E[0]**2*N[0]**2+6*N[0]**4)*U[0]**2+S*(8*E[0]**4-47*E[0]**2*N[0]**2+8*N[0]**4)*U[0]**4+(2*E[0]**4-11*E[0]**2*N[0]**2+2*N[0]**4)*U[0]**6)*N[2]+S*N[0]*(3*S**3*(4*E[0]**2-N[0]**2)-3*S**2*(14*E[0]**2-N[0]**2)*U[0]**2-(8*E[0]**4+E[0]**2*N[0]**2-7*N[0]**4)*U[0]**4+(-2*E[0]**2+N[0]**2)*U[0]**6)*U[2]))+S**2*(-6*S*(S**3*(4*E[0]**2-N[0]**2)-5*S**2*(8*E[0]**2-N[0]**2)*U[0]**2+5*S*(4*E[0]**2+N[0]**2)*U[0]**4-N[0]**2*U[0]**6)*U[1]**3-3*(S+U[0]**2)*U[1]*(3*E[0]*(S**3*(2*E[0]**2-3*N[0]**2)-3*S**2*(4*E[0]**2-N[0]**2)*U[0]**2+S*(2*E[0]**2+7*N[0]**2)*U[0]**4+N[0]**2*U[0]**6)*E[2]+N[0]*(3*S**3*(4*E[0]**2-N[0]**2)-3*S**2*(14*E[0]**2-N[0]**2)*U[0]**2-(8*E[0]**4+E[0]**2*N[0]**2-7*N[0]**4)*U[0]**4+(-2*E[0]**2+N[0]**2)*U[0]**6)*N[2]+2*S*U[0]*(3*S**2*(4*E[0]**2-N[0]**2)-2*S*(6*E[0]**2+N[0]**2)*U[0]**2+N[0]**2*U[0]**4)*U[2])+(S+U[0]**2)**2*(E[0]*U[0]*(-3*S**2*(2*E[0]**2-3*N[0]**2)+2*S*(E[0]**2+6*N[0]**2)*U[0]**2+3*N[0]**2*U[0]**4)*E[3]+N[0]*U[0]*(-3*S**2*(4*E[0]**2-N[0]**2)-2*(3*E[0]**4+E[0]**2*N[0]**2-2*N[0]**4)*U[0]**2+(-2*E[0]**2+N[0]**2)*U[0]**4)*N[3]+S*(2*E[0]**6+3*E[0]**4*N[0]**2-N[0]**6-6*S*E[0]**2*U[0]**2+N[0]**2*U[0]**4)*U[3])))-5*S**2*N[1]*(24*S**2*N[0]*U[0]*(5*S**2-10*S*U[0]**2+U[0]**4)*U[1]**4-12*S*(S+U[0]**2)*U[1]**2*(E[0]*N[0]*U[0]*(-15*S**2+10*S*U[0]**2+U[0]**4)*E[2]+U[0]*(3*S**2*(E[0]**2-4*N[0]**2)+2*S*(E[0]**2+6*N[0]**2)*U[0]**2-E[0]**2*U[0]**4)*N[2]+3*S*N[0]*(S**2-6*S*U[0]**2+U[0]**4)*U[2])+4*S*(S+U[0]**2)**2*U[1]*(E[0]*N[0]*(-3*S**2+6*S*U[0]**2+U[0]**4)*E[3]+(E[0]**6-2*N[0]**6+6*N[0]**4*U[0]**2-E[0]**2*(3*N[0]**4-6*N[0]**2*U[0]**2+U[0]**4))*N[3]-2*S*N[0]*U[0]*(3*S-U[0]**2)*U[3])+(S+U[0]**2)**2*(3*N[0]*U[0]*(3*S**2*(4*E[0]**2-N[0]**2)+2*(3*E[0]**4+E[0]**2*N[0]**2-2*N[0]**4)*U[0]**2+(2*E[0]**2-N[0]**2)*U[0]**4)*E[2]**2-3*N[0]*U[0]*(3*S**2*(3*E[0]**2-2*N[0]**2)+2*S*(6*E[0]**2+N[0]**2)*U[0]**2+3*E[0]**2*U[0]**4)*N[2]**2+6*S*(E[0]**6-2*N[0]**6+6*N[0]**4*U[0]**2-E[0]**2*(3*N[0]**4-6*N[0]**2*U[0]**2+U[0]**4))*N[2]*U[2]+6*E[2]*(E[0]*U[0]*(-3*S**2*(E[0]**2-4*N[0]**2)+2*(-2*E[0]**4+E[0]**2*N[0]**2+3*N[0]**4)*U[0]**2-(E[0]**2-2*N[0]**2)*U[0]**4)*N[2]-S*E[0]*N[0]*(3*S**2-6*S*U[0]**2-U[0]**4)*U[2])+S*(-6*S*N[0]*U[0]*(3*S-U[0]**2)*U[2]**2+U[0]*(S+U[0]**2)*(-(E[0]*N[0]*(3*S+U[0]**2)*E[4])+(E[0]**4-2*N[0]**4+E[0]**2*(-N[0]**2+U[0]**2))*N[4])+S*N[0]*(S**2-U[0]**4)*U[4])))-5*E[1]*(3*E[0]*U[0]*(15*S**4*(E[0]**4-12*E[0]**2*N[0]**2+8*N[0]**4)+20*S**3*(2*E[0]**4-17*E[0]**2*N[0]**2+2*N[0]**4)*U[0]**2+2*S**2*(19*E[0]**4-130*E[0]**2*N[0]**2+40*N[0]**4)*U[0]**4+4*S*(4*E[0]**4-31*E[0]**2*N[0]**2+10*N[0]**4)*U[0]**6+(3*E[0]**4-24*E[0]**2*N[0]**2+8*N[0]**4)*U[0]**8)*N[1]**4+12*S*E[0]*N[0]*(5*S**4*(3*E[0]**2-4*N[0]**2)-10*S**3*(3*E[0]**2-11*N[0]**2)*U[0]**2-10*S**2*(6*E[0]**2-N[0]**2)*U[0]**4-2*S*(9*E[0]**2-5*N[0]**2)*U[0]**6+(-3*E[0]**2+2*N[0]**2)*U[0]**8)*N[1]**3*U[1]-6*S*N[1]**2*(-2*S*E[0]*U[0]*(15*S**3*(E[0]**2-6*N[0]**2)+5*S**2*(E[0]**2+22*N[0]**2)*U[0]**2-(11*E[0]**4+E[0]**2*N[0]**2-10*N[0]**4)*U[0]**4-(E[0]**2-2*N[0]**2)*U[0]**6)*U[1]**2+(S+U[0]**2)*(U[0]*(-3*S**3*(4*E[0]**4-27*E[0]**2*N[0]**2+4*N[0]**4)-3*S**2*(6*E[0]**4-23*E[0]**2*N[0]**2+6*N[0]**4)*U[0]**2-S*(8*E[0]**4-47*E[0]**2*N[0]**2+8*N[0]**4)*U[0]**4+(-2*E[0]**4+11*E[0]**2*N[0]**2-2*N[0]**4)*U[0]**6)*E[2]-3*E[0]*N[0]*U[0]*(5*S**3*(3*E[0]**2-4*N[0]**2)+5*S**2*(5*E[0]**2-2*N[0]**2)*U[0]**2+S*(13*E[0]**2-8*N[0]**2)*U[0]**4+(3*E[0]**2-2*N[0]**2)*U[0]**6)*N[2]+S*E[0]*(3*S**3*(E[0]**2-4*N[0]**2)-3*S**2*(E[0]**2-14*N[0]**2)*U[0]**2+(-7*E[0]**4+E[0]**2*N[0]**2+8*N[0]**4)*U[0]**4-(E[0]**2-2*N[0]**2)*U[0]**6)*U[2]))-4*S**2*N[1]*(-6*S*E[0]*N[0]*(5*S**3-45*S**2*U[0]**2+15*S*U[0]**4+U[0]**6)*U[1]**3+3*(S+U[0]**2)*U[1]*(N[0]*(-3*S**3*(4*E[0]**2-N[0]**2)+3*S**2*(14*E[0]**2-N[0]**2)*U[0]**2+(8*E[0]**4+E[0]**2*N[0]**2-7*N[0]**4)*U[0]**4+(2*E[0]**2-N[0]**2)*U[0]**6)*E[2]+E[0]*(3*S**3*(E[0]**2-4*N[0]**2)-3*S**2*(E[0]**2-14*N[0]**2)*U[0]**2+(-7*E[0]**4+E[0]**2*N[0]**2+8*N[0]**4)*U[0]**4-(E[0]**2-2*N[0]**2)*U[0]**6)*N[2]-2*S*E[0]*N[0]*U[0]*(15*S**2-10*S*U[0]**2-U[0]**4)*U[2])+(S+U[0]**2)**2*(N[0]*U[0]*(-3*S**2*(4*E[0]**2-N[0]**2)-2*(3*E[0]**4+E[0]**2*N[0]**2-2*N[0]**4)*U[0]**2+(-2*E[0]**2+N[0]**2)*U[0]**4)*E[3]+E[0]*U[0]*(3*S**2*(E[0]**2-4*N[0]**2)+2*S*(2*E[0]**2-3*N[0]**2)*U[0]**2+(E[0]**2-2*N[0]**2)*U[0]**4)*N[3]+S*E[0]*N[0]*(3*S**2-6*S*U[0]**2-U[0]**4)*U[3]))+S**2*(24*S**2*E[0]*U[0]*(5*S**2-10*S*U[0]**2+U[0]**4)*U[1]**4-12*S*(S+U[0]**2)*U[1]**2*(U[0]*(-3*S**2*(4*E[0]**2-N[0]**2)+2*S*(6*E[0]**2+N[0]**2)*U[0]**2-N[0]**2*U[0]**4)*E[2]+E[0]*N[0]*U[0]*(-15*S**2+10*S*U[0]**2+U[0]**4)*N[2]+3*S*E[0]*(S**2-6*S*U[0]**2+U[0]**4)*U[2])-4*S*(S+U[0]**2)**2*U[1]*((2*E[0]**6+3*E[0]**4*N[0]**2-N[0]**6-6*S*E[0]**2*U[0]**2+N[0]**2*U[0]**4)*E[3]+E[0]*N[0]*(3*S**2-6*S*U[0]**2-U[0]**4)*N[3]+2*S*E[0]*U[0]*(3*S-U[0]**2)*U[3])+(S+U[0]**2)**2*(3*E[0]*U[0]*(3*S**2*(2*E[0]**2-3*N[0]**2)-2*S*(E[0]**2+6*N[0]**2)*U[0]**2-3*N[0]**2*U[0]**4)*E[2]**2+3*E[0]*U[0]*(-3*S**2*(E[0]**2-4*N[0]**2)+2*(-2*E[0]**4+E[0]**2*N[0]**2+3*N[0]**4)*U[0]**2-(E[0]**2-2*N[0]**2)*U[0]**4)*N[2]**2-6*S*E[0]*N[0]*(3*S**2-6*S*U[0]**2-U[0]**4)*N[2]*U[2]+6*E[2]*(N[0]*U[0]*(3*S**2*(4*E[0]**2-N[0]**2)+2*(3*E[0]**4+E[0]**2*N[0]**2-2*N[0]**4)*U[0]**2+(2*E[0]**2-N[0]**2)*U[0]**4)*N[2]-S*(2*E[0]**6+3*E[0]**4*N[0]**2-N[0]**6-6*S*E[0]**2*U[0]**2+N[0]**2*U[0]**4)*U[2])+S*(-6*S*E[0]*U[0]*(3*S-U[0]**2)*U[2]**2-U[0]*(S+U[0]**2)*((2*E[0]**4+E[0]**2*N[0]**2-N[0]**2*(N[0]**2+U[0]**2))*E[4]+E[0]*N[0]*(3*S+U[0]**2)*N[4])+S*E[0]*(S**2-U[0]**4)*U[4]))))+S**3*(24*S**2*(S**2-10*S*U[0]**2+5*U[0]**4)*U[1]**5+60*S*(S+U[0]**2)*U[1]**3*((S**2-6*S*U[0]**2+U[0]**4)*(E[0]*E[2]+N[0]*N[2])+4*S*U[0]*(S-U[0]**2)*U[2])+20*S*(S+U[0]**2)**2*U[1]**2*(U[0]*(3*S-U[0]**2)*(E[0]*E[3]+N[0]*N[3])-S*(S-3*U[0]**2)*U[3])-5*(S+U[0]**2)**2*U[1]*(3*(-2*E[0]**6+N[0]**6+6*E[0]**2*N[0]**2*U[0]**2-N[0]**2*U[0]**4-3*E[0]**4*(N[0]**2-2*U[0]**2))*E[2]**2+3*(E[0]**6-2*N[0]**6+6*N[0]**4*U[0]**2-E[0]**2*(3*N[0]**4-6*N[0]**2*U[0]**2+U[0]**4))*N[2]**2-12*S*N[0]*U[0]*(3*S-U[0]**2)*N[2]*U[2]+6*E[0]*E[2]*(N[0]*(-3*S**2+6*S*U[0]**2+U[0]**4)*N[2]+2*S*U[0]*(-3*S+U[0]**2)*U[2])+S*(6*S*(S-3*U[0]**2)*U[2]**2+(S**2-U[0]**4)*(E[0]*E[4]+N[0]*N[4])+2*S*U[0]*(S+U[0]**2)*U[4]))+(S+U[0]**2)**3*(10*E[2]*(-(U[0]*(-2*E[0]**4-E[0]**2*N[0]**2+N[0]**4+N[0]**2*U[0]**2)*E[3])+E[0]*N[0]*U[0]*(3*S+U[0]**2)*N[3]-S*E[0]*(S-U[0]**2)*U[3])+10*N[2]*(E[0]*N[0]*U[0]*(3*S+U[0]**2)*E[3]-U[0]*(E[0]**4-2*N[0]**4+E[0]**2*(-N[0]**2+U[0]**2))*N[3]-S*N[0]*(S-U[0]**2)*U[3])+S*(10*U[2]*(-((S-U[0]**2)*(E[0]*E[3]+N[0]*N[3]))-2*S*U[0]*U[3])+(S+U[0]**2)*(-(U[0]*(E[0]*E[5]+N[0]*N[5]))+S*U[5])))))/(S**4.5*(S+U[0]**2)**5);

    def d1RangedENU1(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (E[0]*E[1]+N[0]*N[1]+U[0]*U[1])/sqrt(E[0]**2+N[0]**2+U[0]**2);

    def d2RangedENU2(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))/(2.*(E[0]**2+N[0]**2+U[0]**2)**1.5);

    def d3RangedENU3(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-6*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))+4*(E[0]**2+N[0]**2+U[0]**2)**2*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3]))/(4.*(E[0]**2+N[0]**2+U[0]**2)**2.5);

    def d4RangedENU4(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-10*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-6*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))+4*(E[0]**2+N[0]**2+U[0]**2)**2*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3]))+2*(E[0]**2+N[0]**2+U[0]**2)*(-6*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2])*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))+4*(E[0]**2+N[0]**2+U[0]**2)*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3])+4*(E[0]**2+N[0]**2+U[0]**2)**2*(3*E[2]**2+3*N[2]**2+3*U[2]**2+4*E[1]*E[3]+4*N[1]*N[3]+4*U[1]*U[3]+E[0]*E[4]+N[0]*N[4]+U[0]*U[4])))/(8.*(E[0]**2+N[0]**2+U[0]**2)**3.5);

    def d5RangedENU5(self, E : vector, N : vector, U : vector) -> array:
        '''@S : float'''
        S = E[0]**2 + N[0]**2
        return (-14*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-10*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-6*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))+4*(E[0]**2+N[0]**2+U[0]**2)**2*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3]))+2*(E[0]**2+N[0]**2+U[0]**2)*(-6*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2])*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))+4*(E[0]**2+N[0]**2+U[0]**2)*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3])+4*(E[0]**2+N[0]**2+U[0]**2)**2*(3*E[2]**2+3*N[2]**2+3*U[2]**2+4*E[1]*E[3]+4*N[1]*N[3]+4*U[1]*U[3]+E[0]*E[4]+N[0]*N[4]+U[0]*U[4])))+4*(E[0]**2+N[0]**2+U[0]**2)*(-5*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2])*(-6*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))+4*(E[0]**2+N[0]**2+U[0]**2)**2*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3]))-3*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(-6*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2])*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))+4*(E[0]**2+N[0]**2+U[0]**2)*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3])+4*(E[0]**2+N[0]**2+U[0]**2)**2*(3*E[2]**2+3*N[2]**2+3*U[2]**2+4*E[1]*E[3]+4*N[1]*N[3]+4*U[1]*U[3]+E[0]*E[4]+N[0]*N[4]+U[0]*U[4]))+(E[0]**2+N[0]**2+U[0]**2)*(8*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3])-8*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2])*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3])-6*(-2*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])**2+2*(E[0]**2+N[0]**2+U[0]**2)*(E[1]**2+N[1]**2+U[1]**2+E[0]*E[2]+N[0]*N[2]+U[0]*U[2]))*(3*E[1]*E[2]+3*N[1]*N[2]+3*U[1]*U[2]+E[0]*E[3]+N[0]*N[3]+U[0]*U[3])+20*(E[0]**2+N[0]**2+U[0]**2)*(E[0]*E[1]+N[0]*N[1]+U[0]*U[1])*(3*E[2]**2+3*N[2]**2+3*U[2]**2+4*E[1]*E[3]+4*N[1]*N[3]+4*U[1]*U[3]+E[0]*E[4]+N[0]*N[4]+U[0]*U[4])+4*(E[0]**2+N[0]**2+U[0]**2)**2*(10*E[2]*E[3]+10*N[2]*N[3]+10*U[2]*U[3]+5*E[1]*E[4]+5*N[1]*N[4]+5*U[1]*U[4]+E[0]*E[5]+N[0]*N[5]+U[0]*U[5]))))/(16.*(E[0]**2+N[0]**2+U[0]**2)**4.5);


    def d1EastdAER1(self, A : vector, E : vector, R : vector) -> array:
        return R[0]*cos(A[0])*cos(E[0])*A[1]+sin(A[0])*(cos(E[0])*R[1]-R[0]*E[1]*sin(E[0]));

    def d2EastdAER2(self, A : vector, E : vector, R : vector) -> array:
        return -(sin(A[0])*(cos(E[0])*(R[0]*(A[1]**2+E[1]**2)-R[2])+(2*E[1]*R[1]+R[0]*E[2])*sin(E[0])))+cos(A[0])*(R[0]*cos(E[0])*A[2]+2*A[1]*(cos(E[0])*R[1]-R[0]*E[1]*sin(E[0])));

    def d3EastdAER3(self, A : vector, E : vector, R : vector) -> array:
        return cos(E[0])*(cos(A[0])*(-(R[0]*A[1]**3)+3*R[1]*A[2]+3*A[1]*(-(R[0]*E[1]**2)+R[2])+R[0]*A[3])+(-3*(A[1]**2*R[1]+R[0]*A[1]*A[2]+E[1]*(E[1]*R[1]+R[0]*E[2]))+R[3])*sin(A[0]))-(3*cos(A[0])*(R[0]*E[1]*A[2]+A[1]*(2*E[1]*R[1]+R[0]*E[2]))+(-3*R[0]*A[1]**2*E[1]-R[0]*E[1]**3+3*R[1]*E[2]+3*E[1]*R[2]+R[0]*E[3])*sin(A[0]))*sin(E[0]);

    def d4EastdAER4(self, A : vector, E : vector, R : vector) -> array:
        return R[0]*cos(E[0])*A[1]**4*sin(A[0])+cos(E[0])*(cos(A[0])*(-6*R[0]*E[1]**2*A[2]+6*A[2]*R[2]+4*R[1]*A[3]+R[0]*A[4])+(R[0]*E[1]**4-3*R[0]*(A[2]**2+E[2]**2)-6*E[1]**2*R[2]-4*E[1]*(3*R[1]*E[2]+R[0]*E[3])+R[4])*sin(A[0]))-(6*cos(A[0])*A[2]*(2*E[1]*R[1]+R[0]*E[2])+4*R[0]*cos(A[0])*E[1]*A[3]+(-4*E[1]**3*R[1]-6*R[0]*E[1]**2*E[2]+6*E[2]*R[2]+4*R[1]*E[3]+4*E[1]*R[3]+R[0]*E[4])*sin(A[0]))*sin(E[0])+4*cos(A[0])*A[1]**3*(-(cos(E[0])*R[1])+R[0]*E[1]*sin(E[0]))+6*A[1]**2*(-(cos(E[0])*(R[0]*cos(A[0])*A[2]+(-(R[0]*E[1]**2)+R[2])*sin(A[0])))+(2*E[1]*R[1]+R[0]*E[2])*sin(A[0])*sin(E[0]))+4*A[1]*(-(cos(E[0])*(cos(A[0])*(3*E[1]*(E[1]*R[1]+R[0]*E[2])-R[3])+(3*R[1]*A[2]+R[0]*A[3])*sin(A[0])))+(cos(A[0])*(R[0]*E[1]**3-3*R[1]*E[2]-3*E[1]*R[2]-R[0]*E[3])+3*R[0]*E[1]*A[2]*sin(A[0]))*sin(E[0]));

    def d5EastdAER5(self, A : vector, E : vector, R : vector) -> array:
        return R[0]*cos(A[0])*cos(E[0])*A[1]**5+cos(E[0])*(cos(A[0])*(-30*R[0]*E[1]*A[2]*E[2]+10*R[2]*A[3]-10*E[1]**2*(3*R[1]*A[2]+R[0]*A[3])+10*A[2]*R[3]+5*R[1]*A[4]+R[0]*A[5])+(5*(E[1]**4*R[1]+2*R[0]*E[1]**3*E[2]-3*R[1]*(A[2]**2+E[2]**2)-2*R[0]*(A[2]*A[3]+E[2]*E[3])-2*E[1]**2*R[3]-E[1]*(6*E[2]*R[2]+4*R[1]*E[3]+R[0]*E[4]))+R[5])*sin(A[0]))-(5*cos(A[0])*(-2*R[0]*E[1]**3*A[2]+2*E[2]*(3*R[1]*A[2]+R[0]*A[3])+2*R[0]*A[2]*E[3]+E[1]*(6*A[2]*R[2]+4*R[1]*A[3]+R[0]*A[4]))+(R[0]*E[1]**5-10*E[1]**3*R[2]+10*R[2]*E[3]-10*E[1]**2*(3*R[1]*E[2]+R[0]*E[3])+10*E[2]*R[3]+5*R[1]*E[4]+5*E[1]*(-3*R[0]*(A[2]**2+E[2]**2)+R[4])+R[0]*E[5])*sin(A[0]))*sin(E[0])+5*A[1]**4*sin(A[0])*(cos(E[0])*R[1]-R[0]*E[1]*sin(E[0]))+10*A[1]**3*(cos(E[0])*(R[0]*cos(A[0])*E[1]**2-cos(A[0])*R[2]+R[0]*A[2]*sin(A[0]))+cos(A[0])*(2*E[1]*R[1]+R[0]*E[2])*sin(E[0]))+5*A[1]*(cos(E[0])*(cos(A[0])*(R[0]*E[1]**4-3*R[0]*(A[2]**2+E[2]**2)-6*E[1]**2*R[2]-4*E[1]*(3*R[1]*E[2]+R[0]*E[3])+R[4])+(6*A[2]*(R[0]*E[1]**2-R[2])-4*R[1]*A[3]-R[0]*A[4])*sin(A[0]))+(cos(A[0])*(4*E[1]**3*R[1]+6*R[0]*E[1]**2*E[2]-6*E[2]*R[2]-4*R[1]*E[3]-4*E[1]*R[3]-R[0]*E[4])+6*A[2]*(2*E[1]*R[1]+R[0]*E[2])*sin(A[0])+4*R[0]*E[1]*A[3]*sin(A[0]))*sin(E[0]))+10*A[1]**2*(cos(E[0])*(-(cos(A[0])*(3*R[1]*A[2]+R[0]*A[3]))+(3*E[1]*(E[1]*R[1]+R[0]*E[2])-R[3])*sin(A[0]))+(-(R[0]*E[1]**3*sin(A[0]))+(3*R[1]*E[2]+R[0]*E[3])*sin(A[0])+3*E[1]*(R[0]*cos(A[0])*A[2]+R[2]*sin(A[0])))*sin(E[0]));

    def d1NorthdAER1(self, A : vector, E : vector, R : vector) -> array:
        return cos(A[0])*cos(E[0])*R[1]-R[0]*(cos(E[0])*A[1]*sin(A[0])+cos(A[0])*E[1]*sin(E[0]));

    def d2NorthdAER2(self, A : vector, E : vector, R : vector) -> array:
        return -(cos(E[0])*(cos(A[0])*(R[0]*(A[1]**2+E[1]**2)-R[2])+(2*A[1]*R[1]+R[0]*A[2])*sin(A[0])))-(R[0]*cos(A[0])*E[2]+2*E[1]*(cos(A[0])*R[1]-R[0]*A[1]*sin(A[0])))*sin(E[0]);

    def d3NorthdAER3(self, A : vector, E : vector, R : vector) -> array:
        return cos(E[0])*(cos(A[0])*(-3*(A[1]**2*R[1]+R[0]*A[1]*A[2]+E[1]*(E[1]*R[1]+R[0]*E[2]))+R[3])+(R[0]*A[1]**3-3*R[1]*A[2]+3*A[1]*(R[0]*E[1]**2-R[2])-R[0]*A[3])*sin(A[0]))+(cos(A[0])*(3*R[0]*A[1]**2*E[1]+R[0]*E[1]**3-3*R[1]*E[2]-3*E[1]*R[2]-R[0]*E[3])+3*(R[0]*E[1]*A[2]+A[1]*(2*E[1]*R[1]+R[0]*E[2]))*sin(A[0]))*sin(E[0]);

    def d4NorthdAER4(self, A : vector, E : vector, R : vector) -> array:
        return cos(E[0])*(cos(A[0])*(R[0]*A[1]**4+R[0]*E[1]**4-3*R[0]*(A[2]**2+E[2]**2)+6*A[1]**2*(R[0]*E[1]**2-R[2])-6*E[1]**2*R[2]-4*A[1]*(3*R[1]*A[2]+R[0]*A[3])-4*E[1]*(3*R[1]*E[2]+R[0]*E[3])+R[4])+(4*A[1]**3*R[1]+6*R[0]*A[1]**2*A[2]+6*A[2]*(R[0]*E[1]**2-R[2])-4*R[1]*A[3]+4*A[1]*(3*E[1]*(E[1]*R[1]+R[0]*E[2])-R[3])-R[0]*A[4])*sin(A[0]))+(cos(A[0])*(4*E[1]**3*R[1]+12*R[0]*A[1]*E[1]*A[2]+6*R[0]*E[1]**2*E[2]+6*A[1]**2*(2*E[1]*R[1]+R[0]*E[2])-6*E[2]*R[2]-4*R[1]*E[3]-4*E[1]*R[3]-R[0]*E[4])+2*(-2*R[0]*A[1]**3*E[1]+3*A[2]*(2*E[1]*R[1]+R[0]*E[2])+2*R[0]*E[1]*A[3]+A[1]*(-2*R[0]*E[1]**3+6*R[1]*E[2]+6*E[1]*R[2]+2*R[0]*E[3]))*sin(A[0]))*sin(E[0]);

    def d5NorthdAER5(self, A : vector, E : vector, R : vector) -> array:
        return -(R[0]*cos(E[0])*A[1]**5*sin(A[0]))+5*cos(A[0])*A[1]**4*(cos(E[0])*R[1]-R[0]*E[1]*sin(E[0]))+sin(A[0])*(cos(E[0])*(30*R[0]*E[1]*A[2]*E[2]+10*E[1]**2*(3*R[1]*A[2]+R[0]*A[3])-5*(2*R[2]*A[3]+2*A[2]*R[3]+R[1]*A[4])-R[0]*A[5])+5*(-2*R[0]*E[1]**3*A[2]+2*E[2]*(3*R[1]*A[2]+R[0]*A[3])+2*R[0]*A[2]*E[3]+E[1]*(6*A[2]*R[2]+4*R[1]*A[3]+R[0]*A[4]))*sin(E[0]))+cos(A[0])*(cos(E[0])*(5*(E[1]**4*R[1]+2*R[0]*E[1]**3*E[2]-3*R[1]*(A[2]**2+E[2]**2)-2*R[0]*(A[2]*A[3]+E[2]*E[3])-2*E[1]**2*R[3]-E[1]*(6*E[2]*R[2]+4*R[1]*E[3]+R[0]*E[4]))+R[5])-(R[0]*E[1]**5-10*E[1]**3*R[2]+10*R[2]*E[3]-10*E[1]**2*(3*R[1]*E[2]+R[0]*E[3])+10*E[2]*R[3]+5*R[1]*E[4]+5*E[1]*(-3*R[0]*(A[2]**2+E[2]**2)+R[4])+R[0]*E[5])*sin(E[0]))+10*A[1]**3*(cos(E[0])*(R[0]*cos(A[0])*A[2]+(-(R[0]*E[1]**2)+R[2])*sin(A[0]))-(2*E[1]*R[1]+R[0]*E[2])*sin(A[0])*sin(E[0]))+5*A[1]*(cos(E[0])*(cos(A[0])*(6*A[2]*(R[0]*E[1]**2-R[2])-4*R[1]*A[3]-R[0]*A[4])+(-(R[0]*E[1]**4)+3*R[0]*(A[2]**2+E[2]**2)+6*E[1]**2*R[2]+4*E[1]*(3*R[1]*E[2]+R[0]*E[3])-R[4])*sin(A[0]))+(6*cos(A[0])*A[2]*(2*E[1]*R[1]+R[0]*E[2])+4*R[0]*cos(A[0])*E[1]*A[3]+(-4*E[1]**3*R[1]-6*R[0]*E[1]**2*E[2]+6*E[2]*R[2]+4*R[1]*E[3]+4*E[1]*R[3]+R[0]*E[4])*sin(A[0]))*sin(E[0]))+10*A[1]**2*(cos(E[0])*(cos(A[0])*(3*E[1]*(E[1]*R[1]+R[0]*E[2])-R[3])+(3*R[1]*A[2]+R[0]*A[3])*sin(A[0]))+(-(R[0]*cos(A[0])*E[1]**3)+cos(A[0])*(3*R[1]*E[2]+R[0]*E[3])+3*E[1]*(cos(A[0])*R[2]-R[0]*A[2]*sin(A[0])))*sin(E[0]));

    def d1UpdAER1(self, A : vector, E : vector, R : vector) -> array:
        return R[0]*cos(E[0])*E[1]+R[1]*sin(E[0]);

    def d2UpdAER2(self, A : vector, E : vector, R : vector) -> array:
        return 2*cos(E[0])*E[1]*R[1]+R[0]*cos(E[0])*E[2]-R[0]*E[1]**2*sin(E[0])+R[2]*sin(E[0]);

    def d3UpdAER3(self, A : vector, E : vector, R : vector) -> array:
        return -(R[0]*cos(E[0])*E[1]**3)+3*cos(E[0])*R[1]*E[2]+R[0]*cos(E[0])*E[3]-3*E[1]**2*R[1]*sin(E[0])+R[3]*sin(E[0])+3*E[1]*(cos(E[0])*R[2]-R[0]*E[2]*sin(E[0]));

    def d4UpdAER4(self, A : vector, E : vector, R : vector) -> array:
        return cos(E[0])*(-4*E[1]**3*R[1]-6*R[0]*E[1]**2*E[2]+6*E[2]*R[2]+4*R[1]*E[3]+4*E[1]*R[3]+R[0]*E[4])+(R[0]*E[1]**4-3*R[0]*E[2]**2-6*E[1]**2*R[2]-4*E[1]*(3*R[1]*E[2]+R[0]*E[3])+R[4])*sin(E[0]);

    def d5UpdAER5(self, A : vector, E : vector, R : vector) -> array:
        return cos(E[0])*(R[0]*E[1]**5-10*E[1]**3*R[2]+10*R[2]*E[3]-10*E[1]**2*(3*R[1]*E[2]+R[0]*E[3])+10*E[2]*R[3]+5*R[1]*E[4]+5*E[1]*(-3*R[0]*E[2]**2+R[4])+R[0]*E[5])+(5*E[1]**4*R[1]+10*R[0]*E[1]**3*E[2]-5*E[2]*(3*R[1]*E[2]+2*R[0]*E[3])-10*E[1]**2*R[3]-5*E[1]*(6*E[2]*R[2]+4*R[1]*E[3]+R[0]*E[4])+R[5])*sin(E[0]);

    