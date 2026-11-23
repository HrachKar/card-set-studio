"""Step 3. Image generation (GPT Image 2 with style references). One call = one candidate image."""
import base64, io, threading, time
import openai
from openai import OpenAI
from PIL import Image

from . import config

_client = None

# Circuit breaker (Mac test 23.11): if the key or network is broken, every call fails the same way.
# After NET_FAIL_LIMIT connection errors in a row (or one auth error) no more calls are made.
NET_FAIL_LIMIT = 6
ABORT = None          # reason string once tripped
_net_fails = 0
_lock = threading.Lock()
_NET_ERRORS = (openai.APIConnectionError, openai.APITimeoutError)
_AUTH_ERRORS = (openai.AuthenticationError, openai.PermissionDeniedError)


def _note_error(e):
    global ABORT, _net_fails
    with _lock:
        if ABORT:
            return
        if isinstance(e, _AUTH_ERRORS):
            ABORT = f"OpenAI rejected the key: {str(e)[:200]}"
        elif isinstance(e, _NET_ERRORS):
            _net_fails += 1
            if _net_fails >= NET_FAIL_LIMIT:
                ABORT = f"{_net_fails} connection errors in a row: {str(e)[:200]}"
        if ABORT:
            print(f"[abort] {ABORT}. Stopping image requests.")


def _note_ok():
    global _net_fails
    with _lock:
        _net_fails = 0


def stop_if_aborted():
    """Call after a batch of cards: exits with a clear message if the breaker tripped."""
    if ABORT:
        raise SystemExit(f"[abort] Проблема с ключом или сетью, прогон остановлен, лишние попытки не потрачены.\n"
                         f"  Причина: {ABORT}\n"
                         f"  Что делать: проверьте интернет и ключ (bash setup.sh). Если ключ задан в ~/.zshrc, он важнее .env.")


def client():
    global _client
    if _client is None:
        _client = OpenAI(max_retries=0, timeout=300)
    return _client


def generate(prompt, category, out_path, usage, retries=5, refs=None):
    """Generate one image into out_path (full size PNG). Returns dict with timing / error."""
    t0 = time.time(); err = None
    for attempt in range(retries):
        if ABORT:
            err = err or f"aborted: {ABORT}"
            break
        files = [open(config.REF_DIR / r, "rb") for r in (refs or config.REFS[int(category)])]
        try:
            r = client().images.edit(model=config.IMAGE_MODEL, image=files, prompt=prompt,
                                     size=config.IMAGE_SIZE, quality=config.IMAGE_QUALITY)
            usage.add_image(getattr(r, "usage", None))
            raw = base64.b64decode(r.data[0].b64_json)
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            im.save(out_path)
            _note_ok()
            return dict(file=out_path.name, sec=round(time.time() - t0, 1), size=im.size)
        except Exception as e:
            err = str(e)[:400]
            if "moderation" in err.lower() or "safety" in err.lower():
                break
            _note_error(e)
            if ABORT:
                break
            time.sleep(15 * (attempt + 1))
        finally:
            for f in files:
                f.close()
    return dict(file=None, error=err, sec=round(time.time() - t0, 1))


def to_game_size(src, dst):
    Image.open(src).convert("RGB").resize(config.GAME_SIZE, Image.LANCZOS).save(dst)
