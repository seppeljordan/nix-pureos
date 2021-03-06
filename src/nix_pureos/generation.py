import os

from nix_pureos.paths import GENERATIONS_DIR


def no_handler(old, new):
    pass


class Generations(object):
    def __init__(self, generation_prefix, generation_switch_handler=no_handler):
        self.current_generation = None
        self.generation_prefix = generation_prefix + '-'
        self.generation_switch_handler = generation_switch_handler
        generations_files = self.get_sorted_generation_files()
        if len(generations_files) > 0:
            latest_generation_file = generations_files[-1]
            self.current_generation = int(latest_generation_file.replace(
                self.generation_prefix,
                ''
            ))

    def is_generation_file(self, path):
        return path.startswith(GENERATIONS_DIR + '/' + self.generation_prefix)

    def unlink_files(self, installation_dir):
        installation_contents = map(
            lambda x: installation_dir + '/' + x,
            os.listdir(installation_dir)
        )
        installation_symlinks = filter(
            lambda p: os.path.islink(p) and self.is_generation_file(os.readlink(p)),
            installation_contents
        )
        for path in installation_symlinks:
            absolute_path = os.path.join(installation_dir, path)
            os.remove(absolute_path)

    def link_files(self, installation_dir, generation_number):
        generation_path = self.get_generation_path(generation_number)
        generation_files = os.listdir(generation_path)
        for path in generation_files:
            os.symlink(
                os.path.join(generation_path, path),
                os.path.join(installation_dir, path)
            )


    def install_current_generation(self, installation_dir):
        self.unlink_files(installation_dir)
        self.link_files(installation_dir, self.current_generation)
        self.generation_switch_handler(
            self.get_last_generation_path(),
            self.get_current_generation_path()
        )

    def get_sorted_generation_files(self):
        return list(
            sorted(
                filter(
                    lambda file: file.startswith(self.generation_prefix),
                    os.listdir(GENERATIONS_DIR)
                ),
                key=lambda x: int(x.replace(self.generation_prefix, '')),
            )
        )

    def create_new_generation(self, file_generator):
        """file_generator is a function that only takes one argument: a path"""
        next_generation = self.current_generation + 1 if self.current_generation is not None else 0
        next_generation_filename = GENERATIONS_DIR + '/' + self.generation_prefix + str(next_generation)
        file_generator(next_generation_filename)
        self.current_generation = next_generation

        return next_generation_filename

    def get_generation_path(self, n):
        return GENERATIONS_DIR + '/' + self.generation_prefix + str(n)

    def get_last_generation_path(self):
        generation_files = self.get_sorted_generation_files()
        if len(generation_files) < 2:
            return None
        else:
            return GENERATIONS_DIR + '/' + generation_files[-2]

    def get_current_generation_path(self):
        generation_files = self.get_sorted_generation_files()
        if len(generation_files) < 1:
            return None
        else:
            return GENERATIONS_DIR + '/' + generation_files[-1]

    def delete_old_generations(self):
        all_generations = self.get_sorted_generation_files()
        for generation in all_generations[:-1]:
            path = os.path.join(GENERATIONS_DIR, generation)
            print("Removing path '{path}'".format(path=path))
            os.remove(path)
