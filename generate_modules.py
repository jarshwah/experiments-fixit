import os


def generate_modules(root_dir, levels, letters):
    if levels == 0:
        return

    if levels == 1:
        letters = sub_level_letters

    for letter in letters:
        module_dir = os.path.join(root_dir, letter)
        os.makedirs(module_dir, exist_ok=True)
        init_file = os.path.join(module_dir, "__init__.py")
        with open(init_file, "w") as f:
            f.write("")

        generate_modules(module_dir, levels - 1, letters)


root_dir = "./src"
top_level_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
sub_level_letters = ["a", "b", "c"]

generate_modules(root_dir, 5, top_level_letters)
