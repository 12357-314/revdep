class SystemReverseDependencyChain:
    """
    Parses the output from `emerge --pretend --verbose --emptytree --depclean`
    to create a dictionary mapping dependencies to dependees and the
    `get_pkg_rdep_chain` method to fetch a hierarchy of reverse dependencies
    for a package. 

    """
    def __init__(self, emerge_deps_output):
        lines = emerge_deps_output.split("\n")

        self._lines = self._filter_input_lines(lines)
        self.dependees_by_dependency = self._find_dependees()

    def _filter_input_lines(self, input_lines):
        start_token = "pulled in by:"
        end_token = ">>>"
        start_flag = False
        end_flag = False
        for line in input_lines:
            if not start_flag: start_flag = line.endswith(start_token)
            if start_flag: end_flag = line.startswith(end_token)
            if end_flag: break
            yield(line)

    def _find_dependees(self):
        is_blank = lambda line: not line.strip()

        dependees_by_dependency = {}
        dependee_indent = 0
        dependee_pkgname = ""
        for line in self._lines:
            if is_blank(line): continue

            line_indent = len(line) - len(line.lstrip())
            line_pkgname = line.strip().split(" ")[0]

            if not dependee_indent or line_indent <= dependee_indent:
                dependee_indent = line_indent
                dependee_pkgname = line_pkgname
            else: 
                dependees_by_dependency.setdefault(dependee_pkgname, [])
                dependees_by_dependency[dependee_pkgname].append(line_pkgname)
        return(dependees_by_dependency)

    def get_pkg_rdep_chain(self, pkgname=None, _seen=None, _level=0):
        atom_group_prefix = "@"

        if _seen is None: _seen = []
        if pkgname is None: pkgname = self.prompt_pkgname()
        yield((_level,pkgname,))

        for dependency_name in self.dependees_by_dependency.get(pkgname,[]):
            if dependency_name in _seen:
                continue
            if not dependency_name.startswith(atom_group_prefix):
                _seen.append(dependency_name)
            yield from self.get_pkg_rdep_chain(
                pkgname=dependency_name, 
                _seen=_seen, 
                _level=_level+1)


