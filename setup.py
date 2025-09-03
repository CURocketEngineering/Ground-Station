from setuptools import setup, find_packages

setup(
    name="cure-ground",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pyserial>=3.5",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "tqdm>=4.65.0",
        "kaleido>=0.2.1",
        "questionary",
        "plotly",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "cure-ground=cure_ground.cli.main:main",
        ],
    },
    author="Clemson University Rocket Engineering",
    author_email="",
    description="CURE Ground Station Software",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CURocketEngineering/Ground-Station",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)