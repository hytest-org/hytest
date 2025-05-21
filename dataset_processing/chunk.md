# Chunking Data

Chunking data is an important foundational step in preparing data for HyTEST workflows. It helps massive datasets be easily subsetted (without having to download the whole dataset), and it supports efficient parallelized workflows. Organizing and chunking the data appropriately will dramatically affect the performance of analyses.

This section briefly steps through: 

* What is rechunking?
* Why we would want to rechunk the data?
* A real-world example
* A bigger real-world example

This will give you an introduction to the data chunking process.

Please note that the code use in this chapter's tutorials is out of date and does not work with `xarray>2024.1`. We are working on an updated version of this content - please reach out to our team on our [discussion board](https://github.com/hytest-org/hytest/discussions/categories/data-processing-and-analysis) if you would like early access to this content.

```{tableofcontents}
```