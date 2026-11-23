"""Read KEY=VALUE lines from the repository's .env into the environment (stdlib only).

Needed for the Claude desktop app: apps started from the Dock do not read ~/.zshrc,
so a key exported there is invisible. setup.sh writes the key to .env instead.
A variable that is already set in the environment wins over .env.
API keys are cleaned of spaces, line breaks and quotes from both sources: a key pasted
with a line break (e.g. into ~/.zshrc) made every request fail with "Connection error." (Mac test 23.11).
"""
import os, re, sys
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def load_env(path=ENV_FILE):
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().removeprefix("export ").strip()
        v = v.strip().strip('"').strip("'")
        if k and v and not os.environ.get(k):
            os.environ[k] = v
    clean_keys()


def clean_keys():
    for k in [k for k in os.environ if k.endswith("_API_KEY")]:
        v = os.environ[k]
        c = re.sub(r"[\s\"']", "", v)
        if c != v:
            os.environ[k] = c
            print(f"[key] {k}: removed spaces / line breaks / quotes from the key", file=sys.stderr)
