from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()


setup(
    name="science_data_structure",
    version="0.0.3",
    author="Wouter van Veen",
    description="Structure for large data-sets in science",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/woutervanveen/science_data_structure",
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
    entry_points='''
    [console_scripts]
    science_data_structure=science_data_structure.tools.manage:manage
    '''
)


