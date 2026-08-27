# -*- coding: utf-8 -*-
"""Prepare FlClash pinxixi fork."""
import os
import shutil
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(BASE, "FlClash")
PATCHES = os.path.join(BASE, "patches")

COPIES = [
    ("lib/common/pinxixi.dart", "lib/common/pinxixi.dart"),
    ("lib/common/constant.dart", "lib/common/constant.dart"),
    ("lib/common/request.dart", "lib/common/request.dart"),
    ("lib/models/profile.dart", "lib/models/profile.dart"),
    ("android/app/build.gradle.kts", "android/app/build.gradle.kts"),
    ("android/google-services.json", "android/app/google-services.json"),
    ("macos/AppInfo.xcconfig", "macos/Runner/Configs/AppInfo.xcconfig"),
    ("linux/CMakeLists.txt", "linux/CMakeLists.txt"),
]


def run(cmd, cwd=None, t=900):
    print(f">>> {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=t)
    out = (r.stdout or "") + (r.stderr or "")
    print(out[-2000:] if len(out) > 2000 else out)
    if r.returncode != 0:
        raise RuntimeError(f"failed: {cmd}")


def main():
    if not os.path.isdir(REPO):
        run(
            "git clone --depth 1 https://github.com/chen08209/FlClash.git FlClash",
            cwd=BASE,
        )

    for rel_src, rel_dst in COPIES:
        src = os.path.join(PATCHES, rel_src)
        dst = os.path.join(REPO, rel_dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"copied {rel_dst}")

    print("SOURCE READY at", REPO)


if __name__ == "__main__":
    main()
