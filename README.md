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

Simply generating the set of paths to walk takes about 8 seconds:

```
$ time python walk_paths.py
python walk_paths.py  7.59s user 3.50s system 124% cpu 8.935 total
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

If we configure trailrunner to use a single process, it runs in under a second.

```
$ time python walk_paths_single.py
python walk_paths_single.py  0.09s user 0.04s system 37% cpu 0.347 total
```

Once the paths are collected, if there is more than one, trailrunner is again
used via `run_iter` which does, indeed, speed things up dispatching over multiple
processes.
