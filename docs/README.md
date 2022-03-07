Guidelines for docs:
--------------------

If there is a new file in `fedrec` module. Please add it to the docs by
 
```
   $ pwd
   ../EnvisEdge

   $ cd docs
   $ sphinx-apidoc -o docs/source/fedrec/ fedrec  
   $ make clean; make html
```

Otherwise, please update the existing docs by:

```
   $ pwd
   ../EnvisEdge

   $ cd docs
   $ make clean; make html
```
 