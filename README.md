# dm

Includes:
- the dm and penfold core libraries for coppertop and bones
- Jupyter notebooks and Python code examples using coppertop, bones, dm and penfold

Use this - https://nbviewer.jupyter.org - if github doesn't render properly. 

E.g. https://nbviewer.jupyter.org/github/coppertop-bones/coppertop-libs/tree/main/jupyter/think%20bayes/Ch%201%2C2%2C3%20-%20models.ipynb


<br>

#### Notebook dependencies and coppertop

I have matplotlib, plotnine, numpy, pandas, scipy, pymc3, etc, installed.

Install coppertop-bones-demo via `python -m pip install coppertop-bones-dm`. This also installs coppertop-bones.

Alternatively clone https://github.com/coppertop-bones/coppertop and https://github.com/coppertop-bones/coppertop-libs 
and ensure your PYTHONPATH is set to include the src folders, for example:

```
/Users/david/repos/github/coppertop-bones/coppertop/src 
/Users/david/repos/github/coppertop-bones/coppertop-libs/src
```

Alternatively, you can manually set `sys.path` to include the coppertop-bones/src folder and then at the top of a 
notebook you can do the following:

```
from coppertop.core import ensurePath
'/Users/david/repos/github/coppertop-bones/coppertop-libs/src' >> ensurePath       # <= set this to your path
```

The notebook should be good to go.

