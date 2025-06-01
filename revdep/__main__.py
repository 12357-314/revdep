#!/usr/bin/env python

from pathlib import Path
from .atom_causal_chain import AtomCausalChain
from .user_interface import prompt_pkgname
from .rdep_chain import SystemReverseDependencyChain

def main():
    # emerge --pretend --verbose --emptytree --depclean > emerge_deps.txt
    # portageq metadata / ebuild <PKG> DEPEND

    emerge_rdeps_filename = "./emerge_rdeps.txt"
    emerge_rdeps_filepath = Path(__file__).parent / emerge_rdeps_filename
    emerge_rdeps_file = open(emerge_rdeps_filepath)
    emerge_rdeps_output = emerge_rdeps_file.read()
    rdep_chain = SystemReverseDependencyChain(emerge_rdeps_output)

    pkgname = prompt_pkgname(pkgnames=rdep_chain.dependees_by_dependency.keys())
    causal_chain = AtomCausalChain(rdep_chain=rdep_chain, pkgname=pkgname)
    links = causal_chain.causal_chain
    for link in links:
        print(link)

if __name__ == '__main__':
    main()
