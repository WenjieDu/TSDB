Maintainer Guide
================

Contributing and testing
------------------------

Contribute new datasets, fixes, docs, and tests through
`GitHub <https://github.com/WenjieDu/TSDB>`_. Preserve existing identifiers,
source references and return contracts. Add a dataset profile and offline
regression tests for new loader behavior.

.. code-block:: bash

   pip install -e ".[tsqa]"
   pip install pytest pytest-cov pre-commit
   pre-commit run --all-files
   python -m pytest -m "not network" tests

PR and push CI measure deterministic offline coverage. Daily Testing adds one
representative real-dataset suite. For independent cold release validation,
run the following from a clean tracked checkout with the TSQA extra installed
and without ``TSDB_CI_RAW_CACHE`` set:

.. code-block:: bash

   python scripts/coverage_suite.py --output /path/to/new/report-directory

The runner executes offline and live suites separately on the same checkout,
combines their coverage databases (not an arithmetic average), and records the
revision, exit statuses, line counts and actual per-dataset download modes.
External-source errors fail the job; partial coverage never implies a passing
suite. The designated Coveralls upload remains offline-only.

TSQA authentication in CI
-------------------------

The TSQA dataset requires an authorized Hugging Face identity. Obtain access
at `Time-MQA/TSQA <https://huggingface.co/datasets/Time-MQA/TSQA>`_ and create
a dedicated read-only or fine-grained token at
`Hugging Face token settings <https://huggingface.co/settings/tokens>`_. Store
it as a repository Actions secret named ``HF_TOKEN`` in
`TSDB Actions secrets <https://github.com/WenjieDu/TSDB/settings/secrets/actions>`_.
Do not use a write token, print the token, or save it in an artifact or cache.

The daily workflow forwards this secret only for scheduled or manually
triggered runs on main/dev; the reusable workflow exposes it only in the
combined test step, and the coverage runner passes it only to the live pytest
subprocess. Ordinary offline CI receives no token. Missing credentials fail
trusted daily runs before the expensive downloads. For other branch runs the
secret is not forwarded; gated TSQA access may fail, and that is not a full
release validation. Repository secrets are accessible to workflows written by
trusted repository collaborators, so maintain branch protection and review
workflow changes. For local combined validation, export an authorized
``HF_TOKEN`` securely before running the coverage script (the tests isolate HOME).
TSQA files are not eligible for the shared raw cache.

Daily real-dataset cache
------------------------

Daily Testing on the default branch runs three offline compatibility jobs and
one representative real-dataset suite. Monday–Saturday UTC it restores the
current week's verified public raw data; Sunday bypasses restoration, downloads
every representative dataset afresh and seeds a new cache. Manual Daily Testing
has ``cold-download: true`` by default; use this for release acceptance.
Manual runs outside the default branch and pushes to ``run_daily_testing`` do
not use shared dataset caches.

Only four reviewed CC BY 4.0 datasets are eligible initially:

* `PhysioNet Challenge 2019 v1.0.0 <https://physionet.org/content/challenge-2019/1.0.0/>`_ (Reyna et al., 2019).
* `ElectricityLoadDiagrams20112014 <https://doi.org/10.24432/C58C86>`_ (Artur Trindade, 2015).
* `Beijing Multi-Site Air Quality <https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality>`_ (Song Chen, 2017; DOI 10.24432/C5RK5G).
* `Air Quality <https://doi.org/10.24432/C59K5F>`_ (Saverio De Vito; see source attribution).

Consult each linked source and the `CC BY 4.0 license <https://creativecommons.org/licenses/by/4.0/>`_.
Raw bytes are not transformed. Other datasets continue cold downloads every run.
Cache keys incorporate reviewed source URLs, cache policy and UTC week, not
loader changes. Update the cache policy/version when raw layout changes.
Only raw files and integrity/attribution manifests are saved, never pickles
or temporary downloads. Restored snapshots are verified and copied into an
isolated test cache; the current loader parses them and checks its new pickle.

A cache is saved only after a passing suite and verification of the full
allowlist, with an uncompressed budget of 1 GiB per dataset and 2 GiB total.
Corrupt or unexpected contents fail the job. Delete the affected Actions Cache
or run cold validation independently. Storage is best effort; misses download
fresh data. Warm/mixed coverage is not full cold validation evidence; consult
``summary.json`` for modes.

Release procedure
-----------------

Before publishing, review the exact main commit, passing CI and full cold
live/combined coverage evidence. The Publish to PyPI workflow can be run
manually from the default branch against an existing stable tag for build and
offline validation only. Publishing happens only on a published stable GitHub
Release; the tag must match the package version and identify a commit reachable
from main. A separate publishing job consumes validated wheel and sdist files,
checks SHA-256 digests and uses PyPI Trusted Publishing.

Configure the PyPI project ``tsdb`` with owner ``WenjieDu``, repository ``TSDB``,
workflow ``publish_to_PyPI.yml``, and GitHub environment ``pypi`` before the
first release. No publication occurs on a branch push or manual dry run.

Use ``python -m build`` (sdist followed by wheel) from a clean checkout;
a direct wheel build in an old working directory may include stale setuptools
artifacts. The release validator rejects unexpected wheel members.

Release tooling and the reference runtime environment are locked for Linux
x86_64 / Python 3.10 in ``requirements/requirements_release.txt``. Regenerate
from ``requirements/requirements_release.in`` using the command in the generated
file. This is a release-environment lock, not a constraint on TSDB consumers.
The build uses the verified backend with ``--no-isolation``; local artifact
installs use ``--no-deps --no-index``. Both wheel and sdist are installed and
smoke-tested.

Documentation build
-------------------

.. code-block:: bash

   pip install -e .
   pip install -r docs/requirements.txt
   python -m sphinx -W --keep-going -b html docs /tmp/tsdb-docs-html
   python -m sphinx -W --keep-going -b doctest docs /tmp/tsdb-docs-doctest

The doctests are network-independent. Real-dataset examples in the user guide
require network access on first load; they are not executed by Sphinx.

Autodoc imports data-access modules in an isolated temporary home to avoid
initializing or migrating the maintainer's real ecosystem configuration.
