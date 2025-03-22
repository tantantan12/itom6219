from setuptools import setup, find_packages

setup(
    name="itom6219",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas"
    ],
    author="Your Name",
    description="A package for retrieving Twitter user info and tweets using the Twitter API v2",
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
