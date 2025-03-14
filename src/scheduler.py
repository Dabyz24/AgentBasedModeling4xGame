from typing import Callable, Optional, Type

import mesa


class RandomActivationByTypeFiltered(mesa.time.RandomActivationByType):
    """
    A scheduler that overrides the get_type_count method to allow for filtering
    of agents by a function before counting.

    Example:
    >>> scheduler = RandomActivationByTypeFiltered(model)
    >>> scheduler.get_type_count(AgentA, lambda agent: agent.some_attribute > 10)
    """

    def get_type_count(self, type_class: Type[mesa.Agent], filter_func: Optional[Callable[[mesa.Agent], bool]] = None) -> int:
        """
        Returns the current number of agents of certain type in the queue
        that satisfy the filter function.
        """
        if type_class not in self.agents_by_type:
            return 0
        count = 0
        for agent in self.agents_by_type[type_class].values():
            if filter_func is None or filter_func(agent):
                count += 1
        return count