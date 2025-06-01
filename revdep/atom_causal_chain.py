from .depvar_parser import EbuildDepvarParser
from . import depvars

class CausalLink:
    def __init__(self, level, pkgname, items=None):
        if items is None:
            items = []

        self.level = level
        self.pkgname = pkgname
        self.items = items

    def add_item(self, depvar_name, cause):
        self.items.append((depvar_name, cause,))

    def __repr__(self):
        level = self.level
        out = f"{'    '*level}{self.pkgname} ,{self.pkgname}\n"
        for depvar_name,cause in self.items:
            out+=f"{'    '*level}- {depvar_name}: {cause}\n"
        return(out[:-1])

class AtomCausalChain:
    """
    Provides the causal chain for a given package name from the full system
    reverse dependency chain. 

    """
    def __init__(self, rdep_chain, pkgname):
        self.pkgname = pkgname
        self.pkg_rdep_chain = list(rdep_chain.get_pkg_rdep_chain(self.pkgname))
        self.causal_chain = self._get_causal_chain()

    def _get_atom_pkgname(self, atom):
        x = lambda t: t.data.kind
        p = EbuildDepvarParser(atom)
        p.root()
        t = p.to_tree()
        pkg = t.traverse_branches(["Atom", "CatPkg"], x)[0].data.value
        pkg = pkg.strip()
        return pkg

    def _check_for_atom(self, tree, pkg, prefix=[]):
        x = lambda t: t.data.kind
        pkg = self._get_atom_pkgname(pkg)
        reasons = []
        potential_reasons = []

        atoms = tree.traverse_branches(["Atom"], x)
        any_of_groups = tree.traverse_branches(["AnyOfGroup"], x)
        exactly_one_of_groups = tree.traverse_branches(["ExactlyOneOfGroup"], x)
        most_one_of_groups = tree.traverse_branches(["MostOneOfGroup"], x)
        dynamic_uses = tree.traverse_branches(["DynamicUse"], x)
        empty_groups = tree.traverse_branches(["PseudoGroup"], x)

        pkgnames = []
        for b in atoms:
            pkgname = b.traverse_branches(["CatPkg"], x)
            if len(pkgname) > 1: raise Exception
            pkgname = pkgname[0].data.value
            pkgname = self._get_atom_pkgname(pkgname)
            pkgnames.append(pkgname)
        potential_reasons += prefix+[pkg]
        if pkg in pkgnames:
            reasons += prefix+[pkg]

        for b in any_of_groups:
            reasons += self._check_for_atom(b, pkg, prefix+["||"])
        for b in exactly_one_of_groups:
            reasons += self._check_for_atom(b, pkg, prefix+["^^"])
        for b in most_one_of_groups:
            reasons += self._check_for_atom(b, pkg, prefix+["??"])

        for b in dynamic_uses:
            use_query = b.traverse_branches(["UseQuery"], x)
            if len(use_query) > 1: raise Exception
            use_query = use_query[0].data.value
            reasons += self._check_for_atom(b, pkg, prefix+[use_query])
        return(reasons)

    def _get_causal_chain(self):
        pkg_rdep_chain = self.pkg_rdep_chain

        levels = {}
        level,root = pkg_rdep_chain.pop(0)
        pkgname = self._get_atom_pkgname(root)
        levels[level] = pkgname

        pkgname = root
        link = CausalLink(level,root)
        yield(link)
        for level,pkgname in pkg_rdep_chain:
            link = CausalLink(level,pkgname)
            if pkgname == "@selected":
                yield(link)
                continue
            pkg_depvars = depvars.get_depvars(pkgname)
            levels[level] = self._get_atom_pkgname(pkgname)
            for depend_var,depend_str in zip(depvars.depvar_names.split(" "),pkg_depvars):
                p = EbuildDepvarParser(depend_str)
                p.root()
                tree = p.to_tree()
                cause = self._check_for_atom(tree, levels[level-1])
                if not cause:
                    continue
                link.add_item(depend_var,cause)
            yield(link)
