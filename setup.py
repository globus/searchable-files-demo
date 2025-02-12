from setuptools import find_packages, setup

REQUIREMENTS = [
    "click<8",
    "globus-sdk<3",
    "globus-sdk-tokenstorage==0.4.0",
    "ruamel.yaml==0.17.4",
    "identify<2.0",
]

setup(
    name="searchable-files",
    version="0.0.1",
    author="Stephen Rosen",
    author_email="sirosen@globus.org",
    url="https://github.com/globus/searchable-files-demo",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["searchable-files = searchable_files:cli"]},
    install_requires=REQUIREMENTS,
    license="Apache 2.0",
    python_requires=">=3.6",
)
