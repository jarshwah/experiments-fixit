# Experiment: Fixit

This repo is an attempt to profile performance issues with fixit on large projects.

Even when we have a rule that does nothing but provide a visit_Module that does
nothing, the runtime of fixit is still incredibly slow, showing that the rules
themselves aren't the bottleneck, but the runtime itself.

To run this experiment, setup a virtual environment, install the dependencies,
and run fixit lint:

```
$ pyenv virtualenv 3.11 experiment-fixit
$ pyenv local experiment-fixit
$ pip install -r requirements.txt
$ time fixit lint src
```

On my Macbook Pro M2, this takes approximately 40 seconds to run, with all cores
of my CPU pegged to 100%:

```
$ time fixit lint src
🧼 41111 files clean 🧼
fixit lint src  146.51s user 22.35s system 419% cpu 40.255 total
```

A somewhat unfair comparison is to [ruff](https://docs.astral.sh/ruff/) which is
entirely written in Rust and does not support custom rules written in Python, which
completes in 1 second:

```
$ time ruff check src
All checks passed!
ruff check src  0.36s user 1.71s system 170% cpu 1.213 total
```

## Why is fixit slow?

Digging into this some more, I wanted to try and narrow down what could be the
primary bottlenecks. This section will be updated as I learn more.


### Trailrunner

Fixit uses a package called `trailrunner` to walk the tree of files and execute
a function against each path found. It uses a process pool to parallelize this
part of the process.

Simply generating the set of paths to walk takes about 6 seconds:

```
$ time python walk_paths.py
python walk_paths.py  3.99s user 2.25s system 96% cpu 6.448 total
```

A naive implementation that uses `os.walk` to generate the paths takes about 1.5
seconds:

```
$ time python walk_paths_naive.py
Files: 41111
python walk_paths_naive.py  0.19s user 0.92s system 84% cpu 1.304 total
```

But note that the naive version does not do any regex filtering or gitignore
filtering, so it's not an exact comparison.

Once the paths are collected, if there is more than one, trailrunner is again
used via `run_iter` which does, indeed, speed things up dispatching over multiple
processes.


### Generate Config

A new configuration is generated for each file being linted in `generate_config`.
There should be a relatively (compared to the number of linted files) small number
of possible configs. If these could be cached, we might see a speed up. Let's see
how long it takes to generate a config-per-file:

```
$ time python generate_configs.py
41111 configs generated
python generate_configs.py  12.23s user 4.90s system 88% cpu 19.339 total
```

About 19 seconds, including the naive os.walk of the tree-of-modules.

It seems we've accounted for nearly half of the total runtime when we just consider
the file discovery and config generation mechanisms?

#### Patching Generate Config

Editing `fixit.config.generate_config` to use a global and a single instance of
the root config only saves about 6 seconds:

```
# with cache/global
$ time python fixit_single.py
🧼 41111 files clean 🧼
python fixit_single.py  166.77s user 14.13s system 549% cpu 32.934 total

# without cache/global
$ time python fixit_single.py
🧼 41111 files clean 🧼
python fixit_single.py  188.02s user 18.41s system 525% cpu 39.263 total
```

Which suggests that this isn't a bottleneck either. However, note that total user
time spent is about 22s faster. Worth improving, but not the main cause.

### Collect Rules

`fixit_bytes` does the actual linting. Before though, it generates a list of rules
to be applied. Applying a similar patch as above to cache the set of rules into
a global variable (assuming only one config needs to be applied), we shave off
another 7 seconds of total runtime:

```
$ time python fixit_single.py
🧼 41111 files clean 🧼
python fixit_single.py  127.25s user 7.48s system 530% cpu 25.379 total
```

Note that this includes the changes to both config and collect rules caching.


### Multiprocessing Pool

Multiprocessing is relatively slow in Python, because it has to dispatch tasks
to each sub-process, including serializing and deserializing the data. One mechanism
available to help improve runtime is to chunk the data.

If we patch `fixit.api.run_iter` to use `pool.imap_unordered` with a chunksize, we see
some small improvement (note that caching the config + rules above is enabled):

```
$ time python fixit_single.py
🧼 41111 files clean 🧼
python fixit_single.py  120.02s user 5.79s system 532% cpu 23.636 total
```

Increasing the chunksize above 1000 gives us worse performance. The sweet spot
seems to be around 10 - 100.

```python
def fixit_file_multiprocessing(
    paths: Sequence[Path], autofix: bool, options: Optional[Options] = None
) -> Generator[Result, bool, None]:
    with multiprocessing.Pool() as pool:
        for results in pool.imap_unordered(
            partial(_fixit_file_wrapper, autofix=autofix, options=options),
            paths,
            chunksize=10,
        ):
            yield from results
```

#### Deserialization

If the cost of deserializing the results is high, we should expect to see a speedup
if we return no results (or smaller data). Unfortunately, we see no such gain. We
can somewhat confirm this with pickle locally:

```
import pickle
from fixit.ftypes import Result
r = Result(path="./asfdsa", violation=None)
%timeit pickle.dumps(r)
1.03 µs ± 6.05 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

%timeit pickle.dumps(None)
168 ns ± 2.38 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)
```

Pickling None is about 10 times faster than pickling a Result, but we're still
talking about microseconds per path.


### Fixit Bytes

Skipping the LintRunner altogether by yielding non-violation results right after
collecting the rules, we see that the runtime is about 8 seconds. Running without
parallelism on we get about 9 seconds.

This suggests that fixit_bytes is the primary bottleneck that needs investigation.
