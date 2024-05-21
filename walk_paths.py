from trailrunner import walk
import pathlib


def main():
    files = list(walk(pathlib.Path("./src")))
    print(f"Files: {len(files)}")

if __name__ == "__main__":
    main()
