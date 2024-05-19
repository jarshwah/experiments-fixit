from trailrunner import walk_and_run as run
import pathlib

def main():
    run([pathlib.Path("./src").resolve()], str)


if __name__ == "__main__":
    main()
