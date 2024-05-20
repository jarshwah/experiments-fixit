import sys
import pathlib
from fixit import cli
from fixit import api
from fixit.ftypes import Options
from fixit.api import fixit_paths, print_result
from trailrunner import Trailrunner
from concurrent.futures import ThreadPoolExecutor

def main():
    Trailrunner.DEFAULT_EXECUTOR = ThreadPoolExecutor
    #api.trailrunner.walk = new_walk
    options = Options(debug=None, config_file=None, tags=None, rules=set())
    paths = [pathlib.Path("./src").resolve()]
    exit_code = 0
    visited = set()
    dirty = set()
    autofixes = 0
    cwd = pathlib.Path.cwd()
    for result in fixit_paths(paths, options=options, parallel=True):
        visited.add(result.path)

        if print_result(result, show_diff=False, cwd=cwd):
            dirty.add(result.path)
            if result.violation:
                exit_code |= 1
                if result.violation.autofixable:
                    autofixes += 1
            if result.error:
                exit_code |= 2

    cli.splash(visited, dirty, autofixes)
    sys.exit(exit_code)


def new_walk(path: pathlib.Path, *, excludes=None):
    runner = Trailrunner(concurrency=1)
    return runner.walk(path, excludes=excludes)


if __name__ == "__main__":
    main()
