import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

if __name__ == "__main__":
    # Indicamos a Streamlit que ejecute tu archivo principal
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("dji_pro_tool.py"), # Tu archivo original
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())