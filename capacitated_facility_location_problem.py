import os
import random
from qubots.base_problem import BaseProblem

class CapacitatedFacilityLocationProblem(BaseProblem):
    """
    Capacitated Facility Location Problem (CFLP)

    In this problem, a set of potential facilities must serve a number of sites.
    Each facility f has a given capacity and a fixed opening cost.
    Each site s has a given demand.
    There is an allocation cost for serving site s from facility f.

    A candidate solution is represented as a list of integers of length nb_sites,
    where the element at index s indicates the facility (0-indexed) assigned to site s.

    For each facility:
      - If at least one site is assigned to it, the facility is considered open and incurs its
        fixed opening cost.
      - The total allocation cost is the sum over sites served of allocation_price_data[f][s].
      - The capacity constraint requires that the sum of demands of sites assigned to facility f
        does not exceed capacity_data[f].

    The objective is to minimize the total cost (the sum of fixed opening costs for open facilities
    plus the allocation costs for all sites).
    """

    def __init__(self, instance_file=None, nb_max_facilities=None, nb_sites=None,
                 capacity_data=None, opening_price_data=None, demand_data=None,
                 allocation_price_data=None):
        if instance_file is not None:
            self._load_instance_from_file(instance_file)
        else:
            if (nb_max_facilities is None or nb_sites is None or capacity_data is None or
                opening_price_data is None or demand_data is None or allocation_price_data is None):
                raise ValueError("Either 'instance_file' or all instance parameters must be provided.")
            self.nb_max_facilities = nb_max_facilities
            self.nb_sites = nb_sites
            self.capacity_data = capacity_data
            self.opening_price_data = opening_price_data
            self.demand_data = demand_data
            self.allocation_price_data = allocation_price_data

    def _load_instance_from_file(self, filename):
        # Resolve relative path with respect to this module's directory.
        if not os.path.isabs(filename):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(base_dir, filename)
        with open(filename) as f:
            tokens = f.read().split()
        it = iter(tokens)
        self.nb_max_facilities = int(next(it))
        self.nb_sites = int(next(it))
        self.capacity_data = []
        self.opening_price_data = []
        self.allocation_price_data = []
        # Read capacities and fixed opening costs for each facility.
        for f in range(self.nb_max_facilities):
            self.capacity_data.append(float(next(it)))
            self.opening_price_data.append(float(next(it)))
            self.allocation_price_data.append([])
        # Read demand for each site.
        self.demand_data = []
        for s in range(self.nb_sites):
            self.demand_data.append(float(next(it)))
        # Read the allocation price matrix (facility by site).
        for f in range(self.nb_max_facilities):
            for s in range(self.nb_sites):
                self.allocation_price_data[f].append(float(next(it)))

    def evaluate_solution(self, solution) -> float:
        """
        Evaluate a candidate solution.

        The candidate solution should be a list of integers of length nb_sites, where each element is
        a facility index (in 0 .. nb_max_facilities-1) to which the corresponding site is assigned.

        For each facility f, let S_f be the set of sites assigned to f.
          - If S_f is non-empty, then f is open and its cost is:
              opening_price_data[f] + sum_{s in S_f} allocation_price_data[f][s]
          - Also, the capacity constraint must hold:
              sum_{s in S_f} demand_data[s] <= capacity_data[f]

        The objective is the sum of costs over all facilities.
        If any capacity constraint is violated or if the solution is invalid, a high penalty is returned.
        """
        PENALTY = 1e9
        if not isinstance(solution, (list, tuple)) or len(solution) != self.nb_sites:
            return PENALTY

        # Build assignments: for each facility, list the sites assigned to it.
        assignments = [[] for _ in range(self.nb_max_facilities)]
        for s, f in enumerate(solution):
            if not isinstance(f, int) or f < 0 or f >= self.nb_max_facilities:
                return PENALTY
            assignments[f].append(s)
        
        total_cost = 0.0
        # Evaluate cost per facility.
        for f in range(self.nb_max_facilities):
            if assignments[f]:
                total_demand = sum(self.demand_data[s] for s in assignments[f])
                if total_demand > self.capacity_data[f]:
                    return PENALTY
                allocation_cost = sum(self.allocation_price_data[f][s] for s in assignments[f])
                facility_cost = self.opening_price_data[f] + allocation_cost
                total_cost += facility_cost
        return total_cost

    def random_solution(self):
        """
        Generate a random candidate solution.

        Each site is randomly assigned to a facility index between 0 and nb_max_facilities-1.
        """
        return [random.randint(0, self.nb_max_facilities - 1) for _ in range(self.nb_sites)]
