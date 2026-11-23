#!/bin/bash
# One-time setup: Python virtual env, dependencies, OpenAI key in .env.
# Run from the repository folder:  bash setup.sh
# Safe to run again: it reuses .venv and asks before replacing an existing key.
set -e
cd "$(dirname "$0")"

say() { printf '\n== %s\n' "$1"; }

say "1/3 Python"
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Нужен Python 3.10 или новее. Поставьте с https://www.python.org/downloads/ (или: brew install python) и запустите скрипт снова."
  exit 1
fi
echo "OK: $("$PY" --version)"

say "2/3 Зависимости (.venv)"
if [ ! -x .venv/bin/python ]; then
  "$PY" -m venv .venv
fi
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt
.venv/bin/python -c "import openai, PIL" && echo "OK: openai и pillow установлены в .venv"

say "3/3 Ключ OpenAI (.env)"
write_key=1
if [ -f .env ] && grep -q '^OPENAI_API_KEY=.' .env; then
  read -r -p "Ключ уже сохранён в .env. Заменить? [y/N] " ans
  case "$ans" in y|Y|д|Д) ;; *) write_key=0; echo "Оставил старый ключ." ;; esac
fi
if [ "$write_key" = 1 ]; then
  echo "Ключ: https://platform.openai.com/api-keys"
  echo "Вставьте ключ (sk-...) и нажмите Enter. Символы не показываются, это нормально."
  read -r -s key; echo
  key="$(printf '%s' "$key" | tr -d '[:space:]"'"'")"
  if [ -z "$key" ]; then
    echo "Ключ пустой, .env не изменён. Запустите скрипт снова, когда ключ будет под рукой."
    exit 1
  fi
  case "$key" in sk-*) ;; *) echo "Внимание: ключ обычно начинается с sk-. Сохраняю как есть." ;; esac
  umask 077
  if [ -f .env ]; then grep -v '^OPENAI_API_KEY=' .env > .env.tmp || true; else : > .env.tmp; fi
  printf 'OPENAI_API_KEY=%s\n' "$key" >> .env.tmp
  mv .env.tmp .env
  chmod 600 .env
  echo "OK: ключ сохранён в .env (файл в .gitignore, в git не попадёт)."
fi

if [ -n "$OPENAI_API_KEY" ]; then
  echo "Внимание: OPENAI_API_KEY уже задан в окружении (обычно из ~/.zshrc). Он важнее .env, проверяю именно его."
  echo "Если проверка ниже не пройдёт, исправьте или удалите строку export OPENAI_API_KEY в ~/.zshrc и откройте новое окно Терминала."
fi

# Free check: listing models costs nothing, it only tells whether the key is accepted.
if .venv/bin/python - <<'PY'
import sys
sys.path.insert(0, ".")
from studio.envfile import load_env
load_env()
from openai import OpenAI
try:
    OpenAI(timeout=20, max_retries=0).models.list()
except Exception as e:
    print("Ключ не прошёл проверку:", type(e).__name__, str(e)[:200])
    sys.exit(1)
print("OK: OpenAI принял ключ (проверка бесплатная).")
PY
then :; else
  echo "Проверьте ключ и интернет, потом запустите скрипт снова (bash setup.sh)."
  exit 1
fi

say "Готово"
echo "Дальше: откройте эту папку в приложении Claude (вкладка Code) или в Терминале наберите: claude"
