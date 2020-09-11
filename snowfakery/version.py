from pathlib import Path


# TODO: when Python 3.6 is irrelevant, make this lazy:

# https://www.python.org/dev/peps/pep-0562/

version_file = Path(__file__).parent / "version.txt"
with version_file.open() as f:
    version = f.read()
