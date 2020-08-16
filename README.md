![PyPI](https://img.shields.io/pypi/v/science-data-structure)
![PyPI](https://img.shields.io/pypi/dm/science-data-structure)
![GitHub last commit](https://img.shields.io/github/last-commit/woutervanveen/science_data_structure)
# Science data structure

This library makes it straight forward to make a tree folder structure for large data-sets. For now it supports numpy arrays only, but I have plans to implement pandas, csv, tab-separated and excel soon. 

The idea behind the library is to make a data-set browse-able with a normal file browser. The components can be rearranged with the use of Python, the terminal or a simple file-browser. 


## Install
Install through pip
```
pip install science-data-structure
```

Manual installation
```
python setup.py install
```

## Command line tools
This library is bundled with command line tools to create a system wide author

```bash
science_data_structure global create author "<name>"
```
or
```bash
science_data_structure global create author
```
and you will be prompted for the name of the author. You only have to run the above commands a single time, the data is stored in a configuration file (the location is dependent of your OS). From the command line you can create a dataset:

```bash
science_data_structure create dataset "<name>" "<description>"
```

The author you have created for you system is added to this dataset. Go into the folder of the dataset and execute:

```bash
science_data_structure list author
```
to view all the authors in this dataset. Alternatively you can list the entire meta file

```bash
science_data_structure list meta
```


## Examples

### Simple data-set
In this simple example a data-set is created, with a single branch `parabola`. In this branch two "leafs" are added `x` and `y`. At the end of the example the data_set is written to disk.

Before we can create a dataset we need to create a meta file containing an author, you can do this with the earlier mentioned command line example above.


```python
import science_data_structure.structures as structures
from pathlib import Path
import numpy

# initialize the empty data-set
dataset = structures.StructuredDataSet.create_dataset(Path("./."),
                                                      "test_set")
        

# add data to the data-set
data_set["parabola"]["x"] = numpy.linspace(-2, 2, 100)
data_set["parabola"]["y"] = data_set["parabola"]["x"].data ** 2

# write the data to disk
data_set.write()
```

### Branch overriding
What will happen when a branch or a leaf is overwritten with another leaf or branch? This example extends the previous example

```python
data_set["parabola"]["x"] = None
```

In this case the variable ~x~ stored in the branch ~parabola~ will be deleted upon the first write. 

