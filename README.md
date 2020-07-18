
![PyPI - Downloads](https://img.shields.io/pypi/dm/science-data-structure)
# Science data structure

This library makes it straight forward to make a tree folder structure for large data-sets. For now it supports numpy arrays only, but I have plans to implement pandas, csv, tab-separated and excel soon. 

The idea behind the library is to make a data-set browse-able with a normal file browser. The components can be rearranged with the use of Python, the terminal or a simple file-browser. 


## Install
Install through pip
```
pip install science_data_structure
```

## Examples

### Simple data-set
In this simple example a data-set is created, with a single branch `parabola`. In this branch two "leafs" are added `x` and `y`. At the end of the example the data_set is written to disk.


```python
import science_data_structure.structures as structures
from pathlib import Path
import numpy


# Initialze an empty data-set
data_set = structures.StructuredDataSet(Path("./"), "example", {})

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

The above code will try to delete the variable `x`, however it will raise a `PermissionError`. This protection method is in place to make sure that data from a data-set is not simple overwritten. The user must explicitly ask to override the branch or leaf. In the case above, a simple solution will be:

``` python
data_set.overwrite = True
data_set["parabola"]["x"] = None
data_set.overwrite = False

data_set.write(exists_ok=True)
```

The last protection in place is the `exist_ok` variable in the `data_set.write()` function. This makes sure to not accidentally override an existing data-set.

### Reading an existing data-set
Often you want to read a data-set, use it, adapt it, and write the results back to disk. The following script does just that. 


```python
import science_data_structure.structures as structures
from pathlib import Path
import numpy


# Initialze an empty data-set
data_set = structures.StructuredDataSet.read(Path("./example.struct"))

a = 2
b = 4
data_set["linear"]["x"] = numpy.linspace(-2, 2, 100)
data_set["linear"]["y"] = data_set["linear"]["x"] * a + b

data_set.write(exists_ok=True)
```

Note that we again must set the `exists_ok = True`, otherwise the data-set cannot be written to disk. 
