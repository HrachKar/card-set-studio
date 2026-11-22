import json, re, threading
from pathlib import Path
from . import config


def save_json(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "card"


class Usage:
    """Thread-safe token counter with a rough USD estimate (prices in config.PRICE)."""
    def __init__(self):
        self.lock = threading.Lock()
        self.d = dict(images=0, image_out=0, image_in=0, text_in_img=0, llm_calls=0, llm_in=0, llm_out=0)

    def add_image(self, u):
        with self.lock:
            self.d["images"] += 1
            if u:
                self.d["image_out"] += u.output_tokens or 0
                det = getattr(u, "input_tokens_details", None)
                self.d["image_in"] += getattr(det, "image_tokens", 0) or 0
                self.d["text_in_img"] += getattr(det, "text_tokens", 0) or 0

    def add_llm(self, u):
        with self.lock:
            self.d["llm_calls"] += 1
            if u:
                self.d["llm_in"] += u.input_tokens or 0
                self.d["llm_out"] += u.output_tokens or 0

    def usd(self):
        p = config.PRICE
        return round(sum(self.d[k] * p[k] / 1e6 for k in p), 2)

    def report(self):
        return {**self.d, "usd_estimate": self.usd()}
