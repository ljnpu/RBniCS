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

from ufl import Form
from ufl.algorithms import expand_derivatives
from dolfin import assemble
from rbnics.backends.basic import ParametrizedTensorFactory as BasicParametrizedTensorFactory
from rbnics.backends.dolfin.copy import copy
from rbnics.backends.dolfin.high_order_proper_orthogonal_decomposition import HighOrderProperOrthogonalDecomposition
from rbnics.backends.dolfin.function import Function
from rbnics.backends.dolfin.reduced_mesh import ReducedMesh
from rbnics.backends.dolfin.tensor_basis_list import TensorBasisList
from rbnics.backends.dolfin.tensor_snapshots_list import TensorSnapshotsList
from rbnics.backends.dolfin.wrapping import form_argument_space, form_description, form_iterator, form_name, get_auxiliary_problem_for_non_parametrized_function, is_parametrized, is_problem_solution, is_problem_solution_dot, is_problem_solution_type, is_time_dependent, remove_complex_nodes, solution_dot_identify_component, solution_identify_component, solution_iterator
from rbnics.utils.decorators import BackendFor, ModuleWrapper

backend = ModuleWrapper(copy, Function, HighOrderProperOrthogonalDecomposition, ReducedMesh, TensorBasisList, TensorSnapshotsList)
wrapping = ModuleWrapper(form_iterator, is_problem_solution, is_problem_solution_dot, is_problem_solution_type, solution_dot_identify_component, solution_identify_component, solution_iterator, form_description=form_description, form_name=form_name, get_auxiliary_problem_for_non_parametrized_function=get_auxiliary_problem_for_non_parametrized_function, is_parametrized=is_parametrized, is_time_dependent=is_time_dependent)
ParametrizedTensorFactory_Base = BasicParametrizedTensorFactory(backend, wrapping)

@BackendFor("dolfin", inputs=(Form, ))
class ParametrizedTensorFactory(ParametrizedTensorFactory_Base):
    def __init__(self, form):
        # Preprocess form
        form = expand_derivatives(form)
        form = remove_complex_nodes(form) # TODO support forms in the complex field
        # Extract spaces from forms
        len_spaces = len(form.arguments())
        assert len_spaces in (0, 1, 2)
        if len_spaces is 2:
            spaces = (
                form_argument_space(form, 0),
                form_argument_space(form, 1)
            )
        elif len_spaces is 1:
            spaces = (
                form_argument_space(form, 0),
            )
        elif len_spaces is 0:
            spaces = ()
        else:
            raise ValueError("Invalid arguments")
        # Create empty snapshot
        if len_spaces in (1, 2):
            def assemble_empty_snapshot():
                empty_snapshot = assemble(form, keep_diagonal=True)
                empty_snapshot.zero()
                empty_snapshot.generator = self
                return empty_snapshot
        elif len_spaces is 0:
            def assemble_empty_snapshot():
                return 0.
        else:
            raise ValueError("Invalid arguments")
        # Call Parent
        ParametrizedTensorFactory_Base.__init__(self, form, spaces, assemble_empty_snapshot)
        
    def __eq__(self, other):
        return (
            isinstance(other, type(self))
                and
            self._form.equals(other._form)
                and
            self._spaces == other._spaces
        )
        
    def __hash__(self):
        return hash((self._form, self._spaces))
        
    def create_interpolation_locations_container(self):
        # Populate subdomain data
        subdomain_data = list()
        for integral in form_iterator(self._form, "integrals"):
            if integral.subdomain_data() is not None and integral.subdomain_data() not in subdomain_data:
                subdomain_data.append(integral.subdomain_data())
        if len(subdomain_data) is 0:
            subdomain_data = None
        # Create reduced mesh
        return ParametrizedTensorFactory_Base.create_interpolation_locations_container(self, subdomain_data=subdomain_data)
