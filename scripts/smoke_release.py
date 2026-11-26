"""Exercise the installed package, not the adjacent source checkout."""

# License: BSD-3-Clause

import os
import sys
from pathlib import Path

import tsdb
from tsdb.utils.logging import Logger


def main():
    home = Path.home()
    source = Path(__file__).resolve().parents[1]
    if source in Path(tsdb.__file__).resolve().parents:
        raise RuntimeError("Smoke test unexpectedly imported source checkout")
    if "pandas" in sys.modules or "numpy" in sys.modules or (home / ".pypots").exists():
        raise RuntimeError("Import was not lightweight")
    assert Logger
    assert "electricity_load_diagrams" in tsdb.list()
    from tsdb.utils.config import CONFIG_TEMPLATE_PATH, read_configs

    assert Path(CONFIG_TEMPLATE_PATH).is_file()
    raw = Path(read_configs().get("path", "tsdb_home")) / "electricity_load_diagrams"
    raw.mkdir(parents=True)
    (raw / "LD2011_2014.txt").write_text(";meter\n2011-01-01 00:00:00;1,5\n", encoding="utf-8")
    data = tsdb.load("electricity_load_diagrams")
    assert data["X"]["meter"].tolist() == [1.5]
    assert tsdb.load("electricity_load_diagrams")["X"].equals(data["X"])
    assert tsdb.list_cache() == ["electricity_load_diagrams"]
    print(f"Installed TSDB {tsdb.__version__} from {tsdb.__file__}; HOME={os.fspath(home)}")


if __name__ == "__main__":
    main()
