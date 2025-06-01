import re

def prompt_pkgname(pkgnames, opts=None):
    """
    Prompt for a package name from a given list of package names. Provide
    options if input matches multiple pkgnames. 

    """
    if opts is None:
        opts = []
    elif opts:
        print("Input option number.")
    else:
        print("Input atom name (regex), returns matching atoms.")

    for i,opt in enumerate(opts):
        print(i,opt)
    user_input = input(">>> ")
    try:
        user_regex = re.compile(user_input)
    except re.error:
        print("Invalid regex. Reprompting.")
        return prompt_pkgname()

    if opts and user_input.isdigit(): return list(opts)[int(user_input)]
    elif opts: return prompt_pkgname(pkgnames, opts)

    for pkgname in pkgnames:
        if user_regex.search(pkgname): opts.append(pkgname)

    opts = sorted(list(opts))
    if len(opts) == 1:
        return opts[0]
    return prompt_pkgname(pkgnames, opts)


