"""Free check of the OpenAI key and network before any paid call.

models.list costs nothing. If it fails, the run stops at once with a clear message
instead of spending minutes on retries (Mac test 23.11: a broken key gave
"Connection error." on every image after ~226 s).
"""
import sys


def check_openai():
    import openai
    try:
        openai.OpenAI(timeout=20, max_retries=1).models.list()
    except openai.AuthenticationError:
        sys.exit("[preflight] OpenAI отклонил ключ (401). Проверьте ключ: bash setup.sh. "
                 "Если ключ задан ещё и в ~/.zshrc, он важнее .env: исправьте или удалите ту строку и перезапустите Claude.")
    except openai.PermissionDeniedError as e:
        sys.exit(f"[preflight] У ключа нет доступа (403): {str(e)[:200]}")
    except (openai.APIConnectionError, openai.APITimeoutError) as e:
        sys.exit(f"[preflight] Нет связи с OpenAI: {str(e)[:200]}. Проверьте интернет и VPN/прокси. "
                 "Если интернет в порядке, проверьте ключ: bash setup.sh.")
    except Exception as e:
        sys.exit(f"[preflight] Проверка ключа не прошла: {type(e).__name__}: {str(e)[:200]}")
    print("[preflight] OpenAI key OK")
