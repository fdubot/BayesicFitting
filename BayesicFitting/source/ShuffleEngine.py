import numpy as numpy
import math
from . import Tools
from .Formatter import formatter as fmt

from .OrderEngine import OrderEngine

__author__ = "Do Kester"
__year__ = 2022
__license__ = "GPL3"
__version__ = "3.0.0"
__url__ = "https://www.bayesicfitting.nl"
__status__ = "Alpha"

#  * This file is part of the BayesicFitting package.
#  *
#  * BayesicFitting is free software: you can redistribute it and/or modify
#  * it under the terms of the GNU Lesser General Public License as
#  * published by the Free Software Foundation, either version 3 of
#  * the License, or ( at your option ) any later version.
#  *
#  * BayesicFitting is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  * GNU Lesser General Public License for more details.
#  *
#  * The GPL3 license can be found at <http://www.gnu.org/licenses/>.
#  *
#  *    2018 - 2022 Do Kester

class ShuffleEngine( OrderEngine ):
    """
    The ShuffleEngine tries to shuffle a selection of the parameters in place.

    Input order : [0,1,2,3,4,5,6,7,8,9]

    output order: [0,1,2,5,3,7.4,6,8,9]

    It belongs to the class of generalized travelling salesman problems
    where the parameters of the problem is an ordered list.

    The walker is kept when the logLikelihood > lowLhood

    Author       Do Kester.

    """
    #  *********CONSTRUCTORS***************************************************
    def __init__( self, walkers, errdis, copy=None, seed=4213, verbose=0 ):
        """
        Constructor.

        Parameters
        ----------
        walkers : SampleList
            walkers to be diffused
        errdis : ErrorDistribution
            error distribution to be used
        copy : ShuffleEngine
            to be copied
        seed : int
            for random number generator

        """
        super( ).__init__( walkers, errdis, copy=copy, seed=seed, verbose=verbose )

    def copy( self ):
        """ Return copy of this.  """
        return ShuffleEngine( self.walkers, self.errdis, copy=self )

    def __str__( self ):
        return str( "ShuffleEngine" )

    #  *********EXECUTE***************************************************
    def execute( self, kw, lowLhood ):
        """
        Execute the engine by diffusing the parameters.

        Parameters
        ----------
        kw : int
            id of walker to diffuse
        lowLhood : float
            lower limit in logLikelihood

        Returns
        -------
        int : the number of successfull moves

        """
        walker = self.walkers[kw]
        problem = walker.problem
        np = problem.npars
        param = walker.allpars

        src = self.rng.randint( np )
        t = 2 + min( self.rng.geometric( 0.2 ), np // 2 )

        while t > 1 :
            ent = src + t
            ptry = numpy.roll( param, src )
            ptry[:ent] = self.rng.permutation( ptry[:ent] )


            Ltry = self.errdis.logLikelihood( problem, ptry )

            if self.verbose > 4 :
                print( "Shuffle  ", src, ent, t, fmt( lowLhood ), fmt( Ltry ) )
                print( fmt( param, max=None, format='%3d' ) )
                print( fmt( ptry, max=None, format='%3d' ) )

            if Ltry >= lowLhood:
                self.reportSuccess( )
                self.setWalker( walker.id, problem, ptry, Ltry )

                return t

            t = self.rng.randint( t )
            self.reportFailed( )

        self.reportReject()

        return 0                        # nr of reordered parameters


