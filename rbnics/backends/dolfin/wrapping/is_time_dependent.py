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

from dolfin import has_pybind11
if has_pybind11():
    from dolfin.function.expression import BaseExpression
else:
    from dolfin import Expression as BaseExpression
from rbnics.utils.decorators import get_problem_from_solution
from rbnics.backends.dolfin.wrapping.pull_back_to_reference_domain import is_pull_back_expression, is_pull_back_expression_time_dependent

def basic_is_time_dependent(backend, wrapping):
    def _basic_is_time_dependent(expression_or_form, iterator):
        for node in iterator(expression_or_form):
            # ... parametrized expressions
            if isinstance(node, BaseExpression):
                if is_pull_back_expression(node) and is_pull_back_expression_time_dependent(node):
                    return True
                else:
                    if has_pybind11():
                        parameters = node._parameters
                    else:
                        parameters = node.user_parameters
                    if "t" in parameters:
                        return True
            # ... problem solutions related to nonlinear terms
            elif wrapping.is_problem_solution_type(node):
                if wrapping.is_problem_solution(node):
                    (preprocessed_node, component, truth_solution) = wrapping.solution_identify_component(node)
                    truth_problem = get_problem_from_solution(truth_solution)
                    if hasattr(truth_problem, "set_time"):
                        return True
                elif wrapping.is_problem_solution_dot(node):
                    return True
        return False
    return _basic_is_time_dependent
    
from rbnics.backends.dolfin.wrapping.is_problem_solution import is_problem_solution
from rbnics.backends.dolfin.wrapping.is_problem_solution_dot import is_problem_solution_dot
from rbnics.backends.dolfin.wrapping.is_problem_solution_type import is_problem_solution_type
from rbnics.backends.dolfin.wrapping.solution_identify_component import solution_identify_component
from rbnics.backends.dolfin.wrapping.solution_iterator import solution_iterator
from rbnics.utils.decorators import ModuleWrapper
backend = ModuleWrapper()
wrapping = ModuleWrapper(is_problem_solution, is_problem_solution_dot, is_problem_solution_type, solution_identify_component, solution_iterator)
is_time_dependent = basic_is_time_dependent(backend, wrapping)
