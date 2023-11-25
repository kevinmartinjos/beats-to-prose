from typing import Union
from argparse import ArgumentParser
import pprint

from common.constants import GENERATOR_SIMPLE
from common.utils import read_config, read_beats
from data_structures.prompt import PromptCollection
from generators.simple_generator import SimpleGenerator


def get_generator(generator_type: str) -> Union[SimpleGenerator.__class__]:
    if generator_type == GENERATOR_SIMPLE:
        return SimpleGenerator


def main(beats_file: str, config_file: str) -> None:
    beats = read_beats(beats_file)
    config = read_config(config_file)

    prompt_collection = PromptCollection.from_beats(beats, config.preamble)
    generator_cls = get_generator(config.generator_type)
    generator: Union[SimpleGenerator] = generator_cls(config.model_name, prompt_collection)
    prose: str = generator.generate()

    pprint.pprint(prose)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-b", "--beats", help="Path to a text file containing beats. Each beat should be a separate line")
    parser.add_argument("-c", "--config", help="Path to a yml config")
    args = parser.parse_args()
    main(args.beats, args.config)