#!/usr/bin/env python3
"""Static validation for FS25_BgaExtensions.

These checks intentionally cover only what can be proven without launching FS25.
The game log and disposable-save tests remain the authority for runtime behavior.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


VERSION_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
L10N_RE = re.compile(r"\$l10n_([A-Za-z0-9_]+)")
SELF_MOD_REF_RE = re.compile(r"\$moddir\$FS25_BgaExtensions/([^\"'\s<>]+)")

VANILLA_FILLTYPES = {
    "BEETROOT",
    "CARROT",
    "CHAFF",
    "DRYGRASS_WINDROW",
    "GREENBEAN",
    "GRASS_WINDROW",
    "LIQUIDMANURE",
    "MANURE",
    "PARSNIP",
    "PEA",
    "POTATO",
    "SILAGE",
    "SILAGE_ADDITIVE",
    "SPINACH",
    "STRAW",
    "SUGARCANE",
    "SUGARBEET_CUT",
    "WOODCHIPS",
}

DEPENDENCY_FILLTYPES = {
    "FS25_PlanET_BGA_Modular": {
        "LIQUIDMANURE1",
        "MANURE_IN",
        "SILAGE_IN",
        "SUGARBEETCUT_IN",
    },
    "pdlc_strawHarvestPack": {
        "STRAW_PELLETS",
    },
}

OPTIONAL_FILLTYPE_DENYLIST = {
    "ALFALFA_WINDROW",
    "CLOVER_WINDROW",
    "COMPOST",
    "DRYALFALFA_WINDROW",
    "DRYCLOVER_WINDROW",
    "ORGANICWASTE",
    "POTATO_WASHED",
    "RICE_HUSK",
}

GLOBAL_L10N_KEYS = {
    "unit_literShort",
}

EXPECTED_PACKAGE_ROOT_FILES = {
    "icon.dds",
    "modDesc.xml",
    "xml/phobosFillTypes.xml",
}

FORBIDDEN_PACKAGE_PREFIXES = (
    ".git/",
    ".github/",
    "build/",
    "dist/",
    "docs/",
    "mod/",
    "release/",
    "tools/",
)


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def report(self) -> int:
        for warning in self.warnings:
            print(f"::warning::{warning}")
        for error in self.errors:
            print(f"::error::{error}")
        if self.errors:
            print(f"Validation failed with {len(self.errors)} error(s).")
            return 1
        print("Validation passed.")
        return 0


def parse_xml_file(path: Path, validation: Validation) -> ET.ElementTree | None:
    try:
        return ET.parse(path)
    except ET.ParseError as exc:
        validation.error(f"XML parse failed: {path}: {exc}")
    return None


def iter_xml_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.xml"))


def local_filltypes(mod_root: Path, validation: Validation) -> set[str]:
    result: set[str] = set()
    for path in sorted((mod_root / "xml").glob("*.xml")):
        tree = parse_xml_file(path, validation)
        if tree is None:
            continue
        for node in tree.findall(".//fillType"):
            name = node.get("name")
            if name:
                result.add(name.upper())
    return result


def validate_moddesc_references(mod_root: Path, root: ET.Element, validation: Validation) -> None:
    icon_filename = (root.findtext("iconFilename") or "").strip()
    if icon_filename and not (mod_root / icon_filename).is_file():
        validation.error(f"modDesc.xml references missing iconFilename: {icon_filename}")

    for node in root.findall("./fillTypes"):
        filename = node.get("filename", "").strip()
        if filename and not (mod_root / filename).is_file():
            validation.error(f"modDesc.xml references missing fillTypes file: {filename}")

    for node in root.findall("./storeItems/storeItem"):
        filename = node.get("xmlFilename", "").strip()
        if filename and not (mod_root / filename).is_file():
            validation.error(f"modDesc.xml references missing storeItem file: {filename}")


def moddesc_data(mod_root: Path, validation: Validation) -> tuple[set[str], set[str], dict[str, str]]:
    moddesc_path = mod_root / "modDesc.xml"
    tree = parse_xml_file(moddesc_path, validation)
    if tree is None:
        return set(), set(), {}

    root = tree.getroot()
    version = (root.findtext("version") or "").strip()
    if not VERSION_RE.match(version):
        validation.error(f"modDesc.xml version must be X.Y.Z.W, found '{version}'")

    validate_moddesc_references(mod_root, root, validation)

    dependencies = {
        (node.text or "").strip()
        for node in root.findall("./dependencies/dependency")
        if (node.text or "").strip()
    }
    l10n_keys = {
        node.get("name", "")
        for node in root.findall("./l10n/text")
        if node.get("name")
    }
    construction_tabs = {
        node.get("name", ""): node.get("categoryName", "")
        for node in root.findall("./constructionCategories/tab")
        if node.get("name")
    }
    return dependencies, l10n_keys, construction_tabs


def collect_filltype_refs(path: Path, tree: ET.ElementTree) -> set[str]:
    refs: set[str] = set()
    for node in tree.iter():
        for attr_name, value in node.attrib.items():
            if attr_name.lower() not in {"filltype", "filltypes"}:
                continue
            for name in value.split():
                if name:
                    refs.add(name.upper())
    return refs


def collect_l10n_refs(tree: ET.ElementTree) -> set[str]:
    refs: set[str] = set()
    for node in tree.iter():
        for value in node.attrib.values():
            refs.update(L10N_RE.findall(value))
        if node.text:
            refs.update(L10N_RE.findall(node.text))
    return refs


def validate_self_mod_refs(path: Path, mod_root: Path, repo_root: Path, validation: Validation) -> None:
    text = path.read_text(encoding="utf-8")
    for match in SELF_MOD_REF_RE.finditer(text):
        referenced = match.group(1)
        if not (mod_root / referenced).is_file():
            validation.error(
                f"Missing Phobos-owned asset reference '{referenced}' in {path.relative_to(repo_root)}"
            )
        if referenced.lower().startswith("hud/") and referenced.lower().endswith(".png"):
            validation.error(
                f"Phobos HUD texture should be DDS with mipmaps, not PNG: {path.relative_to(repo_root)}"
            )


def production_filltypes(tree: ET.ElementTree) -> set[str]:
    refs: set[str] = set()
    productions = tree.find(".//productions")
    if productions is None:
        return refs
    for node in productions.iter():
        fill_type = node.get("fillType")
        if fill_type:
            refs.add(fill_type.upper())
    return refs


def storage_filltypes(tree: ET.ElementTree) -> set[str]:
    refs: set[str] = set()
    for node in tree.findall(".//storage/capacity"):
        fill_type = node.get("fillType")
        if fill_type:
            refs.add(fill_type.upper())
    return refs


def count_production_recipes(tree: ET.ElementTree) -> int:
    productions = tree.find(".//productions")
    if productions is None:
        return 0
    return len(productions.findall("./production"))


def validate_construction_tabs(
    path: Path,
    repo_root: Path,
    tree: ET.ElementTree,
    construction_tabs: dict[str, str],
    validation: Validation,
) -> None:
    for brush in tree.findall("./storeData/brush"):
        tab = (brush.findtext("tab") or "").strip()
        category = (brush.findtext("category") or "").strip()
        relative_path = path.relative_to(repo_root)

        if not tab:
            validation.error(f"Phobos placeable is missing a construction brush tab: {relative_path}")
            continue

        if not tab.startswith("phobos"):
            validation.error(
                f"Phobos placeable uses non-Phobos construction tab '{tab}': {relative_path}"
            )
            continue

        declared_category = construction_tabs.get(tab)
        if declared_category is None:
            validation.error(f"Phobos construction tab '{tab}' is not declared in modDesc.xml: {relative_path}")
        elif category and declared_category != category:
            validation.error(
                f"Phobos construction tab '{tab}' is declared for '{declared_category}' "
                f"but used under '{category}': {relative_path}"
            )


def validate_source(repo_root: Path, validation: Validation) -> None:
    mod_root = repo_root / "mod"
    if not mod_root.is_dir():
        validation.error(f"Missing mod source directory: {mod_root}")
        return

    xml_files = iter_xml_files(mod_root)
    if not xml_files:
        validation.error("No XML files found under mod/")
        return

    dependencies, l10n_keys, construction_tabs = moddesc_data(mod_root, validation)
    known_filltypes = set(VANILLA_FILLTYPES)
    known_filltypes.update(local_filltypes(mod_root, validation))
    for dependency in dependencies:
        known_filltypes.update(DEPENDENCY_FILLTYPES.get(dependency, set()))

    for dependency, filltypes in DEPENDENCY_FILLTYPES.items():
        used = False
        for path in sorted((mod_root / "placeables").rglob("*.xml")):
            tree = parse_xml_file(path, validation)
            if tree is not None and collect_filltype_refs(path, tree).intersection(filltypes):
                used = True
        if used and dependency not in dependencies:
            validation.error(f"Dependency fillType used but dependency is not declared: {dependency}")

    for path in xml_files:
        tree = parse_xml_file(path, validation)
        if tree is None:
            continue

        validate_self_mod_refs(path, mod_root, repo_root, validation)

        missing_l10n = sorted(collect_l10n_refs(tree) - l10n_keys - GLOBAL_L10N_KEYS)
        for key in missing_l10n:
            validation.error(f"Missing l10n key '{key}' referenced by {path.relative_to(repo_root)}")

    for path in sorted((mod_root / "placeables").rglob("*.xml")):
        tree = parse_xml_file(path, validation)
        if tree is None:
            continue

        refs = collect_filltype_refs(path, tree)
        unknown = sorted(refs - known_filltypes)
        for fill_type in unknown:
            validation.error(f"Unknown active placeable fillType '{fill_type}' in {path.relative_to(repo_root)}")

        denied = sorted(refs.intersection(OPTIONAL_FILLTYPE_DENYLIST))
        for fill_type in denied:
            validation.error(
                f"Optional fillType '{fill_type}' appears in core placeable XML: {path.relative_to(repo_root)}"
            )

        validate_construction_tabs(path, repo_root, tree, construction_tabs, validation)

        if tree.getroot().get("type") == "productionPoint" or tree.find(".//productions") is not None:
            storage_only = sorted(storage_filltypes(tree) - production_filltypes(tree))
            for fill_type in storage_only:
                validation.error(
                    f"Storage-only fillType '{fill_type}' in production point {path.relative_to(repo_root)}"
                )

        recipe_count = count_production_recipes(tree)
        if recipe_count > 24:
            validation.error(f"{path.relative_to(repo_root)} has {recipe_count} recipes; hard target is 24")
        elif recipe_count > 18:
            validation.warn(f"{path.relative_to(repo_root)} has {recipe_count} recipes; soft target is 18")

    custom_filltype_count = len(local_filltypes(mod_root, validation))
    if custom_filltype_count > 5:
        validation.error(f"{custom_filltype_count} Phobos-owned fillTypes defined; hard target is 5")
    elif custom_filltype_count > 3:
        validation.warn(f"{custom_filltype_count} Phobos-owned fillTypes defined; soft target is 3")


def validate_package(package_path: Path, validation: Validation, soft_size_limit: int) -> None:
    if not package_path.is_file():
        validation.error(f"Package not found: {package_path}")
        return

    package_size = package_path.stat().st_size
    if package_size > soft_size_limit:
        validation.warn(
            f"Package size is {package_size} bytes; XML-only soft target is {soft_size_limit} bytes"
        )

    try:
        with zipfile.ZipFile(package_path) as archive:
            names = sorted(info.filename for info in archive.infolist())
    except zipfile.BadZipFile as exc:
        validation.error(f"Invalid zip file: {package_path}: {exc}")
        return

    missing = sorted(EXPECTED_PACKAGE_ROOT_FILES - set(names))
    for entry in missing:
        validation.error(f"Package is missing expected root entry: {entry}")

    for name in names:
        if "\\" in name:
            validation.error(f"Package entry uses backslash instead of slash: {name}")
        lower = name.lower()
        for prefix in FORBIDDEN_PACKAGE_PREFIXES:
            if lower.startswith(prefix):
                validation.error(f"Package contains forbidden repository path: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FS25_BgaExtensions source or package")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--package", help="Optional package zip to validate")
    parser.add_argument(
        "--package-size-soft-limit",
        type=int,
        default=1_000_000,
        help="Soft package size warning threshold in bytes",
    )
    args = parser.parse_args()

    validation = Validation()
    repo_root = Path(args.repo_root).resolve()

    validate_source(repo_root, validation)
    if args.package:
        validate_package(Path(args.package).resolve(), validation, args.package_size_soft_limit)

    return validation.report()


if __name__ == "__main__":
    sys.exit(main())
