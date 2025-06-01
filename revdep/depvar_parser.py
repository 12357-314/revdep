import functools
from .tree import Tree
from .parcel import Parcel

class EbuildDepvarParser:
    def __init__(self, depvar):
        self.depvar = depvar
        self.parcels = []
        self.i = 0

    def reset(self, i=None):
        if i is None: i = self.i
        # else: self.i = i
        self.parcels = [p for p in self.parcels if p.index_start<i]

    def require(self, 
        options=[], 
        at_least=None, 
        at_most=None, 
        exactly=None, 
        prev_index=None,
    ):
        if prev_index is None:
            prev_index = self.i

        rets = []
        for option in options:
            _i = self.i
            self.look([option])
            rets.append(_i<self.i)


        flag = any((
            (    at_least is None  and all(rets)            ),
            (not at_least is None  and sum(rets) >= at_least),
            (not at_most  is None  and sum(rets) <= at_most ),
            (not exactly  is None  and sum(rets) == exactly ),
            ))

        if not flag: 
            self.i = prev_index
            self.reset(prev_index)
        return flag

    def look(self, options):
        _i = self.i
        for option in options:
            if callable(option): option()
            if self.i >= len(self.depvar):
                if option is None:
                    self.i += 1
            elif self.depvar[self.i] == option: self.i += 1
            if self.i>_i: break

    def read(self, options=[], exceptions=[], count=1, name=None):
        i = _i = self.i

        cur_count = 0
        while True:
            if any((
                count!=-1 and cur_count>=count,
            )): break
            
            self.look(exceptions)
            if self.i > i: 
                self.i = i
                break

            self.look(options)
            if self.i == i: break

            i = self.i
            cur_count += 1

        if (_i < i) and not (name is None):
            parcel = Parcel(_i, i, self.depvar[_i:i], name)
            self.parcels.append(parcel)


    def reads(name):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                self.read(*args, options=[lambda: func(self)], name=name, **kwargs)
            return wrapper
        return decorator


    def lalpha(self): self.read("abcdefghijklmnopqrstuvwxyz", name="AlphaLower")
    def ualpha(self): self.read("ABCDEFGHIJKLMNOPQRSTUVWXYZ", name="AlphaUpper")
    def digit(self): self.read("1234567890", name="Digit")
    def whitespace(self): self.read("\n\t ", name="Whitespace")
    def alpha(self): self.read([self.lalpha, self.ualpha], name="Alpha")
    def alphadig(self): self.read([self.alpha, self.digit], name="AlphaDigit")

    @reads("UseName")
    def use_name(self): 
        _i = self.i
        if not self.require([self.alphadig], prev_index=_i): return
        self.read([self.alphadig, *"+_@-"], count=-1)

    def use_not(self): self.read("!", name="!Use")
    def useq(self): self.read("?", name="Use?")
    @reads("UseQuery")
    def use_query(self):
        _i = self.i
        self.use_not()
        if not self.require([self.use_name], prev_index=_i): return
        if not self.require([self.useq], prev_index=_i): return

    def gt(self): self.read(">", name="gt")
    def lt(self): self.read("<", name="lt")
    def eq(self): self.read("=", name="eq")
    def ax(self): self.read("~", name="ax")
    @reads("gteq")
    def gteq(self):
        _i = self.i
        if not self.require([self.gt, self.eq], prev_index=_i): return 
    @reads("lteq")
    def lteq(self):
        _i = self.i
        if not self.require([self.lt, self.eq], prev_index=_i): return 
    def ver_gate(self): self.read(
        [
            self.gteq, self.lteq, 
            self.gt, self.lt, 
            self.eq, self.ax
        ], 
        name="VersionGate")

    def bang(self): self.read("!", name="Bang")
    def soft_block(self): self.read([self.bang], name="SoftBlock")
    @reads("StrongBlock")
    def strong_block(self): 
        _i = self.i
        if not self.require([self.bang]*2, exactly=2, prev_index=_i): return
    def block(self): self.read([self.strong_block, self.soft_block], name="Block")

    def ver_sep(self): self.read("-", name="VersionSep")
    def ver_maj(self): self.read([self.digit], count=-1, name="VersionMajor")
    def ver_del(self): self.read(".", name="VersionDelimiter")
    def ver_op(self): self.read("*", name="VersionWildcard")
    @reads("VersionMinor")
    def ver_min(self): 
        _i = self.i
        if not self.require([self.ver_del], prev_index=_i): return
        self.read([self.digit], count=-1)
    @reads("VersionNumber")
    def ver_num(self):
        _i = self.i
        if not self.require([self.ver_maj], prev_index=self.i): return
        self.read([self.ver_min], count=-1)
        self.ver_op()
    def ver_letter(self): self.read([self.alpha], name="VersionLetter")
    def ver_rel_sep(self): self.read("_", name="VersionReleaseSep")
    def ver_rel_prefix(self): self.read([self.alpha], count=-1, name="VersionReleasePrefix")
    def ver_rel_suffix(self): self.read([self.digit], count=-1, name="VersionReleaseSuffix")
    def ver_end(self): self.read([*")", self.whitespace, None], name="VerEnd")
    @reads("VersionRelease")
    def ver_release(self):
        _i = self.i
        if not self.require([self.ver_rel_sep, self.ver_rel_prefix], prev_index=_i): return
        self.ver_rel_suffix()
    @reads("VersionRevision")
    def ver_revision(self): 
        _i = self.i
        if not self.require([self.ver_sep], prev_index=_i): return
        if not self.require([self.alpha], prev_index=_i): return
        self.read([self.digit], count=-1)
    @reads("Version")
    def version(self):
        _i = self.i
        if not self.require([self.ver_sep, self.ver_num], prev_index=_i): return
        self.ver_letter()
        self.read([self.ver_release], count=-1)
        self.ver_revision()
        if not self.require([self.ver_end], prev_index=_i): return

    def pkg_char(self): self.read([*"+_-", self.alphadig], [self.version], name="PkgChar")
    @reads("PackageName")
    def pkg_name(self):
        _i = self.i
        if not self.require([lambda: self.read([*"_", self.alphadig], name="PkgChar")], prev_index=_i): return
        self.read([self.pkg_char], count=-1)
        self.read([self.whitespace], count=-1)
    def catpkg_delim(self): self.read("/", name="CatPkgDelim")
    @reads("CategoryName")
    def cat_name(self): 
        _i = self.i
        if not self.require([lambda: self.read([*"_", self.alphadig], count=1, name="CatChar_1")], prev_index=_i): return
        self.read([*"+_.-", self.alphadig], count=-1, name="CatChar")
    @reads("CatPkg")
    def catpkg(self):
        self.require([self.cat_name, self.catpkg_delim])
        self.pkg_name()

    def slot_sep(self): self.read(":", name="SlotSep")
    def slot_first_char(self): self.read([*"_", self.alphadig], name="SlotChar")
    def slot_char(self): self.read([*"+_.-", self.alphadig], name="SlotChar")
    def slot_op(self): self.read("*=", name="SlotOp")
    @reads("SlotBase")
    def slot_base(self): 
        _i = self.i
        if not self.require([self.slot_first_char], prev_index=_i): return
        self.read([self.slot_char], count=-1)
    def subslot_sep(self): self.read("/", name="SubslotSep")
    @reads("Subslot")
    def subslot(self):
        _i = self.i
        if not self.require([self.subslot_sep], prev_index=_i): return
        self.slot_base()
    @reads("Slot")
    def slot(self):
        _i = self.i
        if not self.require([self.slot_sep], prev_index=_i): return
        self.slot_base()
        self.subslot()
        self.slot_op()

    def use_default_open(self): self.read("(", name="UseDefaultOpen")
    def use_default_close(self): self.read(")", name="UseDefaultClose")
    @reads("UseDefault")
    def use_default(self):
        _i = self.i
        if not self.require([self.use_default_open], prev_index=_i): return
        self.read("+-")
        if not self.require([self.use_default_close], prev_index=_i): return

    def use_dep_sep(self): self.read(",", name="UseDependencySep")
    def use_dep_not(self): self.read("-", name="UseDependencyNot")
    @reads("UseDependency")
    def use_dep(self):
        _i = self.i
        self.use_dep_sep()
        self.use_dep_not()
        if not self.require([self.use_name], prev_index=_i): return
        self.use_default()
        self.useq()
    def use_deps_open(self): self.read("[", name="UseDependencyOpen")
    def use_deps_close(self): self.read("]", name="UseDependencyClose")
    def use_cond_op(self): self.read("?=", name="UseConditionalOperator")
    @reads("UseConditional")
    def use_cond(self):
        _i = self.i
        if not self.require([self.use_deps_open], prev_index=_i): return
        self.read([self.use_not])
        if not self.require([self.use_name], prev_index=_i): return
        if not self.require([self.use_cond_op], prev_index=_i): return
        if not self.require([self.use_deps_close], prev_index=_i): return
    @reads("UseDependencies")
    def use_deps(self):
        _i = self.i
        if not self.require([self.use_deps_open], prev_index=_i): return
        self.read([self.use_dep], count=-1)
        if not self.require([self.use_deps_close], prev_index=_i): return

    @reads("Atom")
    def atom(self):
        _i = self.i
        self.block()
        self.ver_gate()
        if not self.require([self.catpkg], prev_index=_i): return
        self.version()
        self.slot()
        self.require([self.use_deps, self.use_cond], at_most=1)
        self.read([self.whitespace], count=-1)

    def group_open(self): self.read("(", name="GroupOpen")
    def group_close(self): self.read(")", name="GroupClose")
    def any_of_group_symbol(self): self.read("|", count=2, name="AnyOfGroupSymbol")
    @reads("AnyOfGroup")
    def any_of_group(self):
        _i = self.i
        if not self.require([self.any_of_group_symbol], prev_index=_i): return
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_open], prev_index=_i): return
        self.read([self.whitespace],count=-1)
        self.read([self.atom,self.dynamic_use,self.all_of_group], count=-1)
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_close], prev_index=_i): return
        self.read([self.whitespace],count=-1)

    def exactly_one_of_group_symbol(self): self.read("^", count=2, name="ExactlyOneOfGroupSymbol")
    @reads("ExactlyOneOfGroup")
    def exactly_one_of_group(self):
        _i = self.i
        if not self.require([self.exactly_one_of_group_symbol], prev_index=_i): return
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_open], prev_index=_i): return
        self.read([self.whitespace],count=-1)
        self.read([self.atom,self.dynamic_use,self.all_of_group], count=-1)
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_close], prev_index=_i): return
        self.read([self.whitespace],count=-1)

    def most_one_of_group_symbol(self): self.read("?", count=2, name="MostOneOfGroupSymbol")
    @reads("MostOneOfGroup")
    def most_one_of_group(self):
        _i = self.i
        if not self.require([self.most_one_of_group_symbol], prev_index=_i): return
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_open], prev_index=_i): return
        self.read([self.whitespace],count=-1)
        self.read([self.atom,self.dynamic_use,self.all_of_group], count=-1)
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_close], prev_index=_i): return
        self.read([self.whitespace],count=-1)

    @reads("AllOfGroup")
    def all_of_group(self):
        _i = self.i
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_open], prev_index=_i): return
        self.read([self.whitespace],count=-1)
        self.read([self.atom,self.dynamic_use,self.all_of_group], count=-1)
        self.read([self.whitespace],count=-1)
        if not self.require([self.group_close], prev_index=_i): return
        self.read([self.whitespace],count=-1)

    def dynamic_use_open(self): self.read("(", name="DynamicUseOpen")
    def dynamic_use_close(self): self.read(")", name="DynamicUseClose")
    @reads("DynamicUse")
    def dynamic_use(self):
        _i = self.i
        if not self.require([self.use_query], prev_index=_i): return
        self.read([self.whitespace], count=-1)
        if not self.require([self.dynamic_use_open], prev_index=_i): return
        self.read([self.whitespace], count=-1)
        self.read([
            self.all_of_group, 
            self.any_of_group, 
            self.exactly_one_of_group, 
            self.most_one_of_group, 
            self.dynamic_use, 
            self.atom
        ], count=-1)
        self.read([self.whitespace], count=-1)
        if not self.require([self.dynamic_use_close], prev_index=_i): return
        self.read([self.whitespace], count=-1)

    def root(self): self.read([
        self.all_of_group, 
        self.any_of_group, 
        self.exactly_one_of_group, 
        self.most_one_of_group, 
        self.dynamic_use, 
        self.atom
    ], count=-1, name="Root")

    def to_tree(self):
        in_tree = lambda a,o: (
            a.data.index_start >= o.data.index_start and a.data.index_end <= o.data.index_end)
        trees = [Tree(parcel) for parcel in self.parcels]
        # Sort by last added if otherwise same. 
        trees.reverse()
        trees.sort(key=lambda t: (t.data.index_start, -t.data.index_end))
        roots = []
        ancestry = []
        for tree in trees:
            while ancestry and not in_tree(tree, ancestry[-1]): ancestry.pop()
            if ancestry:
                ancestry[-1].add_branch(tree)
            else:
                roots.append(tree)
            ancestry.append(tree)
        if not roots:
            return Tree(Parcel(0,0,"",""))
        return roots[0]
