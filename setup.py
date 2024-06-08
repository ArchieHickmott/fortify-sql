from setuptools import setup, find_packages

VERSION = '0.3.1'
DESCRIPTION = 'SQLite extension with a focus on security'
LONG_DESCRIPTION = 'Package friendly for beginner devs that can execute queries on SQLite databases, contains mitigations for SQLinjection'

# Setting up
setup(
    name="fortifysql",
    version=VERSION,
    author="Archie Hickmott",
    author_email="<25hickmar@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['sqlparse'],
    keywords=["sql", "security"],
    classifiers=[
        "Intended Audience :: Beginer Developers",
        "Development Status :: 3 - Alpha",
    ],
    project_urls={  # Optional
        "Bug Reports": "https://github.com/ArchieHickmott/fortify-sql",
    },
)