import sys
import pathlib
from fixit import cli
from fixit import api
from fixit.ftypes import Options, Result
from fixit.api import fixit_paths, print_result
import trailrunner


def main():
    options = Options(debug=None, config_file=None, tags=None, rules=set())
    paths = [pathlib.Path("./src").resolve()]
    exit_code = 0
    visited = set()
    dirty = set()
    autofixes = 0
    cwd = pathlib.Path.cwd()
    for idx, result in enumerate(fixit_paths(paths, options=options, parallel=False)):
        if result is None:
            result = Result(path=paths[0] / f"path{idx}.py", violation=None, error=None)
        visited.add(result.path)

        if print_result(result, show_diff=False):
            dirty.add(result.path)
            if result.violation:
                exit_code |= 1
                if result.violation.autofixable:
                    autofixes += 1
            if result.error:
                exit_code |= 2

    cli.splash(visited, dirty, autofixes)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
