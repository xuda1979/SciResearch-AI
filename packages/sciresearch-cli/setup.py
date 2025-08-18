from setuptools import find_packages, setup

setup(
    name="sciresearch-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sciresearch-providers-openai",
    ],
    entry_points={
        "console_scripts": [
            "sciresearch-ai = sciresearch_cli.main:main",
        ],
    },
)
