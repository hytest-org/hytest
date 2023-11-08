# Jupyter-Book Administration Notes

The documents (markdown and executable notebooks) in this repo are meant to be the source material from
which a _static_ website can be built using [jupyter book](https://jupyterbook.org/en/stable/intro.html).

## Build Overview

* JB will execute notebooks in order to render them and extract an HTML representation.
* The execution environment must, therefore, contain all of the packages and compute resources needed
  for that to succeed (cluster hardware, S3 write access, python modules/libraries, etc).
* The environment must also contain the jupyter-book package. This package is not needed for any
  of the notebooks to run; it is only needed for the build process.  For this reason, it is not included
  in the `HyTEST.yml` environment file. You should [install jupyter-book](https://pypi.org/project/jupyter-book/) to your hytest conda environment if you would like to build the JupyterBook
* JB is based on [Sphinx](https://jupyterbook.org/en/stable/explain/sphinx.html) as the documentation engine.
  Sphinx uses templates to establish styling and
  features. 
* Jupyter Book only builds the static website; it does not publish to a server.
  - How to publish depends on where you want the docs to go.
  - The default for this repo is to use 'GitHub Pages' as the deployment.
  - Publication to GH Pages is made easier with [`ghp-import`](https://pypi.org/project/ghp-import/).  This is yet another of those packages that
    your build environment will need, but is not included in the `HyTEST.yml` file (because notebook users
    don't need it).


## Publication Workflow

This is a set of notes to guide the publication workflow for this Jupyterbook project.
The notes are intended for the project maintainers and contributors, not really for the end-users.
(Although there isn't anything here that is secret or private, just not relevant to the subject
matter in the notebooks).

### Platform

These notebooks are written to execute on a cloud platform, specifically the `nebari` configuration
at `https://nebari.esipfed.org/`. It should be reasonably easy to adapt these to other cloud platforms,
or even HPC systems -- but that is not the focus of this project.

### Data Access

We read from and write to S3 object storage for most workflows. If the user wants to run the notebooks
for themselves, they'll need to sort out their own access to do this.  And likely will need to adjust
path strings throughout the notebooks to ensure they are pointing to a location where they have write
access.

### Conda Environment

The environment for this project is defined in the `env.yml` file. It extends the "standard" pangeo
stack to add the pieces needed for `jupyter-book`. The specific items I added in order to get
jupyter-book to work are:

* `jupyter-book`
* `ghp-import`
* `jsonschema-with-format-nongpl`
* `webcolors`

Those last two items are needed to get the `jupyter-book` build to work, although they are
not declared as dependencies explicitly.

**NOTE** -- I added jupyter book to two different environments: `pangeofu` and also the 
"standard" `pangeo`. These environments differ with respect to versions of a couple of 
key libraries (zarr, fsspec). They both will work the same with respect to the jupyterbook 
build process. 

### Write Your Notebook

Build your workflow in a notebook and save it in an appropriate location.  Doesn't really matter
where it is, so long as it is in this repo -- I started a rough outline based on the old 'college numbering' system (101 is a
freshman level course, 201 is sophomore, etc). But that can easily change as you grow the
book project.

The finished notebook should be able to run all cells without interaction. Clear all outputs, reset the
kernel, then "run all". That verifies that it will run -- but it **does not build the book content.**
That comes later.

Your notebook can contain a mix of markdown and code cells. By default, all code cells are
included in the rendered output. If you want to hide a code cell, you can add a tag to its
metadata to control what gets shown in the rendered output.  Here are some that I like:

* `hide-input` -- The code cell is 'hidden' behind a dropdown.  The user can 'click to
    see more' to reveal the code cell contents.  Code outputs always show.
* `remove-input` -- The code cell is not shown at all.  The user can't see the code, but
    the outputs are shown.  I've included an example of this in an early cell in the
    `00_file_inspection.ipynb` notebook.  The code cell printing library versions has
    been tagged such that the book does not include the code cell, but the ouptut of 
    that cell's execution is included. 
* `remove-cell` -- Does not show the code cell or its outputs. **BUT THE CODE IS EXECUTED.**
    I like this for cells that are used to set up the environment, but don't need to be
    shown in the rendered output. Those cells won't show in the book, but if the user
    downloads the notebook to run, all the code is there.

Other tags are available.  See <https://jupyterbook.org/en/stable/interactive/hiding.html>

#### Special Markup

The jupyter-book project parses the markdown as 'MyST' markup.  This is a superset of
standard markdown, and adds some additional features. See <https://jupyterbook.org/en/stable/reference/cheatsheet.html>
for the full list of options. Here are some useful directives for the HyTEST documentation:


#### Admonitions

There are several types... `note`, `seealso`, `warning`, and so on. They are used like this:

```
:::{note}
This is a note.
:::
```

**NOTE** I have enabled the 'colon fence' extension, so you can use the `:::` syntax
rather than the backticks. I find it easier to type. Backticks are still supported.

#### Cross-References

Referring to other documents in the book is made easier with the `doc` directive.
This constructs a link for you, but it pulls the title of the target document automatically
to serve as the link text:

```
{doc}`/path/to/other/notebook`
```

Note that we are giving a path relative to the repo root (note the leading slash),
and we are **NOT** including the extension. This lets jupyterbook pick the right
file automatically (e.g. `.md` or `.ipynb`).

A couple of useful tips for using `doc` directives:

* The document you are pointing to must be known to the indexer -- which means that it
  *must* appear in the `_toc.yml` file.
* It is possible to use relative path names by leaving off that leading slash.

#### Sidebars and Margin Notes

The page layout of a rendered book page contains a left sidebar, the main content area,
and a right sidebar.  The left sidebar is used for the table of contents, and the right
sidebar is used for the page navigation links (like a table of contents for sections in
this specific page). This margin area on the right is often blank, but you can use it
to put in additional content that is not part of the main flow of the page.

```
:::{margin}
This is a margin note.
:::
```

You can also nest directives... but you have to pair the 'fences' up correctly, so the
parser knows when to end a directive.  If you wanted to put a `note` in the margin, you
might do this:

```
::::{margin}
:::{note}
This is a note in the margin.
:::
::::
```
The `margin` directive has a 4-colon fence, and the `note` directive has a 3-colon fence.

A `sidebar` is used much like a `margin` -- it just puts the text in a different spot.
A `sidebar` is placed in the main content area, against the right margin.  The rest of
the main content text flows around it.

I have found that sidebars do not lay out consistently in the browsers I've tested. I
almost always prefer the effect of `margin` over `sidebar`.

See the `back/Appendix_A.ipynb` notebook to see some of these tags in action. 

#### Math

You can include mathematical expressions in your markdown.  The syntax is very similar to LaTeX, but
uses a lighter-weight markup (KaTeX). Enclose LaTeX-style math expressions in `$` to
have them render.

### Add the notebook to the Table of Contents

I have configured the builder to ignore any document not explicitly listed in the
`_toc.yml` file. You must add your notebook to the table of contents for it to be
included in the compiled/rendered output, and also for other documents to be able to reference it
using `doc` directives.

The format of the `_toc.yml` file is described in the jupyter-book documentation
at <https://jupyterbook.org/en/stable/structure/toc.html>.  I have started a rough
draft already, which should be enough context to let you add what you like.

* `chapter` items appear in the sidebar table of contents on the left in the rendered
  output.
* If a chapter contains `sections`, those sections appear as sub-items in a drop-down
  menu in the sidebar.
* Sections can also contain sections.  This will give you nested dropdown menus.

### Build the Book

The build process operates like a mixture of `sphinx` and `papermill`. It uses the
standard document-generator `sphinx` to build the book content, and it uses a
`papermill`-like process to execute the notebooks and insert the results into the
compiled book content. (It's not papermill, but it's similar.)

#### Run `jb build`

* `cd` to the repo root directory
* Activate the correct conda environment (`conda activate global-pangeo`)
* Run `jb build .` to build the book.

This will create a `_build` directory that contains the compiled book content as well
as the jupyterbook cache.

I have configured the builder to use a cache.  That cache lives in the `_build` folder. 
It will only run notebooks for which it does not have already cached output.  A notebook
with a newer timestamp that that in the cache is also re-run. To force **all** notebooks
to run (ignoring the cache), run `jb build --all .` 

The `jb` command is an alias to `jupyter-book`.  Use whichever you prefer.  Pass a `--help`
to see the available options and arguments available. Mostly, the behavior is controlled
by the `_config.yml` file.

-----
**NOTE** // **NOTE** // **NOTE** // **NOTE** // **NOTE**

This is **VERY** important!!

The `jb` command will execute all the notebooks using the currently active conda environment,
**UNLESS** the `kernelspec` is explicitly set in the notebook metadata.  Most of the notebooks
authored on `nebari` will have that set -- but **IT WILL BE WRONG**.

If you use the standard jupyterlab interface on nebari, it will set the `kernelspec` to something
like this:

```json
   "kernelspec": {
       "display_name": "users-users-pangeofu",
       "language": "python",
       "name": "conda-env-users-users-pangeofu-py"
  }
```

It will *show* you "users-users-pangeofu" as the kernel name, but the actual conda
environment it will activate is named something else. If you were to `conda env list`,
you would see that an environment with name `conda-env-users-users-pangeofu-py` does
not exist -- so jupyter-book will **FAIL** ("kernelspec not found", or similar).

There are a few workarounds:

* Use the `vscode` interface on `nebari`.  It will set the `kernelspec` to a generic
  'python'.  I do not know why this is the case, but it is.  Save the notebook
  out of the `vscode` interface, and your jupyterbook runs will work, so long as
  the `pangeo` or `pangeofu` conda environments are currently active when `jb build` is run.
* Use the jupyterlab interface to set the kernel to "Python 3 (ipykernel)". I have had mixed 
  success with this. It usually works, but not always. 
* Use `vi` to manually edit the notebook JSON.  Completely remove the `kernelspec` entry
  from the notebook metadata. **THIS IS RISKY**

Before I discovered the `vscode` solution, I was manually editing the notebooks -- which
is not a sustainable way forward. The easiest workaround is probably to just reset the
kernel in the lab interface **once your notebook is done** (you've got all the executable
bits working). 

-----

### Publish

The `jb` command will build the book, but it will not publish it. The static HTML
content is generated in the `_build/html` directory under the repo (this folder
is ignored via the `.gitignore` file).  You can copy that directory to a web server
and serve it up, or you can use the `gh-pages` branch to publish it to github pages.
That's what we will do.

The typical workflow for this is to create a `gh-pages` branch, and then push all
of the HTML to that branch on github. The `gh-pages` branch is a special branch
that github will automatically publish to the github pages site.  That workflow
is a little tedious/manual -- and it has been automated with another package we
like to use: `ghp-import`.

Once built, execute the following command to publish the book to github pages:

```bash
ghp-import --no-jekyll -m 'commit message' --push --force _build/html
```

This will:

* Flag this as a 'bare' HTML site (no Jekyll processing)
* Create a commit on the `gh-pages` branch with the message 'commit message'
* Push the commit to the `gh-pages` branch on the origin remote (i.e. github)
* Force the push (overwrite any existing content)

...using the HTML content found in the `_build/html` directory.

### Verify

Now... go to the repo on github.... in the right sidebar of the main page, you should
see a link to a `gh-pages` "Environment". Click on that link.  You should see
the history of deployments to Pages.  Click on the most recent deployment to visit
the published book.

