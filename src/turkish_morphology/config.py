"""Read the initial experiment contract without importing any ML libraries."""

from math import isclose
from pathlib import Path
import re
import tomllib


TARGETS = {"Number", "Case", "Possession", "Person[psor]", "Number[psor]"}


def load_config(path: Path) -> dict:
    with path.open("rb") as stream:
        config = tomllib.load(stream)
    try:
        experiment, data = config["experiment"], config["data"]
        if not isinstance(experiment["name"], str) or not experiment["name"].strip():
            raise ValueError("Experiment name must be nonblank.")
        seeds = experiment["seeds"]
        if not isinstance(seeds, list) or not seeds or any(type(s) is not int or s < 0 for s in seeds):
            raise ValueError("Seeds must be a nonempty list of nonnegative integers.")
        if len(set(seeds)) != len(seeds):
            raise ValueError("Seeds must be unique.")
        targets = experiment["targets"]
        if not isinstance(targets, list) or not targets or any(t not in TARGETS for t in targets):
            raise ValueError("Targets must come from the nominal feature contract.")
        if len(set(targets)) != len(targets):
            raise ValueError("Targets must be unique.")
        if experiment["primary_metric"] != "macro_f1":
            raise ValueError("The current protocol requires macro_f1 as the primary metric.")
        if data["split_unit"] != "pair_id" or data["schema_version"] != "0.1.0":
            raise ValueError("The current protocol requires pair_id splits and schema v0.1.0.")
        if data["condition"] not in {"root_generalization", "composition_holdout"}:
            raise ValueError("Unknown generalization condition.")
        fractions = [data[f"{split}_fraction"] for split in ("train", "dev", "test")]
        if any(type(f) not in (float, int) or not 0 < f < 1 for f in fractions):
            raise ValueError("Split fractions must each lie between 0 and 1.")
        if not isclose(sum(fractions), 1.0):
            raise ValueError("Split fractions must sum to 1.")
        if config["probe"]["selection_split"] != "dev":
            raise ValueError("Probe model selection must use the dev partition.")
        if config["representation"]["pooling"] not in {"mean", "first", "last"}:
            raise ValueError("Unknown pooling mode.")
        if config["evaluation"]["bootstrap_unit"] != "pair_id":
            raise ValueError("Bootstrap resampling must use root pairs.")
        models = config["models"]
        if not isinstance(models, list) or not models:
            raise ValueError("At least one model definition is required.")
        names = set()
        for model in models:
            if model["name"] in names:
                raise ValueError("Model names must be unique.")
            names.add(model["name"])
            if type(model["enabled"]) is not bool:
                raise ValueError("Model enabled must be a boolean.")
            if not all(isinstance(model[k], str) and model[k].strip() for k in ("name", "checkpoint", "revision")):
                raise ValueError("Models require nonblank names, checkpoints, and revisions.")
        if not any(model["enabled"] for model in models):
            raise ValueError("Enable at least one model.")
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Missing or malformed configuration field: {exc}") from exc
    return config


def require_pinned_models(config: dict) -> None:
    for model in config["models"]:
        if model["enabled"] and re.fullmatch(r"[0-9a-f]{40}", model["revision"]) is None:
            raise ValueError(
                f"{model['name']}: replace UNRESOLVED/branch names with a verified 40-character commit revision."
            )
