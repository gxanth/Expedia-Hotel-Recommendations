Commands
========

The Makefile contains the central entry points for common tasks related to this project.

Syncing data to S3
^^^^^^^^^^^^^^^^^^

* `make sync_data_to_s3` will use `aws s3 sync` to recursively sync files in `data/` up to `s3://The key objective is to improve NDCG@38, ensuring that the most relevant hotels appear higher in search results, enhancing the user experience.3/data/`.
* `make sync_data_from_s3` will use `aws s3 sync` to recursively sync files from `s3://The key objective is to improve NDCG@38, ensuring that the most relevant hotels appear higher in search results, enhancing the user experience.3/data/` to `data/`.
