from typing import Union
from argparse import ArgumentParser
import pprint

from common.constants import GENERATOR_SIMPLE, GENERATOR_SEQUENTIAL, GENERATOR_INTERACTIVE
from common.utils import read_config, read_beats
from data_structures.prompt import PromptCollection
from generators.interactive_generator import InteractiveGenerator
from generators.sequential_generator import SequentialGenerator
from generators.simple_generator import SimpleGenerator


def get_generator(generator_type: str) -> Union[SimpleGenerator.__class__]:
    if generator_type == GENERATOR_SIMPLE:
        return SimpleGenerator
    elif generator_type == GENERATOR_SEQUENTIAL:
        return SequentialGenerator
    elif generator_type == GENERATOR_INTERACTIVE:
        return InteractiveGenerator
    else:
        raise ValueError(f"Unknown generator type: {generator_type}")


def main(beats_file: str, config_file: str) -> None:
    beats = read_beats(beats_file)
    config = read_config(config_file)

    prompt_collection = PromptCollection.from_beats(beats, config.preamble)
    generator_cls = get_generator(config.generator_type)
    generator: Union[SimpleGenerator] = generator_cls(
        config.model_name, prompt_collection, config.max_tokens_per_beat, config.num_choices, config.seed
    )
    prose: str = generator.generate()

    pprint.pprint(prose)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-b", "--beats", help="Path to a text file containing beats. Each beat should be a separate line")
    parser.add_argument("-c", "--config", help="Path to a yml config")
    args = parser.parse_args()
    main(args.beats, args.config)