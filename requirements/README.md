# Dependency management

`requirements/requirements.txt` defines the public runtime dependencies of TSDB.
Keep these compatible with downstream users; the root `uv.lock` instead records
the resolved runtime and `test` dependency group for reproducible validation.
The lock covers the declared Python range with environment markers and package
hashes. It does not constrain dependencies in the published wheel metadata.

The Ubuntu Latest / Python 3.14 reference CI job installs the locked dependencies
with hash verification before installing the wheel from the checkout. Other
compatibility jobs continue to resolve dependencies normally to exercise the
public dependency contract. The lock does not cover the isolated build backend.

After changing dependency declarations, refresh and commit the lock using uv
0.12.13 from the repository root:

```bash
uv lock --default-index https://pypi.org/simple
uv lock --check
uv export --locked --no-emit-project --group test --format requirements-txt -o locked-requirements.txt
```

The exported requirements are a temporary validation artifact, not another
source-controlled dependency manifest. Review intentional dependency upgrades
and regenerate the lock rather than editing generated entries by hand.
