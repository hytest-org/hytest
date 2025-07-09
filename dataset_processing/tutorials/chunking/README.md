# Data Chunking Tutorial Overview

Chunking data is an important foundational step in preparing data for HyTEST workflows. It helps massive datasets be easily subsetted (without having to download the whole dataset), and it supports efficient parallelized workflows. Organizing and chunking the data appropriately will dramatically affect the performance of analyses.

In this tutorial, we will go over all levels of information on data chunking,
from the basic introductions on the topic to complex methods of selecting optimal chunk sizes and rechunking on the cloud.
Much of what is covered in this tutorial replicates concepts covered in a variety of materials that we cite as we go.
However, that material has been adapted to use data that looks like data you might encounter in a HyTEST workflow.

The content is split into two primary sections:

 - [Introduction to Chunking](./101/index.md)
 - [Advanced Topics in Chunking](./201/index.md)

In [Introduction to Chunking](./101/index.md), we discuss all of the basic introductory topics associated with chunking. As for [Advanced Topics in Chunking](./201/index.md), we dive into some more advanced topics related to chunking, which require a firm understanding of introductory topics. Feel free to read this tutorial in order (which has been set up for those new to chunking) or jump directly to the topic that interests you.

If you would like to run this tutorial on your own, you can find the jupyter notebooks that are used in this tutorial in our [Github repository](https://github.com/hytest-org/hytest/tree/main/dataset_processing/tutorials/chunking). We also include a python environment file [here](https://github.com/hytest-org/hytest/blob/main/dataset_processing/tutorials/chunking/env.yml). The "101: Introduction to Chunking" topics can be run on your local computer, but some of the "201: Advanced Topics in Chunking" notebooks will likely require an HPC or cloud computing resources to complete. If you are a USGS staff member, you can work in HyTEST's preconfigured cloud environment which will provide both the python environment and access to the needed cloud computing resources. Please reach out to asnyder@usgs.gov if you would like access to this space.

If you find any issues or errors in this tutorial, please open an [issue in our Github repository](https://github.com/hytest-org/hytest/issues). If you have questions or want to talk more about data chunking, please feel free to ask on our [Data Processing Discussion Board](https://github.com/hytest-org/hytest/discussions/categories/data-processing-and-analysis).
