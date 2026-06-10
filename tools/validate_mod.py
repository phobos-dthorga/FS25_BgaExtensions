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

DATA_PACK_API_VERSION = "1"
DATA_PACK_ROUTE_CAP = 12
DATA_PACK_TARGET_CAPS = {
    "biomassIntake": 6,
    "wetSubstratePrep": 8,
    "dryFuelProcessor": 6,
}
DATA_PACK_TIERS = {
    "emergency",
    "exceptional",
    "excellent",
    "fair",
    "good",
}
DATA_PACK_TEMPLATE_TARGETS = {
    "forageSilage": "biomassIntake",
    "greenMash": "wetSubstratePrep",
    "hayPelletFuel": "dryFuelProcessor",
    "residueMash": "wetSubstratePrep",
    "rootMash": "wetSubstratePrep",
    "strawPelletFuel": "dryFuelProcessor",
    "strawPretreatment": "biomassIntake",
    "sweetMash": "wetSubstratePrep",
}
DATA_PACK_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
DATA_PACK_FILLTYPE_RE = re.compile(r"^[A-Z0-9_]+$")
DATA_PACK_ROOT_ATTRS = {"apiVersion", "author", "packId", "title"}
DATA_PACK_ROUTE_ATTRS = {"id", "inputFillType", "target", "template", "tier"}

IDENTITY_DISPATCHER_PRODUCTIONS = {
    "gbwProcessSupplyAdditiveDispatch": {"SILAGE_ADDITIVE": 1.0},
    "gbwProcessSupplyMolassesDispatch": {"MOLASSES": 100.0},
    "gbwProcessSupplyWaterDispatch": {"WATER": 500.0},
}
IDENTITY_DISPATCHER_FILE = "planetProcessSupplyHub.xml"

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
    if not icon_filename:
        validation.error("modDesc.xml is missing required iconFilename")
    elif not (mod_root / icon_filename).is_file():
        validation.error(f"modDesc.xml references missing iconFilename: {icon_filename}")

    for node in root.findall("./fillTypes"):
        filename = node.get("filename", "").strip()
        if filename and not (mod_root / filename).is_file():
            validation.error(f"modDesc.xml references missing fillTypes file: {filename}")

    for node in root.findall("./extraSourceFiles/sourceFile"):
        filename = node.get("filename", "").strip()
        if filename and not (mod_root / filename).is_file():
            validation.error(f"modDesc.xml references missing sourceFile: {filename}")

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


def production_amounts(production: ET.Element, section: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for node in production.findall(f"./{section}/*"):
        fill_type = (node.get("fillType") or "").upper()
        if not fill_type:
            continue
        result[fill_type] = result.get(fill_type, 0.0) + float(node.get("amount", "0"))
    return result


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
    refs.update(trigger_filltypes(tree, ".//sellingStation/palletTrigger"))
    return refs


def load_trigger_filltypes(tree: ET.ElementTree) -> set[str]:
    return trigger_filltypes(tree, ".//loadingStation/loadTrigger")


def i3d_mapping_ids(tree: ET.ElementTree) -> set[str]:
    return {
        node.get("id", "")
        for node in tree.findall(".//i3dMapping")
        if node.get("id")
    }


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
        validation.error(f"Production input '{fill_type}' is not accepted by unload, bale, or pallet triggers in {relative_path}")

    for fill_type in sorted(outputs - loadable_outputs):
        validation.error(f"Production output '{fill_type}' is not available from load triggers in {relative_path}")


def validate_identity_dispatcher_rules(
    path: Path,
    repo_root: Path,
    tree: ET.ElementTree,
    validation: Validation,
) -> None:
    relative_path = path.relative_to(repo_root)

    for production in tree.findall(".//productions/production"):
        production_id = production.get("id", "")
        inputs = production_amounts(production, "inputs")
        outputs = production_amounts(production, "outputs")
        shared_filltypes = set(inputs).intersection(outputs)
        if not shared_filltypes:
            continue

        allowed = IDENTITY_DISPATCHER_PRODUCTIONS.get(production_id)
        if path.name != IDENTITY_DISPATCHER_FILE or allowed is None:
            validation.error(
                f"Production '{production_id}' has same input/output fillType(s) "
                f"{', '.join(sorted(shared_filltypes))} in {relative_path}; only "
                f"{IDENTITY_DISPATCHER_FILE} dispatcher recipes may do this"
            )
            continue

        allowed_filltypes = set(allowed)
        if set(inputs) != allowed_filltypes or set(outputs) != allowed_filltypes:
            validation.error(
                f"Dispatcher production '{production_id}' must only pass through "
                f"{', '.join(sorted(allowed_filltypes))} in {relative_path}"
            )
            continue

        for fill_type, expected_amount in allowed.items():
            if inputs.get(fill_type) != expected_amount or outputs.get(fill_type) != expected_amount:
                validation.error(
                    f"Dispatcher production '{production_id}' must pass through {expected_amount:g} l "
                    f"of {fill_type} per cycle in {relative_path}"
                )

        cycles = float(production.get("cyclesPerHour", "0"))
        if cycles != 60.0:
            validation.error(
                f"Dispatcher production '{production_id}' must run at 60 cycles/hour in {relative_path}"
            )


def validate_process_supply_hub_trigger_rules(
    path: Path,
    repo_root: Path,
    tree: ET.ElementTree,
    validation: Validation,
) -> None:
    if path.name != IDENTITY_DISPATCHER_FILE:
        return

    relative_path = path.relative_to(repo_root)
    expected_supplies = {"MOLASSES", "SILAGE_ADDITIVE", "WATER"}
    mapping_ids = i3d_mapping_ids(tree)

    required_mappings = {
        "palletTrigger",
        "unloadTriggerWater",
        "unloadTriggerWaterAiNode",
        "unloadTriggerWaterMarker",
    }
    for mapping_id in sorted(required_mappings - mapping_ids):
        validation.error(f"Process Supply Hub is missing i3d mapping '{mapping_id}' in {relative_path}")

    forbidden_mappings = {"unloadTriggerMixer", "unloadTriggerMixerMarker"}
    for mapping_id in sorted(forbidden_mappings.intersection(mapping_ids)):
        validation.error(f"Process Supply Hub must not use mixer unload mapping '{mapping_id}' in {relative_path}")

    water_marker = None
    pallet_marker = None
    for marker in tree.findall("./triggerMarkers/triggerMarker"):
        node = marker.get("node", "")
        if node == "unloadTriggerWaterMarker":
            water_marker = marker
        elif node == "palletTrigger":
            pallet_marker = marker

    if water_marker is None:
        validation.error(f"Process Supply Hub needs a water unload marker in {relative_path}")
    else:
        marker_file = water_marker.get("filename", "")
        if marker_file != "$data/shared/assets/marker/markerIconWater.i3d":
            validation.error(f"Process Supply Hub water marker must use markerIconWater.i3d in {relative_path}")
        if water_marker.get("adjustToGround", "") != "true":
            validation.error(f"Process Supply Hub water marker must adjust to ground in {relative_path}")

    if pallet_marker is None:
        validation.error(f"Process Supply Hub needs a pallet unload marker in {relative_path}")
    else:
        marker_file = pallet_marker.get("filename", "")
        if marker_file != "$data/shared/assets/marker/markerIconUnload.i3d":
            validation.error(f"Process Supply Hub pallet marker must use markerIconUnload.i3d in {relative_path}")

    water_unloads = [
        node
        for node in tree.findall(".//sellingStation/unloadTrigger")
        if node.get("exactFillRootNode") == "unloadTriggerWater"
    ]
    if len(water_unloads) != 1:
        validation.error(f"Process Supply Hub must have exactly one water unloadTrigger in {relative_path}")
    else:
        water_filltypes = set(water_unloads[0].get("fillTypes", "").split())
        if water_filltypes != {"WATER"}:
            validation.error(f"Process Supply Hub water unloadTrigger must accept only WATER in {relative_path}")
        if water_unloads[0].get("aiNode", "") != "unloadTriggerWaterAiNode":
            validation.error(f"Process Supply Hub water unloadTrigger must use unloadTriggerWaterAiNode in {relative_path}")

    for node in tree.findall(".//sellingStation/unloadTrigger"):
        if node.get("exactFillRootNode") == "unloadTriggerMixer":
            validation.error(f"Process Supply Hub must not use the mixer unload trigger in {relative_path}")

    pallet_triggers = [
        node
        for node in tree.findall(".//sellingStation/palletTrigger")
        if node.get("triggerNode") == "palletTrigger"
    ]
    if len(pallet_triggers) != 1:
        validation.error(f"Process Supply Hub must have exactly one palletTrigger in {relative_path}")
    else:
        pallet_filltypes = set(pallet_triggers[0].get("fillTypes", "").split())
        if pallet_filltypes != expected_supplies:
            validation.error(
                f"Process Supply Hub palletTrigger must accept "
                f"{', '.join(sorted(expected_supplies))} in {relative_path}"
            )


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


def validate_data_pack_file(path: Path, repo_root: Path, validation: Validation) -> None:
    tree = parse_xml_file(path, validation)
    if tree is None:
        return

    root = tree.getroot()
    relative_path = path.relative_to(repo_root)
    if root.tag != "gbwDataPack":
        validation.error(f"Data pack XML root must be gbwDataPack: {relative_path}")
        return

    for attr in root.attrib:
        if attr not in DATA_PACK_ROOT_ATTRS:
            validation.error(f"Unknown gbwDataPack attribute '{attr}' in {relative_path}")

    api_version = (root.get("apiVersion") or "").strip()
    if api_version != DATA_PACK_API_VERSION:
        validation.error(
            f"Data pack apiVersion must be '{DATA_PACK_API_VERSION}', found '{api_version}' in {relative_path}"
        )

    pack_id = (root.get("packId") or "").strip()
    if not DATA_PACK_ID_RE.match(pack_id):
        validation.error(f"Data pack packId must match {DATA_PACK_ID_RE.pattern}: {relative_path}")

    if not (root.get("title") or "").strip():
        validation.error(f"Data pack title is required: {relative_path}")
    if not (root.get("author") or "").strip():
        validation.error(f"Data pack author is required: {relative_path}")

    allowed_children = {"routes"}
    for child in root:
        if child.tag not in allowed_children:
            validation.error(f"Unknown gbwDataPack child '{child.tag}' in {relative_path}")

    routes_node = root.find("./routes")
    if routes_node is None:
        validation.error(f"Data pack requires a routes node: {relative_path}")
        return

    route_ids: set[str] = set()
    route_count = 0
    target_counts = {target: 0 for target in DATA_PACK_TARGET_CAPS}

    for child in routes_node:
        if child.tag != "route":
            validation.error(f"Unknown routes child '{child.tag}' in {relative_path}")
            continue

        route_count += 1
        for attr in child.attrib:
            if attr not in DATA_PACK_ROUTE_ATTRS:
                validation.error(f"Unknown data-pack route attribute '{attr}' in {relative_path}")

        route_id = (child.get("id") or "").strip()
        if not DATA_PACK_ID_RE.match(route_id):
            validation.error(f"Data-pack route id must match {DATA_PACK_ID_RE.pattern}: {relative_path}")
        elif route_id in route_ids:
            validation.error(f"Duplicate data-pack route id '{route_id}' in {relative_path}")
        else:
            route_ids.add(route_id)

        fill_type = (child.get("inputFillType") or "").strip()
        if not DATA_PACK_FILLTYPE_RE.match(fill_type):
            validation.error(f"Data-pack route '{route_id}' has invalid inputFillType '{fill_type}' in {relative_path}")

        target = (child.get("target") or "").strip()
        if target not in DATA_PACK_TARGET_CAPS:
            validation.error(f"Data-pack route '{route_id}' has unknown target '{target}' in {relative_path}")
        else:
            target_counts[target] += 1

        template = (child.get("template") or "").strip()
        expected_target = DATA_PACK_TEMPLATE_TARGETS.get(template)
        if expected_target is None:
            validation.error(f"Data-pack route '{route_id}' has unknown template '{template}' in {relative_path}")
        elif target and target != expected_target:
            validation.error(
                f"Data-pack route '{route_id}' template '{template}' requires target '{expected_target}', found '{target}' in {relative_path}"
            )

        tier = (child.get("tier") or "").strip()
        if tier not in DATA_PACK_TIERS:
            validation.error(f"Data-pack route '{route_id}' has unknown tier '{tier}' in {relative_path}")

    if route_count == 0:
        validation.error(f"Data pack must define at least one route: {relative_path}")
    if route_count > DATA_PACK_ROUTE_CAP:
        validation.error(f"Data pack has {route_count} routes; hard cap is {DATA_PACK_ROUTE_CAP}: {relative_path}")

    for target, count in sorted(target_counts.items()):
        cap = DATA_PACK_TARGET_CAPS[target]
        if count > cap:
            validation.error(
                f"Data pack target '{target}' has {count} routes; hard cap is {cap}: {relative_path}"
            )


def validate_data_pack_files(mod_root: Path, repo_root: Path, validation: Validation) -> None:
    for path in sorted(mod_root.rglob("gbwDataPack.xml")):
        validate_data_pack_file(path, repo_root, validation)


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
    validate_data_pack_files(mod_root, repo_root, validation)

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
            validate_identity_dispatcher_rules(path, repo_root, tree, validation)
            validate_process_supply_hub_trigger_rules(path, repo_root, tree, validation)
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

    for node in root.findall("./extraSourceFiles/sourceFile"):
        filename = node.get("filename", "").strip()
        if filename:
            expected.add(filename.replace("\\", "/"))

    for node in root.findall("./storeItems/storeItem"):
        filename = node.get("xmlFilename", "").strip()
        if filename:
            expected.add(filename.replace("\\", "/"))

    if "gbwDataPack.xml" in names:
        expected.add("gbwDataPack.xml")

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
