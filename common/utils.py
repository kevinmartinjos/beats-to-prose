import os
from typing import List
from omegaconf import OmegaConf, DictConfig


def read_beats(beats_file: str) -> List[str]:
    """
    Reads in a list of lines from a file. Each line represents a "beat"
    :param beats_file:
    :return: List of strings
    """
    beats = []
    with open(beats_file) as f:
        for line in f:
            if line.strip():
                beats.append(line)

    return beats


def read_config(config_file: str) -> DictConfig:
    """
    Parses a yml file to omegaconf dict config
    :param config_file: yaml file
    :return: parsed config
    """

    return OmegaConf.load(config_file)


def get_openrouter_api_key() -> str:
    return os.environ['OPENROUTER_KEY']
