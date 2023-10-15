#!/usr/bin/python3
"""Scan source files and to update translations"""
# pylint: disable=global-statement, exec-used
import os
import sys
import subprocess
from pathlib import Path
import setuptools

# Global variables

exclude_files = ['setup.py',
                 os.path.basename(sys.argv[0]),
                 'build']
project_root=Path(subprocess.getoutput("git rev-parse --show-toplevel"))

po_dir=project_root / "po"

metadata = {}

# Load metadata from setup.py
# First create a mock setup() function
def setup(**kwargs):
    """Retrieve metadata from setup.py
    @returns: metadata as 'metadata'
    """
    global metadata
    metadata = kwargs
setuptools.setup = setup

# Now open setup.py and use setup to store metadata
# in the dictionary metadata

with open(project_root/"setup.py", mode='r', encoding='utf-8') as setup_fd:
    setup_str = setup_fd.read()
exec(setup_str)

os.makedirs(po_dir, exist_ok=True)

# Generate po files
xgettext = ['xgettext', '--indent', '--language=Python',
            '--foreign-use', '--output-dir', str(po_dir),
            f'--package-name={metadata["name"]}',
            f'--package-version={metadata["version"]}',
            f'--default-domain={metadata["name"]}',
            f'--output={metadata["name"]}.pot',
            '--msgid-bugs-address=none@none']
msgmerge = [ 'msgmerge', '--update']
msginit = ['msginit',
           '--no-translator', '--locale=en',
           f'--output-file={str(po_dir)}/en.po',
           f'--input={str(po_dir)}/{metadata["name"]}.pot']

package_path = Path(metadata["name"])

src_files = [ str(src_file.relative_to(project_root)) \
              for src_file in (project_root/package_path).glob('**/*.py') \
              if src_file.name not in exclude_files]

os.chdir(project_root)

try:
    subprocess.run([*xgettext, *src_files], check=True)
except subprocess.CalledProcessError as e:
    print(e)

# Now update existing translations if needed
for po_file in po_dir.glob('*.po'):
    try:
        subprocess.run([*msgmerge, po_file, str(po_dir)+f'/{metadata["name"]}.pot'],
                       check=True)
    except subprocess.CalledProcessError as e:
        print(e)

# Create or update English translation
english_translation = po_dir/'en.po'

if english_translation.exists():
    english_translation.unlink()
try:
    subprocess.run([*msginit],
                   check=True)
except subprocess.CalledProcessError as e:
    print(e)
