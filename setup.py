import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dc-cli",
    version="0.0.7",
    author="Malte Soennichsen",
    author_email="malte-soe@users.noreply.github.com",
    description="Dataclass command line interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/malte-soe/dataclass-cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
