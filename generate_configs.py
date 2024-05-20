import pathlib
import os
from fixit.api import generate_config


def yield_python_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)


def main():
    configs = []
    for file_path in yield_python_files("./src"):
        path = pathlib.Path(file_path).resolve()
        configs.append(generate_config(path, options=None))
    print(f"{len(configs)} configs generated")


if __name__ == "__main__":
    main()
