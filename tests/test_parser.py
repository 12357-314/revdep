from revdep.depvar_parser import EbuildDepvarParser
import pytest

@pytest.mark.parametrize("depvar,catname", [
    ("catname/","catname",),
    ("ABCD","ABCD",),
    ("abcd","abcd",),
    ("0189","0189",),
    ("abc+","abc+",),
    ("def_","def_",),
    ("ghi.","ghi.",),
    ("jkl-","jkl-",),
    ("AB+4","AB+4",),
    ("AB_4","AB_4",),
    ("AB-4","AB-4",),
    ("AB.4","AB.4",),
    ("-abc",""),
    (".abc",""),
    ("+abc",""),
    ("_abc","_abc"),
    ("ab=c","ab"),
    ("a+%d","a+"),
    ("a.&d","a."),
])
def test_category(depvar,catname):
    r"""
    3.1.1 Category names

    A category name may contain any of the characters [A-Za-z0-9+_.-]. It must
    not begin with a hyphen, a dot or a plus sign.

    """
    parser = EbuildDepvarParser(depvar)
    parser.cat_name()
    assert parser.to_tree().data.value == catname

@pytest.mark.parametrize("depvar,pkgname", [
    ("ABCD","ABCD",),
    ("abcd","abcd",),
    ("0189","0189",),
    ("abc+","abc+",),
    ("def_","def_",),
    ("ghi.","ghi",),
    ("jkl-","jkl-",),
    ("AB+4","AB+4",),
    ("AB_4","AB_4",),
    ("AB-4","AB",),
    ("AB-4++","AB-4++",),
    ("AB.4","AB",),
    ("-abc",""),
    (".abc",""),
    ("+abc",""),
    ("_abc","_abc"),
    ("ab=c","ab"),
    ("a+%d","a+"),
    ("a.&d","a"),
])
def test_pkgname(depvar,pkgname):
    r"""
    3.1.2 Package names

    A package name may contain any of the characters [A-Za-z0-9+_-]. It must
    not begin with a hyphen or a plus sign, and must not end in a hyphen
    followed by anything matching the version syntax described in section 3.2.

    Note: A package name does not include the category. The term qualiﬁed
    package name is used where a category/package pair is meant. 

    # EXTRA NOTE: the category requirement is not enforced by the parser here. 

    """
    parser = EbuildDepvarParser(depvar)
    parser.pkg_name()
    assert parser.to_tree().data.value == pkgname

@pytest.mark.parametrize("depvar,slotname", [
    ("slotname","slotname",),
    ("ABCD","ABCD",),
    ("abcd","abcd",),
    ("0189","0189",),
    ("abc+","abc+",),
    ("def_","def_",),
    ("ghi.","ghi.",),
    ("jkl-","jkl-",),
    ("AB+4","AB+4",),
    ("AB_4","AB_4",),
    ("AB-4","AB-4",),
    ("AB.4","AB.4",),
    ("-abc",""),
    (".abc",""),
    ("+abc",""),
    ("_abc","_abc"),
    ("ab=c","ab"),
    ("a+%d","a+"),
    ("a.&d","a."),
])
def test_slotname(depvar,slotname):
    r"""
    3.1.3 Slot names
    A slot name may contain any of the characters [A-Za-z0-9+_.-]. It must not begin with a hyphen,
    a dot or a plus sign.
    """
    parser = EbuildDepvarParser(depvar)
    parser.slot_base()
    assert parser.to_tree().data.value == slotname

@pytest.mark.parametrize("depvar,usename", [
    ("usename?","usename",),
    ("ABCD","ABCD",),
    ("abcd","abcd",),
    ("0189","0189",),
    ("abc+","abc+",),
    ("def_","def_",),
    ("jkl-","jkl-",),
    ("AB+4","AB+4",),
    ("AB_4","AB_4",),
    ("AB@4","AB@4",),
    ("AB-4","AB-4",),
    ("-abc",""),
    (".abc",""),
    ("+abc",""),
    ("_abc",""),
    ("ab.c","ab"),
    ("ab=c","ab"),
    ("a+%d","a+"),
    ("a@%d","a@"),
])
def test_usename(depvar,usename):
    r"""
    3.1.4 USE flag names

    A USE flag name may contain any of the characters [A-Za-z0-9+_@-]. It must
    begin with an alphanumeric character. Underscores should be considered
    reserved for USE_EXPAND, as described in section 11.1.1.

    Note: Usage of the at-sign is deprecated. It was previously required for
    LINGUAS.

    """
    parser = EbuildDepvarParser(depvar)
    parser.use_name()
    assert parser.to_tree().data.value == usename

@pytest.mark.parametrize("depvar,version", [
    ("-0","-0"),
    ("-1.0","-1.0"),
    ("-01.0","-01.0"),
    ("-01.02.03.4.5.6","-01.02.03.4.5.6"),
    ("-1.2a","-1.2a"),
    ("-1.2_alpha","-1.2_alpha"),
    ("-1_pre","-1_pre"),
    ("-1_beta1","-1_beta1"),
    ("-1_beta_alpha1","-1_beta_alpha1"),
    ("-1_beta_alpha","-1_beta_alpha"),
    ("-1_beta_alpha990","-1_beta_alpha990"),
    ("-1_p42","-1_p42"),
    ("-1_p42-r0","-1_p42-r0"),
    ("1.4",""),
])
def test_version(depvar,version):
    r"""
    3.2 Version Specifications

    The package manager must neither impose fixed limits upon the number of
    version components, nor upon the length of any component. Package managers
    should indicate or reject any version that is invalid according to the
    rules below.

    A version starts with the number part, which is in the form
    [0-9]+(\.[0-9]+)* (an unsigned integer, followed by zero or more
    dot-prefixed unsigned integers).

    This may optionally be followed by one of [a-z] (a lowercase letter).

    This may be followed by zero or more of the suffixes _alpha, _beta, _pre,
    _rc or _p, each of which may optionally be followed by an unsigned integer.
    Suffix and integer count as separate version components.

    This may optionally be followed by the suffix -r followed immediately by an
    unsigned integer (the “revision number”). If this suffix is not present, it
    is assumed to be -r0.

    # EXTRA NOTE: the start of a version is marked with a dash '-'. 

    """
    parser = EbuildDepvarParser(depvar)
    parser.version()
    assert parser.to_tree().data.value == version

@pytest.mark.parametrize("depvar,all_of_group", [
    ("()","()"),
    ("( )","( )"),
    ("( ",""),
    (") ",""),
    (" (",""),
    (" )",""),
    (")",""),
    ("(",""),
    ("( ) ","( ) "),
    (" ( ) "," ( ) "),
    (" ( )"," ( )"),
    (" (  atom )"," (  atom )"),
    ("|| ( )",""),
])
def test_all_of_group(depvar,all_of_group):
    r"""
    8.2 Dependency Specification Format

    An all-of group, which consists of an open parenthesis, followed by
    whitespace, followed by one or more of (a dependency item of any kind
    followed by whitespace), followed by a close parenthesis. More formally:
    all-of ::= ’(’ whitespace (item whitespace)+ ’)’. Permitted in all
    specification style variables.

    # EXTRA NOTE: the whitespace requirement is not enforced by the parser
    # here. 

    """
    parser = EbuildDepvarParser(depvar)
    parser.all_of_group()
    assert parser.to_tree().data.value == all_of_group


@pytest.mark.parametrize("depvar,any_of_group", [
    ("|| ()","|| ()"),
    ("|| ( )","|| ( )"),
    ("|| ( ",""),
    ("|| ) ",""),
    ("||  (",""),
    ("||  )",""),
    ("|| )",""),
    ("|| (",""),
    ("|| ( ) ","|| ( ) "),
    ("||  ( ) ","||  ( ) "),
    ("||  ( )","||  ( )"),
    ("( atom )",""),
])
def test_any_of_group(depvar,any_of_group):
    r"""
    8.2 Dependency Specification Format


    An any-of group, which consists of the string ||, followed by whitespace,
    followed by an open parenthesis, followed by whitespace, followed by one or
    more of (a dependency item of any kind followed by whitespace), followed by
    a close parenthesis. More formally: any-of ::= ’||’ whitespace ’(’
    whitespace (item whitespace)+ ’)’. Permitted in DEPEND, BDEPEND, RDEPEND,
    PDEPEND, IDEPEND, LICENSE, REQUIRED_USE.

    # EXTRA NOTE: the whitespace requirement is not enforced by the parser
    # here. 

    """
    parser = EbuildDepvarParser(depvar)
    parser.any_of_group()
    assert parser.to_tree().data.value == any_of_group

@pytest.mark.parametrize("depvar,exactly_one_of_group", [
    ("^^ ()","^^ ()"),
    ("^^ ( )","^^ ( )"),
    ("^^ ( ",""),
    ("^^ ) ",""),
    ("^^  (",""),
    ("^^  )",""),
    ("^^ )",""),
    ("^^ (",""),
    ("^^ ( ) ","^^ ( ) "),
    ("^^  ( ) ","^^  ( ) "),
    ("^^  ( )","^^  ( )"),
    ("( atom )",""),
])
def test_exactly_one_of_group(depvar,exactly_one_of_group):
    r"""
    8.2 Dependency Specification Format

    An exactly-one-of group, which has the same format as the any-of group, but
    begins with the string ^^ instead. Permitted in REQUIRED_USE.

    # EXTRA NOTE: the whitespace requirement is not enforced by the parser
    # here. 

    """
    parser = EbuildDepvarParser(depvar)
    parser.exactly_one_of_group()
    assert parser.to_tree().data.value == exactly_one_of_group

@pytest.mark.parametrize("depvar,most_one_of_group", [
    ("?? ()","?? ()"),
    ("?? ( )","?? ( )"),
    ("?? ( ",""),
    ("?? ) ",""),
    ("??  (",""),
    ("??  )",""),
    ("?? )",""),
    ("?? (",""),
    ("?? ( ) ","?? ( ) "),
    ("??  ( ) ","??  ( ) "),
    ("??  ( )","??  ( )"),
    ("( atom )",""),
])
def test_most_one_of_group(depvar,most_one_of_group):
    r"""
    8.2 Dependency Specification Format

    An at-most-one-of group, which has the same format as the any-of group, but
    begins with the string ?? instead. Permitted in REQUIRED_USE in EAPIs
    listed in table 8.5 as supporting REQUIRED_USE ?? groups.

    # EXTRA NOTE: the whitespace requirement is not enforced by the parser
    # here. 

    """
    parser = EbuildDepvarParser(depvar)
    parser.most_one_of_group()
    assert parser.to_tree().data.value == most_one_of_group

@pytest.mark.parametrize("depvar,dynamic_use", [
    ("use? ()","use? ()"),
    ("use?",""),
    ("!use? ()","!use? ()"),
    ("!use? (   atom )","!use? (   atom )"),
    ("!use?(atom)","!use?(atom)"),
    ("!?",""),
])
def test_dynamic_use(depvar,dynamic_use):
    r"""
    8.2 Dependency Specification Format


    A use-conditional group, which consists of an optional exclamation mark,
    followed by a use flag name, followed by a question mark, followed by
    whitespace, followed by an open paren- thesis, followed by whitespace,
    followed by one or more of (a dependency item of any kind followed by
    whitespace), followed by a close parenthesis. More formally:
    use-conditional ::= ’!’? flag-name ’?’ whitespace ’(’ whitespace (item
    whitespace)+ ’)’. Permitted in all specification style variables.

    # EXTRA NOTE: the whitespace requirement is not enforced by the parser
    # here. 

    """
    parser = EbuildDepvarParser(depvar)
    parser.dynamic_use()
    assert parser.to_tree().data.value == dynamic_use

@pytest.mark.parametrize("depvar,operator", [
    ("<","<"),
    ("<=","<="),
    ("=","="),
    ("~","~"),
    (">=",">="),
    (">",">"),
    ("==","="),
    ("= ","="),
])
def test_package_operator(depvar,operator):
    r"""
    8.3.1 Operators

    The following operators are available:
    - < Strictly less than the specified version.
    - <= Less than or equal to the specified version.
    - = Exactly equal to the specified version. Special exception: if the
      version specified has an asterisk immediately following it, then only the
      given number of version components is used for com- parison, i. e. the
      asterisk acts as a wildcard for any further components. When an asterisk
      is used, the specification must remain valid if the asterisk were
      removed. (An asterisk used with any other operator is illegal.)
    - ~ Equal to the specified version when revision parts are ignored.
    - >= Greater than or equal to the specified version.
    - > Strictly greater than the specified version.

    """
    parser = EbuildDepvarParser(depvar)
    parser.ver_gate()
    assert parser.to_tree().data.value == operator

@pytest.mark.parametrize("depvar,block", [
    ("!","!"),
    ("!!","!!"),
    ("!!!","!!"),
    ("! !","!"),
])
def test_package_block(depvar,block):
    r"""
    8.3.2 Block operator

    If the specification is prefixed with one or two exclamation marks, the
    named dependency is a block rather than a requirement—that is to say, the
    specified package must not be installed. As an exception, weak blocks on
    the package version of the ebuild itself do not count. There are two
    strengths of block: weak and strong. A weak block may be ignored by the
    package manager, so long as any blocked package will be uninstalled later
    on. A strong block must not be ignored. The mapping from one or two
    exclamation marks to strength is described in table 8.9.

    """
    parser = EbuildDepvarParser(depvar)
    parser.block()
    assert parser.to_tree().data.value == block

@pytest.mark.parametrize("depvar,slot", [
    (":",":"),
    (":slot",":slot"),
    (":slot/",":slot/"),
    (":slot/subslot",":slot/subslot"),
    (":=",":="),
    (":*",":*"),
    (":slot=",":slot="),
    (":slot=/subslot",":slot="),
    (":sl+ot",":sl+ot"),
    (":sl_ot",":sl_ot"),
    (":sl.ot",":sl.ot"),
    (":sl-ot",":sl-ot"),
    (":_slot",":_slot"),
    (":+slot",":"),
    (":.slot",":"),
    (":-slot",":"),
    ("slot",""),

])
def test_package_slot(depvar,slot):
    r"""
    8.3.3 Slot dependencies

    A named slot dependency consists of a colon followed by a slot name. A
    specification with a named slot dependency matches only if the slot of the
    matched package is equal to the slot specified. If the slot of the package
    to match cannot be determined (e. g. because it is not a supported EAPI),
    the match is treated as unsuccessful.

    In EAPIs shown in table 8.7 as supporting sub-slots, a slot dependency may
    contain an optional sub-slot part that follows the regular slot and is
    delimited by a / character. An operator slot dependency consists of a colon
    followed by one of the following operators:
    - * Indicates that any slot value is acceptable. In addition, for runtime
      dependencies, indicates that the package will not break if the matched
      package is uninstalled and replaced by a different matching package in a
      different slot.
    - = Indicates that any slot value is acceptable. In addition, for runtime
      dependencies, indicates that the package will break unless a matching
      package with slot and sub-slot equal to the slot and sub-slot of the best
      version installed as a build-time (DEPEND) dependency is available.
    - slot= Indicates that only a specific slot value is acceptable, and
      otherwise behaves identically to the plain equals slot operator.

    To implement the equals slot operator, the package manager will need to
    store the slot/sub-slot pair of the best installed version of the matching
    package. This syntax is only for package manager use and must not be used
    by ebuilds. The package manager may do this by inserting the appropriate
    slot/sub-slot pair between the colon and equals sign when saving the
    package’s dependencies. The sub-slot part must not be omitted here (when
    the SLOT variable omits the sub-slot part, the package is considered to
    have an implicit sub-slot which is equal to the regular slot). Whenever the
    equals slot operator is used in an enabled dependency group, the
    dependencies (DEPEND) must ensure that a matching package is installed at
    build time. It is invalid to use the equals slot operator inside PDEPEND or
    inside any-of dependency specifications.

    3.1.3 Slot names

    A slot name may contain any of the characters [A-Za-z0-9+_.-]. It must not
    begin with a hyphen, a dot or a plus sign.

    """
    parser = EbuildDepvarParser(depvar)
    parser.slot()
    assert parser.to_tree().data.value == slot

@pytest.mark.parametrize("depvar,use_dependency", [
    ("[]","[]"),
])
def test_use_dependency(depvar,use_dependency):
    r"""
    8.3.4 2-style and 4-style USE dependencies

    A 2-style or 4-style use dependency consists of one of the following:
    - [opt] The flag must be enabled.
    - [opt=] The flag must be enabled if the flag is enabled for the package
      with the dependency, or disabled otherwise.
    - [!opt=] The flag must be disabled if the flag is enabled for the package
      with the dependency, or enabled otherwise.
    - [opt?] The flag must be enabled if the flag is enabled for the package
      with the dependency.
    - [!opt?] The flag must be disabled if the use flag is disabled for the
      package with the dependency.
    - [-opt] The flag must be disabled.

    Multiple requirements may be combined using commas, e. g.
    [first,-second,third?]. When multiple requirements are specified, all must
    match for a successful match. In a 4-style use dependency, the flag name
    may immediately be followed by a default specified by either (+) or (-).
    The former indicates that, when applying the use dependency to a package
    that does not have the flag in question in IUSE_REFERENCEABLE, the package
    manager shall behave as if the flag were present and enabled; the latter,
    present and disabled. Unless a 4-style default is specified, it is an error
    for a use dependency to be applied to an ebuild which does not have the
    flag in question in IUSE_REFERENCEABLE. Note: By extension of the above, a
    default that could reference an ebuild using an EAPI not support- ing
    profile IUSE injections cannot rely upon any particular behaviour for flags
    that would not have to be part of IUSE. It is an error for an ebuild to use
    a conditional use dependency when that ebuild does not have the flag in
    IUSE_EFFECTIVE.

    """
    parser = EbuildDepvarParser(depvar)
    parser.slot()
    assert parser.to_tree().data.value == use_dependency
