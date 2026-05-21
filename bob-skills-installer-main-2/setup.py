from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bob-skills-installer",
    version="1.0.0",
    author="Wei Cao",
    author_email="weicao@ca.ibm.com",
    description="CLI tool to install and manage Bob AI skills",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.ibm.com/weicao/bob-skills-installer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
        "gitpython>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "bob-skills=bob_installer.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "bob_installer": ["templates/*.md"],
    },
)