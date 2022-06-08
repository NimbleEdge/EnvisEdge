# Contributing Guidelines

We are always eager to work with new contributors, engage with them and build exciting technologies. 
This library allows you to train your recommendation models on user devices and is the core SDK that gets deployed across millions of users.

Here are some important resources to get ready for contributing:

  * [Introduction to Federated Learning](https://arxiv.org/abs/1602.05629) gives a brief introduction to the space and sets the basic terminology
  * [Deploying Federated Learning at scale](https://arxiv.org/abs/1902.01046) explains how a scalable FL system can be built 
  * [NimbleEdge Tutorials](./docs) is an overview of the library and our architecture
  
There are lot of ways in which you can help us!!

## Do you want to contribute to code ??
Make sure you follow satisfy all these criteria before making your pr :
* Your code contributions can be in lot of ways like filing bugs,improving existing code etc.
* We request you to use the autopep-8 reformat **on the VCS changes** before the final commit.
* We expect you to ensure indentation consistency.
* You must follow Google code style.
* You must follow numpy style guides [here](https://numpydoc.readthedocs.io/en/latest/format.html)as well.
* You must not forget to include documentation of the code you are contributing to when adding a new module/feature to EnvisEdge.
* Your pull request must pass all the checks and has no conflicts.
* And,your pull request must include detailed commit messages along with title.

## Do you want to test our code?? 

The library is in the initial stages and we would like to build a complete suite of tests. Till then we can only test functionality.If you are someone interested in testing our code please head towards our [discord](https://nimbleedge.ai/discord) channel to have a inital conversation with project maintainers.

## Are you someone interested in writing documentation ???
We already have a small group of people who are building working regulary to improve docs.We suggest you to thoroughly follow our docs and look for points where the doc needs improvemnets.The documentation source is stored under the [docs](./docs) directory and written in [reStructuredText format](http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html).

You can build the documentation in HTML format locally:

```bash
cd docs
make html
```

HTML files are generated under `build/html` directory. Open the `index.html` file in your browser to view the documentation.

The design of the documentation is inspired from [Mlflow](https://mlflow.org/docs/latest/).

## Are you willing to help us in improving NimbleEdge Website ??
Our community is highly in need of web developers open source contributors who can work on the minor changes we expected from the website.We already have few open issues in the [issues](https://github.com/NimbleEdge/EnvisEdge/issues) section with #web tag.You can check it out and reach out to mainatiners in [discord](https://nimbleedge.ai/discord) for futher clarification.

## Do you love graphic or UI/UX designing ??
We are open to these contributions as well.We will be glad if someone comes up with a new UI/Ux design for our website so that we can work accordingly and make it look more attractive and user friednly.

## Do you really love marketing ??
We are social, in every sense of the word. And we love nothing more than building new relationships.To build relationships,we need people who
can help us in reaching to new contributors and spread a word about our community.

## Is there any other way to contribute??
yayy!! contributions types are not only restricted to above listed .You can do it lot more ways.You can train new contributors in the community,open good first issues, speak about nimbleedge in meetups,conferences and standups,you can spread a word about our community and lot more!!
If you want to get involved in some other ways,please dont hestitate to reach out to us! 
## Submitting Pull Requests

Please send a [GitHub Pull Request to EnvisEdge](https://github.com/NimbleEdge/EnvisEdge) with a clear list of what you've done (read more about [pull requests](http://help.github.com/pull-requests/)). 
Please Squash your commits into one before sending the pull request. 

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."

