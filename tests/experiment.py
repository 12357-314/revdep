from revdep.depvar_parser import EbuildDepvarParser

depvar = ":"
parser = EbuildDepvarParser(depvar)
parser.block()
print(parser.to_tree())
print(parser.to_tree().data.value)
