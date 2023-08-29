class Group:
    """A group of units of the given order."""
    def __init__(self, order: int, units: list):
        assert order >= 1, f"Order must be >= 1, got {order}"
        assert len(units) == order, f"Number of units must be equal to order, got {len(units)} units and order {order}"

        self._order = order
        self._units = units
        self._current

    def __iter__(self):
        return iter(self._units)
    
    def __str__(self):
        return f"Group(order={self._order}, units={self._units})"
       

class GroupList:
    """A list of groups of the same, given order."""
    def __init__(self, order: int):
        assert order >= 1, f"Order must be >= 1, got {order}"
        self._order = order
        self._groups = []
    
    def add_group(self, group: Group):
        assert isinstance(group, Group), "Only Group instances can be added."
        assert group._order == self._order, f"Group order must be {self._order}, got {group._order}"
        self._groups.append(group)
        
    def __iter__(self):
        return iter(self._groups)
    
    def __len__(self):
        return len(self._groups)
    
    def __getitem__(self, index):
        return self._groups[index]

    def __str__(self):
        return "\n".join(str(group) for group in self._groups)