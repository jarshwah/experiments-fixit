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
