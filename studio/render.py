"""Step 3. Image generation (GPT Image 2 with style references). One call = one candidate image."""
import base64, io, time
from openai import OpenAI
from PIL import Image

from . import config

_client = None


def client():
    global _client
    if _client is None:
        _client = OpenAI(max_retries=0, timeout=300)
    return _client


def generate(prompt, category, out_path, usage, retries=5, refs=None):
    """Generate one image into out_path (full size PNG). Returns dict with timing / error."""
    t0 = time.time(); err = None
    for attempt in range(retries):
        files = [open(config.REF_DIR / r, "rb") for r in (refs or config.REFS[int(category)])]
        try:
            r = client().images.edit(model=config.IMAGE_MODEL, image=files, prompt=prompt,
                                     size=config.IMAGE_SIZE, quality=config.IMAGE_QUALITY)
            usage.add_image(getattr(r, "usage", None))
            raw = base64.b64decode(r.data[0].b64_json)
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            im.save(out_path)
            return dict(file=out_path.name, sec=round(time.time() - t0, 1), size=im.size)
        except Exception as e:
            err = str(e)[:400]
            if "moderation" in err.lower() or "safety" in err.lower():
                break
            time.sleep(15 * (attempt + 1))
        finally:
            for f in files:
                f.close()
    return dict(file=None, error=err, sec=round(time.time() - t0, 1))


def to_game_size(src, dst):
    Image.open(src).convert("RGB").resize(config.GAME_SIZE, Image.LANCZOS).save(dst)
