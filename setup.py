from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'fast development of python applications using SQLite3'
LONG_DESCRIPTION = 'This package contains functionality to peform all basic CRUD operations using SQLite3.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="quicksqlite", 
        version=VERSION,
        author="Jason Dsouza",
        author_email="<youremail@email.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)