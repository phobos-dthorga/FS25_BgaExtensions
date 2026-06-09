#!/usr/bin/env python3
"""Static validation for FS25_BgaExtensions.

These checks intentionally cover only what can be proven without launching FS25.
The game log and disposable-save tests remain the authority for runtime behavior.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


VERSION_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
L10N_RE = re.compile(r"\$l10n_([A-Za-z0-9_]+)")
SELF_MOD_REF_RE = re.compile(r"\$moddir\$FS25_BgaExtensions/([^\"'\s<>]+)")
SELF_MOD_ASSET_PREFIX = "$moddir$FS25_BgaExtensions/"

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
    "WATER",
    "WOODCHIPS",
}

DEPENDENCY_FILLTYPES = {
    "FS25_BgaExtensions": {
        "GBW_GREEN_MASH",
        "GBW_RESIDUE_MASH",
        "GBW_ROOT_MASH",
        "GBW_SWEET_MASH",
    },
    "FS25_PlanET_BGA_Modular": {
        "LIQUIDMANURE1",
        "MANURE_IN",
        "SILAGE_IN",
        "SUGARBEETCUT_IN",
    },
    "FS25_potatoWasher": {
        "POTATO_WASHED",
    },
    "FS25_RicePackagingFactory": {
        "RICE_HUSK",
    },
    "FS25_orchardsAndGreenhouses_crossplay": {
        "COMPOST",
        "ORGANICWASTE",
    },
    "FS25_Nordkirchen_x4": {
        "COMPOST",
    },
    "FS25_The_Mechet": {
        "COMPOST",
        "COMPOST_RAW",
    },
    "FS25_Potato_Chips_Factory_MF": {
        "ORGANICWASTE",
    },
    "pdlc_strawHarvestPack": {
        "HAY_PELLETS",
        "MOLASSES",
        "STRAW_PELLETS",
    },
}

OPTIONAL_FILLTYPE_PROVIDERS = {
    "COMPOST": {
        "FS25_Nordkirchen_x4",
        "FS25_orchardsAndGreenhouses_crossplay",
        "FS25_The_Mechet",
    },
    "COMPOST_RAW": {
        "FS25_The_Mechet",
    },
    "ORGANICWASTE": {
        "FS25_orchardsAndGreenhouses_crossplay",
        "FS25_Potato_Chips_Factory_MF",
    },
    "POTATO_WASHED": {
        "FS25_potatoWasher",
    },
    "RICE_HUSK": {
        "FS25_RicePackagingFactory",
    },
}

OPTIONAL_FILLTYPE_DENYLIST = {
    "ALFALFA_WINDROW",
    "CLOVER_WINDROW",
    "COMPOST",
    "COMPOST_RAW",
    "DRYALFALFA_WINDROW",
    "DRYCLOVER_WINDROW",
    "ORGANICWASTE",
    "POTATO_WASHED",
    "RICE_HUSK",
}

DEPENDENCY_CONSTRUCTION_TABS = {
    "FS25_BgaExtensions": {
        "gbwBgaCompatibility": "production",
        "gbwBgaProduction": "production",
        "gbwFuelProcessing": "production",
        "gbwFuelStorage": "buildings",
    },
}

GLOBAL_L10N_KEYS = {
    "unit_literShort",
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


def validate_dds_hud_icon(path: Path, label: str, validation: Validation) -> None:
    if not path.is_file():
        validation.error(f"FillType HUD icon is missing: {label}")
        return

    data = path.read_bytes()
    if len(data) < 128 or data[:4] != b"DDS ":
        validation.error(f"FillType HUD icon must be a DDS file: {label}")
        return

    header_size, flags, height, width, linear_size, _depth, mipmaps = struct.unpack_from("<7I", data, 4)
    pixel_format_size = struct.unpack_from("<I", data, 76)[0]
    pixel_flags = struct.unpack_from("<I", data, 80)[0]
    fourcc = data[84:88]
    rgb_bits = struct.unpack_from("<I", data, 88)[0]
    masks = struct.unpack_from("<4I", data, 92)

    if header_size != 124 or pixel_format_size != 32:
        validation.error(f"FillType HUD icon has an invalid DDS header: {label}")
    if width != 256 or height != 256:
        validation.error(f"FillType HUD icon must be 256x256, found {width}x{height}: {label}")
    if fourcc != b"DXT5" or pixel_flags != 0x4 or rgb_bits != 0:
        validation.error(f"FillType HUD icon must be DXT5-compressed DDS: {label}")
    if masks != (0, 0, 0, 0):
        validation.error(f"FillType HUD icon must use DXT5 color masks: {label}")
    if mipmaps != 1:
        validation.error(f"FillType HUD icon must match FS25 HUD style with one DDS image level, found {mipmaps}: {label}")

    expected_linear_size = ((width + 3) // 4) * ((height + 3) // 4) * 16
    if linear_size != expected_linear_size:
        validation.error(f"FillType HUD icon has an unexpected DXT5 linear size: {label}")

    expected_size = 128 + expected_linear_size
    if len(data) != expected_size:
        validation.error(f"FillType HUD icon DDS byte size is unexpected: {label}")


def validate_filltype_icons(mod_root: Path, repo_root: Path, validation: Validation) -> None:
    for path in sorted((mod_root / "xml").glob("*.xml")):
        tree = parse_xml_file(path, validation)
        if tree is None:
            continue
        for fill_type in tree.findall(".//fillType"):
            name = (fill_type.get("name") or "").strip()
            image = fill_type.find("./image")
            hud_ref = (image.get("hud") if image is not None else "") or ""
            label = f"{name} in {path.relative_to(repo_root)}"

            if not hud_ref:
                validation.error(f"GBW-owned fillType is missing a HUD icon: {label}")
                continue
            if not hud_ref.lower().endswith(".dds"):
                validation.error(f"FillType HUD icon must reference a DDS file: {label}")
                continue
            if not hud_ref.startswith(SELF_MOD_ASSET_PREFIX):
                validation.error(f"FillType HUD icon must be a GBW-owned asset: {label}")
                continue

            relative_asset = hud_ref[len(SELF_MOD_ASSET_PREFIX) :]
            icon_path = mod_root / relative_asset
            validate_dds_hud_icon(icon_path, f"{label}: {relative_asset}", validation)


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
                f"Missing GBW-owned asset reference '{referenced}' in {path.relative_to(repo_root)}"
            )
        if referenced.lower().startswith("hud/") and referenced.lower().endswith(".png"):
            validation.error(
                f"GBW HUD texture should be DDS, not PNG: {path.relative_to(repo_root)}"
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


def production_input_filltypes(tree: ET.ElementTree) -> set[str]:
    refs: set[str] = set()
    for node in tree.findall(".//productions/production/inputs/input"):
        fill_type = node.get("fillType")
        if fill_type:
            refs.add(fill_type.upper())
    return refs


def production_output_filltypes(tree: ET.ElementTree) -> set[str]:
    refs: set[str] = set()
    for node in tree.findall(".//productions/production/outputs/output"):
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


def trigger_filltypes(tree: ET.ElementTree, xpath: str) -> set[str]:
    refs: set[str] = set()
    for node in tree.findall(xpath):
        for name in node.get("fillTypes", "").split():
            if name:
                refs.add(name.upper())
    return refs


def unload_trigger_filltypes(tree: ET.ElementTree) -> set[str]:
    refs = trigger_filltypes(tree, ".//sellingStation/unloadTrigger")
    refs.update(trigger_filltypes(tree, ".//sellingStation/baleTrigger"))
    return refs


def load_trigger_filltypes(tree: ET.ElementTree) -> set[str]:
    return trigger_filltypes(tree, ".//loadingStation/loadTrigger")


def count_production_recipes(tree: ET.ElementTree) -> int:
    productions = tree.find(".//productions")
    if productions is None:
        return 0
    return len(productions.findall("./production"))


def production_record(tree: ET.ElementTree, production_id: str) -> dict[str, object] | None:
    production = tree.find(f".//productions/production[@id='{production_id}']")
    if production is None:
        return None

    def sum_amount(xpath: str, fill_type: str) -> float:
        result = 0.0
        for node in production.findall(xpath):
            if (node.get("fillType") or "").upper() != fill_type.upper():
                continue
            result += float(node.get("amount", "0"))
        return result

    return {
        "id": production_id,
        "cycles": float(production.get("cyclesPerHour", "0")),
        "drygrass_windrow": sum_amount("./inputs/input", "DRYGRASS_WINDROW"),
        "hay_pellets_input": sum_amount("./inputs/input", "HAY_PELLETS"),
        "hay_pellets_output": sum_amount("./outputs/output", "HAY_PELLETS"),
        "molasses": sum_amount("./inputs/input", "MOLASSES"),
        "silage_in": sum_amount("./outputs/output", "SILAGE_IN"),
        "sugarbeetcut_in": sum_amount("./outputs/output", "SUGARBEETCUT_IN"),
        "silage_additive": sum_amount("./inputs/input", "SILAGE_ADDITIVE"),
        "straw": sum_amount("./inputs/input", "STRAW"),
        "straw_pellets_input": sum_amount("./inputs/input", "STRAW_PELLETS"),
        "straw_pellets_output": sum_amount("./outputs/output", "STRAW_PELLETS"),
        "water": sum_amount("./inputs/input", "WATER"),
    }


def require_record(
    path: Path,
    repo_root: Path,
    tree: ET.ElementTree,
    production_id: str,
    validation: Validation,
) -> dict[str, object] | None:
    record = production_record(tree, production_id)
    if record is None:
        validation.error(f"Missing expected production '{production_id}' in {path.relative_to(repo_root)}")
    return record


def require_greater(
    left: float,
    right: float,
    message: str,
    validation: Validation,
) -> None:
    if left <= right:
        validation.error(message)


def validate_fermentation_priority_rules(
    path: Path,
    repo_root: Path,
    tree: ET.ElementTree,
    validation: Validation,
) -> None:
    filename = path.name
    size_prefix_by_file = {
        "planetBiomassIntakeSmall.xml": "gbwSmall",
        "planetBiomassIntakeMedium.xml": "gbwMedium",
        "planetBiomassIntakeLarge.xml": "gbwLarge",
    }
    size_prefix = size_prefix_by_file.get(filename)
    if size_prefix is not None:
        relative_path = path.relative_to(repo_root)
        silage = require_record(path, repo_root, tree, f"{size_prefix}SilageToPlanetSilage", validation)
        chaff = require_record(path, repo_root, tree, f"{size_prefix}ChaffToPlanetSilage", validation)
        chaff_additive = require_record(
            path, repo_root, tree, f"{size_prefix}ChaffAdditiveToPlanetSilage", validation
        )
        grass = require_record(path, repo_root, tree, f"{size_prefix}GrassToPlanetSilage", validation)
        grass_additive = require_record(
            path, repo_root, tree, f"{size_prefix}GrassAdditiveToPlanetSilage", validation
        )
        straw = require_record(path, repo_root, tree, f"{size_prefix}StrawToPlanetSilage", validation)

        if all(record is not None for record in [silage, chaff, chaff_additive, grass, grass_additive, straw]):
            require_greater(
                float(silage["cycles"]),
                float(chaff_additive["cycles"]),
                f"Prepared silage must run faster than chaff with additive in {relative_path}",
                validation,
            )
            require_greater(
                float(chaff_additive["cycles"]),
                float(chaff["cycles"]),
                f"Chaff with additive must run faster than raw chaff in {relative_path}",
                validation,
            )
            require_greater(
                float(silage["silage_in"]),
                float(chaff_additive["silage_in"]),
                f"Prepared silage must yield more usable substrate than chaff with additive in {relative_path}",
                validation,
            )
            require_greater(
                float(chaff_additive["silage_in"]),
                float(chaff["silage_in"]),
                f"Chaff with additive must yield more usable substrate than raw chaff in {relative_path}",
                validation,
            )
            require_greater(
                float(silage["cycles"]),
                float(grass_additive["cycles"]),
                f"Prepared silage must run faster than grass with additive in {relative_path}",
                validation,
            )
            require_greater(
                float(grass_additive["cycles"]),
                float(grass["cycles"]),
                f"Grass with additive must run faster than raw grass in {relative_path}",
                validation,
            )
            require_greater(
                float(silage["silage_in"]),
                float(grass_additive["silage_in"]),
                f"Prepared silage must yield more usable substrate than grass with additive in {relative_path}",
                validation,
            )
            require_greater(
                float(grass_additive["silage_in"]),
                float(grass["silage_in"]),
                f"Grass with additive must yield more usable substrate than raw grass in {relative_path}",
                validation,
            )
            require_greater(
                float(straw["silage_additive"]),
                0.0,
                f"Straw pretreatment must consume SILAGE_ADDITIVE in {relative_path}",
                validation,
            )
            require_greater(
                float(grass["silage_in"]),
                float(straw["silage_in"]),
                f"Fresh grass must yield more usable substrate than assisted straw pretreatment in {relative_path}",
                validation,
            )

    if filename == "planetFermentationVessel.xml":
        relative_path = path.relative_to(repo_root)
        for production in tree.findall(".//productions/production"):
            production_id = production.get("id", "")
            record = production_record(tree, production_id)
            if record is None:
                continue
            if float(record["hay_pellets_input"]) <= 0 and float(record["straw_pellets_input"]) <= 0:
                continue
            require_greater(
                float(record["water"]),
                0.0,
                f"Pellet fermentation '{production_id}' must consume WATER in {relative_path}",
                validation,
            )
            require_greater(
                float(record["silage_additive"]),
                0.0,
                f"Pellet fermentation '{production_id}' must consume SILAGE_ADDITIVE in {relative_path}",
                validation,
            )

        mash_pairs = [
            ("Sweet", "sweet"),
            ("Root", "root"),
            ("Green", "green"),
            ("Residue", "residue"),
        ]
        for production_prefix, message_prefix in mash_pairs:
            plain = require_record(
                path,
                repo_root,
                tree,
                f"gbwFermenter{production_prefix}MashToPlanetBeet",
                validation,
            )
            additive = require_record(
                path,
                repo_root,
                tree,
                f"gbwFermenter{production_prefix}MashAdditiveToPlanetBeet",
                validation,
            )
            if plain is None or additive is None:
                continue
            require_greater(
                float(additive["cycles"]),
                float(plain["cycles"]),
                f"{message_prefix.title()} mash with additive must run faster than plain {message_prefix} mash in {relative_path}",
                validation,
            )
            require_greater(
                float(additive["sugarbeetcut_in"]),
                float(plain["sugarbeetcut_in"]),
                f"{message_prefix.title()} mash with additive must yield more usable substrate than plain {message_prefix} mash in {relative_path}",
                validation,
            )
            require_greater(
                float(additive["silage_additive"]),
                0.0,
                f"{message_prefix.title()} mash additive recipe must consume SILAGE_ADDITIVE in {relative_path}",
                validation,
            )

        hay_pellets = require_record(
            path, repo_root, tree, "gbwFermenterHayPelletsToPlanetSilage", validation
        )
        straw_pellets = require_record(
            path, repo_root, tree, "gbwFermenterStrawPelletsToPlanetSilage", validation
        )
        if hay_pellets is not None and straw_pellets is not None:
            for record, label in [(hay_pellets, "Hay pellets"), (straw_pellets, "Straw pellets")]:
                require_greater(
                    float(record["water"]),
                    0.0,
                    f"{label} fermentation must consume WATER in {relative_path}",
                    validation,
                )
                require_greater(
                    float(record["silage_additive"]),
                    0.0,
                    f"{label} fermentation must consume SILAGE_ADDITIVE in {relative_path}",
                    validation,
                )
            require_greater(
                float(hay_pellets["cycles"]),
                float(straw_pellets["cycles"]),
                f"Hay pellet fermentation must run faster than straw pellet fermentation in {relative_path}",
                validation,
            )
            require_greater(
                float(hay_pellets["silage_in"]),
                float(straw_pellets["silage_in"]),
                f"Hay pellet fermentation must yield more usable substrate than straw pellet fermentation in {relative_path}",
                validation,
            )

    if filename == "planetDryFuelProcessor.xml":
        relative_path = path.relative_to(repo_root)
        straw = require_record(path, repo_root, tree, "gbwDryFuelStrawToPellets", validation)
        hay = require_record(path, repo_root, tree, "gbwDryFuelHayToPellets", validation)
        if straw is not None and hay is not None:
            for record, label in [(straw, "Straw pelletizing"), (hay, "Hay pelletizing")]:
                require_greater(
                    float(record["water"]),
                    0.0,
                    f"{label} must consume WATER in {relative_path}",
                    validation,
                )
                require_greater(
                    float(record["molasses"]),
                    0.0,
                    f"{label} must consume MOLASSES in {relative_path}",
                    validation,
                )
            require_greater(
                float(hay["hay_pellets_output"]),
                0.0,
                f"Hay pelletizing must output HAY_PELLETS in {relative_path}",
                validation,
            )
            require_greater(
                float(straw["straw_pellets_output"]),
                0.0,
                f"Straw pelletizing must output STRAW_PELLETS in {relative_path}",
                validation,
            )
            require_greater(
                float(hay["hay_pellets_output"]),
                float(straw["straw_pellets_output"]),
                f"Hay pelletizing should yield more pellet material than straw pelletizing in {relative_path}",
                validation,
            )


def validate_production_trigger_coverage(
    path: Path,
    repo_root: Path,
    tree: ET.ElementTree,
    validation: Validation,
) -> None:
    inputs = production_input_filltypes(tree)
    outputs = production_output_filltypes(tree)
    if not inputs and not outputs:
        return

    accepted_inputs = unload_trigger_filltypes(tree)
    loadable_outputs = load_trigger_filltypes(tree)
    relative_path = path.relative_to(repo_root)

    for fill_type in sorted(inputs - accepted_inputs):
        validation.error(f"Production input '{fill_type}' is not accepted by unload or bale triggers in {relative_path}")

    for fill_type in sorted(outputs - loadable_outputs):
        validation.error(f"Production output '{fill_type}' is not available from load triggers in {relative_path}")


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
            validation.error(f"GBW placeable is missing a construction brush tab: {relative_path}")
            continue

        if not tab.startswith("gbw"):
            validation.error(
                f"GBW placeable uses non-GBW construction tab '{tab}': {relative_path}"
            )
            continue

        declared_category = construction_tabs.get(tab)
        if declared_category is None:
            validation.error(f"GBW construction tab '{tab}' is not declared in modDesc.xml: {relative_path}")
        elif category and declared_category != category:
            validation.error(
                f"GBW construction tab '{tab}' is declared for '{declared_category}' "
                f"but used under '{category}': {relative_path}"
            )


def validate_source(repo_root: Path, mod_source: str, validation: Validation) -> None:
    source_path = Path(mod_source)
    mod_root = source_path if source_path.is_absolute() else repo_root / source_path
    if not mod_root.is_dir():
        validation.error(f"Missing mod source directory: {mod_root}")
        return

    xml_files = iter_xml_files(mod_root)
    if not xml_files:
        validation.error("No XML files found under mod/")
        return

    dependencies, l10n_keys, construction_tabs = moddesc_data(mod_root, validation)
    known_construction_tabs = dict(construction_tabs)
    for dependency in dependencies:
        known_construction_tabs.update(DEPENDENCY_CONSTRUCTION_TABS.get(dependency, {}))

    local_types = local_filltypes(mod_root, validation)
    validate_filltype_icons(mod_root, repo_root, validation)

    known_filltypes = set(VANILLA_FILLTYPES)
    known_filltypes.update(local_types)
    for dependency in dependencies:
        known_filltypes.update(DEPENDENCY_FILLTYPES.get(dependency, set()))

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
            providers = OPTIONAL_FILLTYPE_PROVIDERS.get(fill_type, set())
            if not providers.intersection(dependencies):
                validation.error(
                    f"Optional fillType '{fill_type}' appears without a declared provider dependency "
                    f"in {path.relative_to(repo_root)}"
                )

        validate_construction_tabs(path, repo_root, tree, known_construction_tabs, validation)

        if tree.getroot().get("type") == "productionPoint" or tree.find(".//productions") is not None:
            validate_production_trigger_coverage(path, repo_root, tree, validation)
            validate_fermentation_priority_rules(path, repo_root, tree, validation)

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

    custom_filltype_count = len(local_types)
    if custom_filltype_count > 5:
        validation.error(f"{custom_filltype_count} GBW-owned fillTypes defined; hard target is 5")
    elif custom_filltype_count > 4:
        validation.warn(f"{custom_filltype_count} GBW-owned fillTypes defined; soft target is 4")


def package_expected_entries(names: set[str], archive: zipfile.ZipFile, validation: Validation) -> set[str]:
    expected = {"modDesc.xml"}
    if "modDesc.xml" not in names:
        return expected

    try:
        root = ET.fromstring(archive.read("modDesc.xml"))
    except ET.ParseError as exc:
        validation.error(f"Package modDesc.xml parse failed: {exc}")
        return expected

    icon_filename = (root.findtext("iconFilename") or "").strip()
    if icon_filename:
        expected.add(icon_filename.replace("\\", "/"))

    for node in root.findall("./fillTypes"):
        filename = node.get("filename", "").strip()
        if filename:
            expected.add(filename.replace("\\", "/"))

    for node in root.findall("./storeItems/storeItem"):
        filename = node.get("xmlFilename", "").strip()
        if filename:
            expected.add(filename.replace("\\", "/"))

    return expected


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
            name_set = set(names)
            expected_entries = package_expected_entries(name_set, archive, validation)
    except zipfile.BadZipFile as exc:
        validation.error(f"Invalid zip file: {package_path}: {exc}")
        return

    missing = sorted(expected_entries - set(names))
    for entry in missing:
        validation.error(f"Package is missing expected entry referenced by modDesc.xml: {entry}")

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
    parser.add_argument("--mod-source", default="mod", help="Mod source folder relative to the repository root")
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

    validate_source(repo_root, args.mod_source, validation)
    if args.package:
        validate_package(Path(args.package).resolve(), validation, args.package_size_soft_limit)

    return validation.report()


if __name__ == "__main__":
    sys.exit(main())
