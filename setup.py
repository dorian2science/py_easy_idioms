from setuptools import setup, find_packages
import os
setup(
    name="py_easy_idioms",
    version=0.1,
    description="easy idioms",
    long_description="Some utilities to learn languages quickly",
    long_description_content_type="text/markdown",
    author="Dorian Drevon",
    author_email="drevondorian@gmail.com",
    url="coming",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "conf": ["conf/*"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "ipykernel"
            ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
