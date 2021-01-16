from setuptools import setup, find_packages

setup(
    name="Ping Pong",
    version="2021.116",
    author="TPGPL",
    author_email="tpgplofficial@gmail.com",
    license="MIT",
    description="A word-based game made in Python",
    packages=find_packages(),
    install_requires=["pyfiglet"],
    python_requires=">=3.5",
)
