import os

def yield_python_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def main():
    files = list(yield_python_files("./src"))
    print(f"Files: {len(files)}")


if __name__ == "__main__":
    main()
