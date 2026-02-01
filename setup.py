"""
Setup configuration for SysML v2 Parser
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sysml-v2-parser",
    version="0.1.0",
    author="SysML IDE Development",
    description="A comprehensive Python parser for reading and writing SysML v2 models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/sysml-v2-parser",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="sysml systems-modeling uml",
    project_urls={
        "Bug Reports": "https://github.com/example/sysml-v2-parser/issues",
        "Source": "https://github.com/example/sysml-v2-parser",
    },
)
