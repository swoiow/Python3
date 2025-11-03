import os
import shutil
from collections import defaultdict
from pathlib import Path


# === 配置区 ===
OLD_DIR = Path(r"C:\Python312")  # 官方 3.12.10 安装目录
NEW_DIR = Path(r"C:\cpython-3.12.12-win64")  # 你 build 的 3.12.12 产物目录
MERGED_DIR = Path(r"C:\Python3_1212")  # 合成输出目录

DRY_RUN = False  # True = 只打印，不实际写入；确认逻辑后改 False
BACKUP_OLD_FILES = False  # True = 生成 *.bak31210 备份；False = 直接覆盖不留备份

# 碰到同名文件在多个位置时怎么处理
#   "skip"   -> 打印警告，跳过，不覆盖
#   "first"  -> 选第一个路径（不太安全，但有时你想强行用）
ON_AMBIGUOUS = "first"


def build_old_index(old_dir: Path) -> dict[str, list[Path]]:
    """
    在 OLD_DIR 下建立索引：
    文件名 -> [相对路径1, 相对路径2, ...]
    """
    index: dict[str, list[Path]] = defaultdict(list)
    for root, dirs, files in os.walk(old_dir):
        root_path = Path(root)
        rel_root = root_path.relative_to(old_dir)
        for name in files:
            rel_path = rel_root / name  # 如 DLLs\_asyncio.pyd
            index[name].append(rel_path)
    return index


def copy_old_to_merged(old_dir: Path, merged_dir: Path) -> None:
    if merged_dir.exists():
        raise RuntimeError(f"目标合成目录已存在：{merged_dir}，请先手动删除或改名。")
    print(f"[+] 复制旧目录 {old_dir} -> {merged_dir}")
    if not DRY_RUN:
        shutil.copytree(old_dir, merged_dir)


def overlay_by_filename(
    merged_dir: Path,
    new_dir: Path,
    old_index: dict[str, list[Path]],
) -> None:
    """
    遍历 NEW_DIR 中所有文件：
    - 用“文件名”在 old_index 中查找对应的相对路径
    - 若不存在：提示 & 跳过（默认）
    - 若唯一：在 MERGED_DIR 对应位置备份旧文件并覆盖（是否备份由 BACKUP_OLD_FILES 决定）
    - 若多个：按 ON_AMBIGUOUS 策略处理
    """
    print(f"[+] 按文件名匹配 OLD_DIR 结构，用 {new_dir} 覆盖 {merged_dir}")
    print(f"    BACKUP_OLD_FILES = {BACKUP_OLD_FILES}")

    for root, dirs, files in os.walk(new_dir):
        root_path = Path(root)
        for name in files:
            src_file = root_path / name  # C:\cpython-3.12.12-win64\...\xxx.pyd

            candidates = old_index.get(name)
            if not candidates:
                # OLD_DIR 中没有这个名字的文件
                print(f"[-] OLD 中未找到同名文件，跳过: {name}  (src: {src_file})")
                continue

            if len(candidates) > 1:
                if ON_AMBIGUOUS == "skip":
                    print(f"[!] 同名文件在 OLD 中有多个位置，跳过: {name}")
                    for p in candidates:
                        print(f"    - {p}")
                    continue
                elif ON_AMBIGUOUS == "first":
                    rel_path = candidates[0]
                    print(f"[!] 同名文件多处存在，按策略 'first' 选用: {rel_path}")
                else:
                    raise RuntimeError(f"未知 ON_AMBIGUOUS 设置: {ON_AMBIGUOUS}")
            else:
                rel_path = candidates[0]

            dst_file = merged_dir / rel_path  # 在合成目录中的真实位置
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # 备份或直接覆盖
            if dst_file.exists():
                if BACKUP_OLD_FILES:
                    backup_file = dst_file.with_suffix(dst_file.suffix + ".bak31210")
                    print(f"[=] 备份旧文件: {dst_file} -> {backup_file}")
                    if not DRY_RUN:
                        if backup_file.exists():
                            backup_file.unlink()
                        dst_file.rename(backup_file)
                else:
                    print(f"[~] 直接覆盖旧文件（不生成备份）: {dst_file}")
            else:
                print(f"[?] 注意：合成目录中原本不存在该路径，仍将写入: {dst_file}")

            # 覆盖为 3.12.12 的新文件
            print(f"[>] 覆盖文件: {src_file} -> {dst_file}")
            if not DRY_RUN:
                shutil.copy2(src_file, dst_file)


def main() -> None:
    if not OLD_DIR.is_dir():
        raise RuntimeError(f"旧目录不存在或不是目录：{OLD_DIR}")
    if not NEW_DIR.is_dir():
        raise RuntimeError(f"新目录不存在或不是目录：{NEW_DIR}")

    print(f"OLD_DIR          : {OLD_DIR}")
    print(f"NEW_DIR          : {NEW_DIR}")
    print(f"MERGED_DIR       : {MERGED_DIR}")
    print(f"DRY_RUN          : {DRY_RUN}")
    print(f"BACKUP_OLD_FILES : {BACKUP_OLD_FILES}")
    print(f"ON_AMBIGUOUS     : {ON_AMBIGUOUS}")
    print()

    if DRY_RUN:
        print("[!] 当前为 DRY_RUN 模式，只打印操作，不实际写入。\n")

    # 1. 建立 OLD_DIR 文件名索引
    print("[+] 构建 OLD_DIR 文件索引（按文件名）...")
    old_index = build_old_index(OLD_DIR)
    print(f"[+] 索引完成，共 {len(old_index)} 个不同文件名\n")

    # 2. 复制旧目录到合成目录
    copy_old_to_merged(OLD_DIR, MERGED_DIR)

    # 3. 使用 NEW_DIR 中的文件按 OLD 结构覆盖
    overlay_by_filename(MERGED_DIR, NEW_DIR, old_index)

    print("\n[✓] 合成完成。")
    print(f"    合成目录: {MERGED_DIR}")
    print("    建议后续测试：")
    print(f"      {MERGED_DIR}\\python.exe -V")
    print(f"      {MERGED_DIR}\\python.exe -m site")
    print(f"      {MERGED_DIR}\\python.exe -m venv venv31212 && .\\venv31212\\Scripts\\python.exe -V")


if __name__ == "__main__":
    main()
