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
    from dolfin.cpp.la import GenericVector
else:
    from dolfin import GenericVector

def Vector():
    raise NotImplementedError("This is dummy function (not required by the interface) just store the Type")
    
# Attach a Type() function
def Type():
    return GenericVector
Vector.Type = Type

# swig wrappers prevent GenericVector from being hashable
if not has_pybind11():
    assert GenericVector.__hash__ is None
    del GenericVector.__hash__

# pybind11 wrappers do not implement __neg__ unary operator
if has_pybind11():
    def custom__neg__(self):
        return -1.*self
    setattr(GenericVector, "__neg__", custom__neg__)

# Preserve generator attribute in algebraic operators, as required by DEIM
def preserve_generator_attribute(operator):
    original_operator = getattr(GenericVector, operator)
    def custom_operator(self, other):
        if hasattr(self, "generator"):
            output = original_operator(self, other)
            output.generator = self.generator
            return output
        else:
            return original_operator(self, other)
    setattr(GenericVector, operator, custom_operator)
    
for operator in ("__add__", "__radd__", "__iadd__", "__sub__", "__rsub__", "__isub__", "__mul__", "__rmul__", "__imul__", "__truediv__", "__itruediv__"):
    preserve_generator_attribute(operator)
