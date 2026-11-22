"""Optional post-processing: micro-contrast and deeper contact shadows (no prompt change).
Off by default; turn on with config.POST_MICROCONTRAST = True. Free: works on already generated images.
  python -m studio.post <in.png> <out.png>
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

def microcontrast(im, radius=24, percent=35, shadow=0.12):
    im = im.convert("RGB").filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=2))
    a = np.asarray(im, dtype=float) / 255
    lum = a.mean(axis=2, keepdims=True)
    k = 1 - shadow * np.clip(1 - lum / 0.55, 0, 1)   # darken only the darker tones (shadows, joints)
    return Image.fromarray((np.clip(a * k, 0, 1) * 255).astype("uint8"))

if __name__ == "__main__":
    microcontrast(Image.open(sys.argv[1])).save(sys.argv[2])
