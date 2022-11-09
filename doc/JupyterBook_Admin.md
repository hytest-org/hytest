# Jupyter-Book Administration Notes

The documents (markdown and executable notebooks) in this repo are meant to be the source material from
which a _static_ website can be built using [jupyter book](https://jupyterbook.org/en/stable/intro.html).

## Build Notes

* JB will execute notebooks in order to render them and extract an HTML representation.
* The execution environment must, therefore, contain all of the packages and compute resources needed
  for that to succeed (cluster hardware, S3 write access, python modules/libraries, etc).
* The environment must also contain the jupyter-book package. This package is not needed for any
  of the notebooks to run; it is only needed for the build process.  For this reason, it is not included
  in the `HyTEST.yml` environment file.
* JB is based on [Sphinx](https://jupyterbook.org/en/stable/explain/sphinx.html) as the documentation engine.
  Sphinx uses templates to establish styling and
  features.  The Project Pythia Cookbook style is the basis of the HyTEST book style.
* Styling templates are installed as python packages, usin conda or pip.  Much like the jupyter-book
  package itself, `sphinx_pythia_theme` must be installed.  This package is also not included in the
  `HyTEST.yml` environment file.
* Jupyter Book only builds the static website; it does not publish to a server.
  - How to publish depends on where you want the docs to go.
  - The default for this repo is to use 'GitHub Pages' as the deployment.
  - Publication to GH Pages is made easier with `ghp-import`.  This is yet another of those packages that
    your build environment will need, but is not included in the `HyTEST.yml` file (because notebook users
    don't need it).
* To ease the jupyter-book command invocation, a `Makefile` is included, with simplified targets defined:
  - `make book` -- builds the static website to local disk.  Use your browser to open a `file://path/` URL
    to preview the built site.
  - `make clean` -- removes all cached and previously built HTML files.
  - `make publish` -- automates the publication to GH Pages once the static site is built.
* `make` is not installed as standard in many Linux environments. If you don't have access to it, then you
  may have to invoke those build or publish commands manually.
* Automation -- In an ideal world, we would have an automatic system to rebuild the jupyterbook whenever
  changes to the documentation are pushed to the `main` branch of the repo. This is limited by the need
  of our notebooks to execute on a clustered environment with access to specific S3 buckets. As yet, that
  environemnt is not built which will let us do that, so these books must be built by hand.

## Document Features

JupyterBook is built on Sphinx, which understands many types of files and can format complex layouts. The
base for most of this repo is markdown.  But it also understands `rST` files (restructured text). The
variant of `rST` is [MyST](https://jupyterbook.org/en/stable/reference/cheatsheet.html).  MyST document
styling features are available within both markdown and notebook documents.

Of particular interest for this book build, the following directives can be used to enhance a notebook's appearance:

### Sidebars

<pre>
:::{sidebar} sidebar title here
sidebar text goes here...
:::
</pre>
The specified text will appear as a gloss/sidebar in the right margin. See the examples [here](https://jupyterbook.org/en/stable/content/layout.html#sidebar-content)

### Admonitions

<pre>
:::{admonition}
text goes here
:::
Admonitions are highlighted block quotes, with a colorful headline bar.  These are useful to highlight text
of particular importance.  There are different styles of admonition (note, warning, error, tip, etc).  See
the [cheat sheet]() for examples.
</pre>

### Dropdowns

These are admonitions with a 'collapsable' feature. See <https://jupyterbook.org/en/stable/content/components.html#dropdowns>
<pre>
:::{dropdown}

:::
</pre>