from trailrunner import Trailrunner
import pathlib


def main_reduced_concurrency():
    tr = Trailrunner(concurrency=1)
    tr.run([pathlib.Path("./src").resolve()], str)


if __name__ == "__main__":
    main_reduced_concurrency()
