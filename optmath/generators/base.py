"""Generator abstract base class"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import gurobipy as gp


class BaseGenerator(ABC):
    """Abstract base class for optimization problem instance generators"""

    @abstractmethod
    def generate_instance(self) -> "gp.Model":
        """
        Generate an optimization problem instance.
        Returns:
            gurobipy.Model: Configured Gurobi model
        """
        pass
