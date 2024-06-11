from setuptools import setup, find_packages

VERSION = '0.3.2'
DESCRIPTION = 'SQLite extension with a focus on security'
long_description = ""
with open("README.md", 'r') as readme:
    long_description = readme.read()

# Setting up
setup(
    name="fortifysql",
    version=VERSION,
    author="Archie Hickmott",
    author_email="25hickmar@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['sqlparse'],
    keywords=["sql", "security"],
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
    ],
    project_urls={  # Optional
        "Bug Reports": "https://github.com/ArchieHickmott/fortify-sql",
        "Documentation": "https://archiehickmott.github.io/fortify-sql/"
    },
)