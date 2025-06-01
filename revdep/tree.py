class Tree:
    """
    Provides a tree structure with each tree having a list of branch trees, a
    root tree, and a data attribute. A method for recursing through the tree's
    branches to a specific branch and one for printing the tree are also
    provided. 

    """
    def __init__(self, data=None):
        self.data = data
        self._root = None
        self._branches = []

    @property
    def branches(self):
        return self._branches

    def add_branch(self, tree):
        tree._root = self
        self._branches.append(tree)

    def __repr__(self, num_indents=0):
        output = f"{' '*4*num_indents}{self.data}\n"
        for b in self.branches:
            output += b.__repr__(num_indents=num_indents+1)
        return output

    def traverse_branches(self, values, key):
        branch_by_value = {}
        branch = [self]

        for value in values:
            if type(value) is int: branch = [branch[value]]; continue
            elif len(branch) == 1: branch = branch[0]
            else: raise Exception(
                f"Multiple potential branches for {value}.")

            branch_by_value = {}
            for branch in branch.branches:
                branch_value = key(branch)
                branch_by_value.setdefault(branch_value, []).append(branch)
            branch = branch_by_value.get(value, [])
        return branch


