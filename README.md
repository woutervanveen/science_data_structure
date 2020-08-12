![PyPI](https://img.shields.io/pypi/v/science-data-structure)

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
## Examples

### Simple data-set
In this simple example a data-set is created, with a single branch `parabola`. In this branch two "leafs" are added `x` and `y`. At the end of the example the data_set is written to disk.

Before we can create a dataset we need to create a meta file containing an author


```python
import science_data_structure.structures as structures
import science_data_structure.authors as authors
from pathlib import Path
import numpy

# create author and meta file
author = authors.Author("Author Name")
meta = Meta.create_meta

author = Author.create_author("Test_author")
meta = Meta.create_top_level_meta(None, author)

# initialize the empty data-set
dataset = structures.StructuredDataSet.create_dataset(Path("./."),
                                                      "test_set",
                                                      meta)
        

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

