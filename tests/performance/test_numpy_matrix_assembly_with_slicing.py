# Copyright (C) 2015-2018 by the RBniCS authors
#
# This file is part of RBniCS.
#
# RBniCS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RBniCS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RBniCS. If not, see <http://www.gnu.org/licenses/>.
#

import pytest
from numpy import isclose
from numpy.linalg import norm
from numpy.random import randint
from rbnics.backends import product as factory_product, sum as factory_sum
from rbnics.backends.online import OnlineAffineExpansionStorage, online_product, online_sum
from rbnics.backends.online.numpy import product as numpy_product, sum as numpy_sum
from test_utils import RandomNumpyMatrix, RandomTuple

product = None
sum = None
all_product = {"numpy": numpy_product, "online": online_product, "factory": factory_product}
all_sum = {"numpy": numpy_sum, "online": online_sum, "factory": factory_sum}

class Data(object):
    def __init__(self, Nmax, Q):
        self.Nmax = Nmax
        self.Q = Q
        
    def generate_random(self):
        A = OnlineAffineExpansionStorage(self.Q)
        for i in range(self.Q):
            # Generate random matrix
            A[i] = RandomNumpyMatrix(self.Nmax, self.Nmax)
        # Genereate random theta
        theta = RandomTuple(self.Q)
        # Generate N <= Nmax
        N = randint(1, self.Nmax + 1)
        # Return
        return (theta, A, N)
        
    def evaluate_builtin(self, theta, A, N):
        result_builtin = theta[0]*A[0][:N, :N]
        for i in range(1, self.Q):
            result_builtin += theta[i]*A[i][:N, :N]
        return result_builtin
        
    def evaluate_backend(self, theta, A, N):
        return sum(product(theta, A[:N, :N]))
        
    def assert_backend(self, theta, A, N, result_backend):
        result_builtin = self.evaluate_builtin(theta, A, N)
        relative_error = norm(result_builtin - result_backend)/norm(result_builtin)
        assert isclose(relative_error, 0., atol=1e-12)

@pytest.mark.parametrize("N", [2**i for i in range(1, 9)])
@pytest.mark.parametrize("Q", [10 + 4*j for j in range(1, 4)])
@pytest.mark.parametrize("test_type", ["builtin"] + list(all_product.keys()))
def test_numpy_matrix_assembly_with_slicing(N, Q, test_type, benchmark):
    data = Data(N, Q)
    print("N = " + str(N) + ", Q = " + str(Q))
    if test_type == "builtin":
        print("Testing", test_type)
        benchmark(data.evaluate_builtin, setup=data.generate_random)
    else:
        print("Testing", test_type, "backend")
        global product, sum
        product, sum = all_product[test_type], all_sum[test_type]
        benchmark(data.evaluate_backend, setup=data.generate_random, teardown=data.assert_backend)
