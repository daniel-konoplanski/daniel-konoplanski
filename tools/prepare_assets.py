#!/usr/bin/env python3
"""Regenerate the featured-project screenshots used by README.md.

Every card is normalised to the same 16:10 frame at 800x500 (2x the 400px
render width) with rounded, transparent corners so it sits correctly on both
the light and dark GitHub themes.

Run from the repository root:

    python3 tools/prepare_assets.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

CARD_SIZE = (800, 500)  # 16:10
CORNER_RADIUS = 16

# Konsole background of the p2p_ft captures, sampled from an empty region.
TERMINAL_BG = (35, 42, 48)


def round_corners(image: Image.Image, radius: int) -> Image.Image:
    """Return an RGBA copy of *image* with its corners masked out."""
    image = image.convert("RGBA")
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, image.width - 1, image.height - 1), radius=radius, fill=255
    )
    image.putalpha(mask)
    return image


def finish(image: Image.Image, destination: Path) -> None:
    """Downscale *image* to the card frame, round it, and write it out."""
    card = image.convert("RGB").resize(CARD_SIZE, Image.LANCZOS)
    round_corners(card, CORNER_RADIUS).save(destination)
    print(f"{destination.relative_to(ROOT)}  {card.size[0]}x{card.size[1]}")


def build_ramiel() -> None:
    """Source is 2497x1565 (1.5955) - trim 4px to land on an exact 16:10."""
    source = Image.open(ASSETS / "ramiel" / "dashboard.jpg")
    finish(source.crop((0, 0, 2497, 1561)), ASSETS / "ramiel" / "dashboard-rounded.png")


def build_bf2() -> None:
    """Source is 2045x1596 (1.281) - trim the bottom to reach 16:10.

    Nametags, the in-game menu and the minimap all sit in the upper two
    thirds, so the crop only loses the lower part of the weapon model.
    """
    source = Image.open(ASSETS / "bf2_memhack_v2" / "nametags_and_maphack.jpg")
    finish(
        source.crop((0, 0, 2045, 1278)),
        ASSETS / "bf2_memhack_v2" / "nametags_and_maphack-rounded.png",
    )


def build_p2p_ft() -> None:
    """Compose both halves of a transfer into a single 16:10 frame.

    No single p2p_ft capture fills a 16:10 frame - each one is a 957x445
    terminal with text only in the top half. Stacking the sender and the
    receiver fills the card and shows both ends of the protocol at once.

    Each block is cropped just below its last line of output; the canvas is
    filled with the terminal background so the padding is seamless.
    """
    directory = ASSETS / "p2p_ft"
    # Text occupies rows 31..203 (sender) and 29..223 (receiver); crop a
    # little below each to leave a consistent bottom margin inside the block.
    sender = Image.open(directory / "sender_completed.jpg").crop((0, 0, 957, 228))
    receiver = Image.open(directory / "receiver_completed.jpg").crop((0, 0, 957, 248))

    gap = 40
    canvas_height = round(957 / 1.6)  # 598
    padding = (canvas_height - sender.height - gap - receiver.height) // 2

    canvas = Image.new("RGB", (957, canvas_height), TERMINAL_BG)
    canvas.paste(sender, (0, padding))
    canvas.paste(receiver, (0, padding + sender.height + gap))

    finish(canvas, directory / "transfer-rounded.png")


def main() -> None:
    build_ramiel()
    build_bf2()
    build_p2p_ft()


if __name__ == "__main__":
    main()
