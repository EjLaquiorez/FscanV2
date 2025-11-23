"""
Auto-label images with placeholder YOLO bounding boxes and organize
them into a YOLO-ready dataset directory.

Usage examples (PowerShell):

  # Add a new class folder with 80/10/10 split into train/val/test
  python auto_label_dataset.py --src FreshBanana --class-name "Fresh Banana" \
      --dst Fruit_dataset --split 0.8 0.1 0.1

  # Add RottenBanana as class 1
  python auto_label_dataset.py --src RottenBanana --class-name "Rotten Banana" \
      --dst Fruit_dataset --split 0.8 0.1 0.1

  # Add any folder into flat images/labels instead of split
  python auto_label_dataset.py --src MyNewFruit --class-name "My New Fruit" \
      --dst Fruit_dataset --mode flat

The placeholder box defaults to: center (0.5, 0.5), size (0.8, 0.9).
Change via --bbox "0.5 0.5 0.8 0.9".
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
from pathlib import Path


IMAGE_EXTS = (".png", ".jpg", ".jpeg")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_or_create_classes(dst_root: Path) -> list[str]:
    classes_file = dst_root / "classes.txt"
    if classes_file.exists():
        return [line.strip() for line in classes_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    # create empty file
    ensure_dir(dst_root)
    classes_file.write_text("", encoding="utf-8")
    return []


def upsert_class_id(dst_root: Path, class_name: str | None, class_id: int | None) -> int:
    if class_id is not None:
        return class_id
    if not class_name:
        raise ValueError("Provide --class-name or --class-id")
    classes = read_or_create_classes(dst_root)
    if class_name not in classes:
        classes.append(class_name)
        (dst_root / "classes.txt").write_text("\n".join(classes) + "\n", encoding="utf-8")
    return classes.index(class_name)


def gather_images(src_dir: Path) -> list[Path]:
    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {src_dir}")
    images = [p for p in src_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS and p.is_file()]
    return images


def unique_target_path(target_dir: Path, base_name: str, ext: str) -> Path:
    candidate = target_dir / f"{base_name}{ext}"
    if not candidate.exists():
        return candidate
    # avoid collisions by suffixing _1, _2, ...
    i = 1
    while True:
        c = target_dir / f"{base_name}_{i}{ext}"
        if not c.exists():
            return c
        i += 1


def write_label(label_path: Path, class_id: int, bbox: tuple[float, float, float, float]) -> None:
    cx, cy, w, h = bbox
    label_path.write_text(f"{class_id} {cx} {cy} {w} {h}\n", encoding="ascii")


def copy_and_label(images: list[Path], dst_img: Path, dst_lbl: Path, class_id: int, bbox: tuple[float, float, float, float]) -> int:
    ensure_dir(dst_img)
    ensure_dir(dst_lbl)
    count = 0
    for src in images:
        base = src.stem
        tgt_img = unique_target_path(dst_img, base, src.suffix)
        shutil.copy2(src, tgt_img)
        tgt_lbl = dst_lbl / (tgt_img.stem + ".txt")
        write_label(tgt_lbl, class_id, bbox)
        count += 1
    return count


def split_indices(n: int, ratios: tuple[float, float, float]) -> tuple[list[int], list[int], list[int]]:
    r_train, r_val, r_test = ratios
    assert abs((r_train + r_val + r_test) - 1.0) < 1e-6, "Split ratios must sum to 1"
    idxs = list(range(n))
    random.shuffle(idxs)
    n_train = int(n * r_train)
    n_val = int(n * r_val)
    train_idx = idxs[:n_train]
    val_idx = idxs[n_train:n_train + n_val]
    test_idx = idxs[n_train + n_val:]
    return train_idx, val_idx, test_idx


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-label and organize images for YOLO training")
    parser.add_argument("--src", required=True, help="Source images folder (class folder)")
    parser.add_argument("--dst", default="data/datasets/Fruit_dataset", help="YOLO dataset root")
    parser.add_argument("--class-name", default=None, help="Class name to append/use in classes.txt")
    parser.add_argument("--class-id", type=int, default=None, help="Class id to use (overrides --class-name)")
    parser.add_argument("--mode", choices=["split", "flat"], default="split", help="split: train/val/test; flat: images/labels only")
    parser.add_argument("--split", nargs=3, type=float, default=[0.8, 0.1, 0.1], metavar=("TRAIN", "VAL", "TEST"), help="Split ratios for split mode")
    parser.add_argument("--bbox", nargs=4, type=float, default=[0.5, 0.5, 0.8, 0.9], metavar=("CX", "CY", "W", "H"), help="Placeholder bbox (normalized)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for splitting")
    args = parser.parse_args()

    random.seed(args.seed)
    dst_root = Path(args.dst)
    src_dir = Path(args.src)
    bbox = (args.bbox[0], args.bbox[1], args.bbox[2], args.bbox[3])

    # Determine/insert class id
    class_id = upsert_class_id(dst_root, args.class_name, args.class_id)

    # Gather images
    images = gather_images(src_dir)
    if not images:
        print(f"No images found under: {src_dir}")
        return

    if args.mode == "flat":
        dst_images = dst_root / "images"
        dst_labels = dst_root / "labels"
        copied = copy_and_label(images, dst_images, dst_labels, class_id, bbox)
        print(f"Flat copy complete -> images: {copied}, labels: {copied}")
        return

    # split mode
    train_idx, val_idx, test_idx = split_indices(len(images), tuple(args.split))
    train_imgs = [images[i] for i in train_idx]
    val_imgs = [images[i] for i in val_idx]
    test_imgs = [images[i] for i in test_idx]

    t1 = copy_and_label(train_imgs, dst_root / "train" / "images", dst_root / "train" / "labels", class_id, bbox)
    t2 = copy_and_label(val_imgs,   dst_root / "val" / "images",   dst_root / "val" / "labels",   class_id, bbox)
    t3 = copy_and_label(test_imgs,  dst_root / "test" / "images",  dst_root / "test" / "labels",  class_id, bbox)

    print("Split copy complete:")
    print(f"  Train: {t1}")
    print(f"  Val:   {t2}")
    print(f"  Test:  {t3}")


if __name__ == "__main__":
    main()


