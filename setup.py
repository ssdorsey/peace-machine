from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="wanderingpole",
    version="0.1",
    author="Spencer Dorsey",
    author_email="spencer.dorsey@duke.edu",
    description="A project for tracking polarization in elite political messaging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ssdorsey/peace-machine",
    packages=find_packages(),
    classifiers=[
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
    install_requires=[
        "selenium",
        "pandas", 
        "pandas",
        "numpy",
        "requests",
        "tqdm",
        "regex",
        "transformers",
        "simpletransformers",
        "scipy",
        "scikit-learn",
        "seqeval",
    ],
)