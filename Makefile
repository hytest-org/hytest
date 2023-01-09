##
# Makefile for jupyterbook project


.DEFAULT: book

book:
	jupyter-book build .

_build/html: _toc.yml _config.yml
	jupyter-book build .

publish: _build/html
	ghp-import -m 'Update JupyterBook' --no-jekyll --push --force  $<

clean:
	jupyter-book clean .

real-clean:
	jupyter-book clean --all .
