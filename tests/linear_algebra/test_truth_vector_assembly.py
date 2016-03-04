# Copyright (C) 2015-2016 by the RBniCS authors
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
## @file test_truth_vector_assembly.py
#  @brief Test sum_{i = 1}^{Q} theta_i F_i
#
#  @author Francesco Ballarin <francesco.ballarin@sissa.it>
#  @author Gianluigi Rozza    <gianluigi.rozza@sissa.it>
#  @author Alberto   Sartori  <alberto.sartori@sissa.it>

from __future__ import print_function
from test_main import TestBase
from dolfin import *
from RBniCS.linear_algebra.online_matrix import OnlineMatrix
from RBniCS.linear_algebra.sum import sum
from RBniCS.linear_algebra.product import product

class Test(TestBase):
    def __init__(self, Nh, Q):
        self.Q = Q
        mesh = UnitSquareMesh(Nh, Nh)
        V = FunctionSpace(mesh, "Lagrange", 1)
        self.f = Function(V)
        # Call parent init
        TestBase.__init__(self)
            
    def run(self):
        Q = self.Q
        test_id = self.test_id
        test_subid = self.test_subid
        if test_id >= 0:
            if not self.index in self.storage:
                F = ()
                for i in range(self.Q):
                    # Generate random vectors
                    self.f.vector().set_local(self.rand(self.f.vector().array().size))
                    self.f.vector().apply("insert")
                    # Generate random matrix
                    F += (self.f.vector().copy(),)
                # Genereate random theta
                theta = tuple(self.rand(Q))
                # Store
                self.storage[self.index] = (theta, F)
            else:
                (theta, F) = self.storage[self.index]
            self.index += 1
        if test_id >= 1:
            if test_id > 1 or (test_id == 1 and test_subid == "a"):
                # Time using built in methods
                assembled_vector_builtin = F[0].copy()
                assembled_vector_builtin.zero()
                for i in range(self.Q):
                    assembled_vector_builtin.add_local(theta[i]*F[i].array())
                assembled_vector_builtin.apply("insert")
            if test_id > 1 or (test_id == 1 and test_subid == "b"):
                # Time using sum(product()) method
                assembled_vector_sum_product = sum(product(theta, F))
        if test_id >= 2:
            return (assembled_vector_builtin - assembled_vector_sum_product).norm("l2")/assembled_vector_builtin.norm("l2")

for i in range(3, 7):
    Nh = 2**i
    for j in range(1, 4):
        Q = 10 + 4*j
        test = Test(Nh, Q)
        print("Nh =", test.f.vector().size(), "and Q =", Q)
        
        test.init_test(0)
        (usec_0_build, usec_0_access) = test.timeit()
        print("Construction:", usec_0_build, "usec", "(number of runs: ", test.number_of_runs(), ")")
        print("Access:", usec_0_access, "usec", "(number of runs: ", test.number_of_runs(), ")")
        
        test.init_test(1, "a")
        usec_1a = test.timeit()
        print("Builtin method:", usec_1a - usec_0_access, "usec", "(number of runs: ", test.number_of_runs(), ")")
        
        test.init_test(1, "b")
        usec_1b = test.timeit()
        print("sum(product()) method:", usec_1b - usec_0_access, "usec", "(number of runs: ", test.number_of_runs(), ")")
        
        print("Relative overhead of the sum(product()) method:", (usec_1b - usec_1a)/(usec_1a - usec_0_access))
        
        test.init_test(2)
        error = test.average()
        print("Relative error:", error)
    
