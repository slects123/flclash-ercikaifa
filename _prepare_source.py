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
    ("lib/common/pinxixi_traffic.dart", "lib/common/pinxixi_traffic.dart"),
    ("lib/common/common.dart", "lib/common/common.dart"),
    ("lib/common/constant.dart", "lib/common/constant.dart"),
    ("lib/common/request.dart", "lib/common/request.dart"),
    ("lib/models/profile.dart", "lib/models/profile.dart"),
    ("lib/providers/actions/common.dart", "lib/providers/actions/common.dart"),
    ("android/app/build.gradle.kts", "android/app/build.gradle.kts"),
    ("android/google-services.json", "android/app/google-services.json"),
    ("android/common/Components.kt", "android/common/src/main/java/com/follow/clash/common/Components.kt"),
    (
        "android/app/src/main/kotlin/com/follow/clash/plugins/ServicePlugin.kt",
        "android/app/src/main/kotlin/com/follow/clash/plugins/ServicePlugin.kt",
    ),
    (
        "android/app/src/main/kotlin/com/follow/clash/plugins/AppPlugin.kt",
        "android/app/src/main/kotlin/com/follow/clash/plugins/AppPlugin.kt",
    ),
    (
        "android/app/src/main/kotlin/com/follow/clash/plugins/TilePlugin.kt",
        "android/app/src/main/kotlin/com/follow/clash/plugins/TilePlugin.kt",
    ),
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


def patch_app_env_manager(content: str) -> str:
    """去掉右上角 PRE/DEBUG 角标。"""
    old = """  @override
  Widget build(BuildContext context) {
    if (kDebugMode) {
      if (globalState.isPre) {
        return Banner(
          message: 'DEBUG',
          location: BannerLocation.topEnd,
          child: child,
        );
      }
    }
    if (globalState.isPre) {
      return Banner(
        message: globalState.appEnv.toUpperCase(),
        location: BannerLocation.topEnd,
        child: child,
      );
    }
    return child;
  }"""
    new = """  @override
  Widget build(BuildContext context) {
    // 二次开发发行包不展示 PRE/DEBUG 角标
    return child;
  }"""
    if old not in content:
        if "二次开发发行包不展示" in content:
            return content
        raise RuntimeError("AppEnvManager build() pattern not found")
    return content.replace(old, new)


def patch_state_app_env(content: str) -> str:
    """默认 APP_ENV=stable，避免漏传 dart-define 时仍显示 PRE。"""
    old = "appEnv = const String.fromEnvironment('APP_ENV', defaultValue: 'pre');"
    new = "appEnv = const String.fromEnvironment('APP_ENV', defaultValue: 'stable');"
    if old not in content:
        if "defaultValue: 'stable'" in content:
            return content
        raise RuntimeError("APP_ENV defaultValue pattern not found")
    return content.replace(old, new)


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

    app_mgr = os.path.join(REPO, "lib", "manager", "app_manager.dart")
    with open(app_mgr, "r", encoding="utf-8") as f:
        mgr = f.read()
    with open(app_mgr, "w", encoding="utf-8") as f:
        f.write(patch_app_env_manager(mgr))
    print("patched AppEnvManager (no PRE banner)")

    state_path = os.path.join(REPO, "lib", "state.dart")
    with open(state_path, "r", encoding="utf-8") as f:
        state = f.read()
    with open(state_path, "w", encoding="utf-8") as f:
        f.write(patch_state_app_env(state))
    print("patched state.dart APP_ENV default=stable")

    print("SOURCE READY at", REPO)


if __name__ == "__main__":
    main()
