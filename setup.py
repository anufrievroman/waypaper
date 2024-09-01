from pathlib import Path
import setuptools

setup_dir = Path(__file__).resolve().parent

setuptools.setup(
    name='waypaper',
    author='Roman Anufriev',
    author_email='anufriev.roman@protonmail.com',
    url='https://github.com/anufrievroman/waypaper',
    description='GUI wallpaper setter for Wayland',
    long_description=Path(setup_dir, 'README.md').open().read(),
    long_description_content_type='text/markdown',
    license='GPL',
    entry_points={
        "gui_scripts": [
            "waypaper = waypaper.__main__:run"
        ]
    },
    install_requires=["PyGObject", "importlib_metadata", "platformdirs", "Pillow"],
    version='2.3',
    python_requires='>3.9',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    packages=["waypaper"],
    package_data={
        'waypaper': ['data/waypaper.desktop', 'data/waypaper.svg']
    },
    include_package_data=True,
    data_files=[
        ('share/icons/hicolor/scalable/apps',
         ['data/waypaper.svg']
         ),
        ('share/applications',
         ['data/waypaper.desktop']
         ),
        ('share/man/man1',
         ['data/waypaper.1.gz']
         ),
    ],
)
