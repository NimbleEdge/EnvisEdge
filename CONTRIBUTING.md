# Contributing Guidelines

We are always eager to work with new contributors, engage with them and build exciting technologies. 
This library allows you to train your recommendation models on user devices and is the core SDK that gets deployed across millions of users.

Here are some important resources to get ready for contributing:

  * [Introduction to Federated Learning](https://arxiv.org/abs/1602.05629) gives a brief introduction to the space and sets the basic terminology
  * [Deploying Federated Learning at scale](https://arxiv.org/abs/1902.01046) explains how a scalable FL system can be built 
  * [NimbleEdge Tutorials](./docs) is an overview of the library and our architecture
  
## Testing 

The library is in the initial stages and we would like to build a complete suite of tests. Till then we can only test functionality 

## Documentation

When adding a new module/feature to EnvisEdge, please make sure to add the documentation for it. The documentation source is stored under the [docs](./docs) directory and written in [reStructuredText format](http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html).

You can build the documentation in HTML format locally:

```bash
cd docs
make html
```

HTML files are generated under `build/html` directory. Open the `index.html` file in your browser to view the documentation.

The design of the documentation is inspired from [Mlflow](https://mlflow.org/docs/latest/).


## Submitting Pull Requests

Please send a [GitHub Pull Request to EnvisEdge](https://github.com/NimbleEdge/EnvisEdge) with a clear list of what you've done (read more about [pull requests](http://help.github.com/pull-requests/)). 
Please Squash your commits into one before sending the pull request. 

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."

## Coding conventions

* Please use the autopep-8 reformat **on the VCS changes** before the final commit.
* Ensure indentation consistency
* Follow Google code style
* Please follow numpy style guides [here](https://numpydoc.readthedocs.io/en/latest/format.html).
