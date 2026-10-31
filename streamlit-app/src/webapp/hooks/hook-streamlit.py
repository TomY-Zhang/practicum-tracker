import platform
import site
from pathlib import Path

import streamlit
from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

os = platform.system()
match os:
    case "Windows":
        datas = [
            (str(Path(streamlit.__file__).parent / "runtime"), "./streamlit/runtime")
        ]
    case "Linux":
        site_packages_dir = site.getsitepackages()[0]
        datas = [(f"{site_packages_dir}/streamlit/runtime", "./streamlit/runtime")]
    case _:
        raise ValueError(f"Unable to build executable for system: {os}")

datas += copy_metadata("streamlit")
datas += collect_data_files("streamlit")
hiddenimports = collect_submodules("streamlit")
