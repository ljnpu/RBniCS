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
## @file sum.py
#  @brief sum function to assemble truth/reduced affine expansions.
#
#  @author Francesco Ballarin <francesco.ballarin@sissa.it>
#  @author Gianluigi Rozza    <gianluigi.rozza@sissa.it>
#  @author Alberto   Sartori  <alberto.sartori@sissa.it>

###########################     OFFLINE AND ONLINE COMMON INTERFACES     ########################### 
## @defgroup OfflineOnlineInterfaces Common interfaces for offline and online
#  @{

from RBniCS.linear_algebra.truth_vector import TruthVector
from RBniCS.linear_algebra.truth_matrix import TruthMatrix
from RBniCS.linear_algebra.online_vector import OnlineVector_Type
from RBniCS.linear_algebra.online_matrix import OnlineMatrix_Type

# sum function to assemble truth/reduced affine expansions. To be used in combination with the product method.
__std_sum = sum
def sum(product_output):
    if isinstance(product_output[0], tuple):
        if isinstance(product_output[0][1], TruthMatrix):
            sum_output = product_output[0][1].copy()
            sum_output.zero()
            for i in range(len(product_output)):
                sum_output += product_output[i][0]*product_output[i][1]
            return sum_output
        elif isinstance(product_output[0][1], TruthVector):
            sum_output = product_output[0][1].copy()
            sum_output.zero()
            for i in range(len(product_output)):
                sum_output.add_local(product_output[i][0]*product_output[i][1].array())
            sum_output.apply("insert")
            return sum_output
        elif \
            isinstance(product_output[0][1], OnlineMatrix_Type) or isinstance(product_output[0][1], OnlineVector_Type) \
        :
            sum_output = product_output[0][0]*product_output[0][1]
            for i in range(1,len(product_output)):
                sum_output += product_output[i][0]*product_output[i][1]
            return sum_output
    elif isinstance(product_output[0], list): # we use this Dirichlet BCs with FEniCS
        boundary_id_to_function_space_map = {} # first argument of the constructor
        boundary_id_to_function_map = {} # second argument of the constructor
        boundary_id_to_boundary_mesh_map = {} # third argument of the constructor
        for i in range(len(product_output)):
            # Each element of the list contains a tuple. Owing to FEniCS documentation (overloaded version with MeshFunction argument),
            # its fourth argument is the subdomain id, to be collected and used as map index.
            assert len(product_output[i]) == 4
            function_space = product_output[0]
            function = product_output[1]
            boundary_mesh = product_output[2]
            boundary_id = product_output[3]
            if not boundary_id in boundary_id_to_function_map:
                assert not boundary_id in boundary_id_to_function_space_map
                assert not boundary_id in boundary_id_to_boundary_mesh_map
                boundary_id_to_function_space_map[boundary_id] = function_space
                boundary_id_to_function_map[boundary_id] = function
                boundary_id_to_boundary_mesh_map[boundary_id] = boundary_mesh
            else:
                assert boundary_id_to_function_space_map[boundary_id] == function_space
                assert boundary_id_to_boundary_mesh_map[boundary_id] == boundary_mesh
                boundary_id_to_function_map[boundary_id] += function
        output = []
        for boundary_id in boundary_id_to_function_map.keys():
            assert boundary_id in boundary_id_to_function_space_map
            assert boundary_id in boundary_id_to_boundary_mesh_map
            output.append( \
                DirichletBC( \
                    boundary_id_to_function_space_map[boundary_id], \
                    boundary_id_to_function_map[boundary_id], \
                    boundary_id_to_boundary_mesh_map[boundary_id], \
                    boundary_id \
                ) \
            )
    else: # preserve the standard python sum function
        return __std_sum(product_output)
    return output
        
#  @}
########################### end - OFFLINE AND ONLINE COMMON INTERFACES - end ########################### 
