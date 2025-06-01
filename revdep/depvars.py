import subprocess

depvar_names="DEPEND RDEPEND BDEPEND IDEPEND PDEPEND"

def get_depvars(pkgname):
    command = f"portageq metadata / ebuild {pkgname} {depvar_names}"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, text=True)
    stdout, stderr = process.communicate()
    depvars = stdout.split("\n")
    return depvars 
