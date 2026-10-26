import sys

import streamlit.web.cli as stcli

from webapp.config import WEBAPP_DIR


def main():
    path_str = str(WEBAPP_DIR / "pages" / "__init__.py")
    sys.argv = [
        "streamlit",
        "run",
        path_str,
        "--global.developmentMode=false",
        "--server.headless=true",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
