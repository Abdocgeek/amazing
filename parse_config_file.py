from typing import Dict, Any


def parse_config(filename: str) -> Dict[str, Any]:
    """ Parse your config file

    Args:
        filename: name of the configfile

    Returns:
        Dictionary with parsed configuration values.

    Raises:
        ValueError: If required keys are missing or values are invalid.
        TypeError: If entry and exit are the same point.
    """
    config = {}

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line or line.count("=") != 1:
                raise ValueError(f"Invalid line: {line}")
            key, value = line.split("=")
            if " " in key or "\t" in key:
                raise ValueError("Key cannot contain spaces")
            if " " in value or "\t" in value:
                raise ValueError("Value cannot contain spaces")

            config[key.strip()] = value.strip()
    required = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    ]

    for key in required:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")
    width = int(config["WIDTH"])
    height = int(config["HEIGHT"])
    entry_x, entry_y = map(int, config["ENTRY"].split(","))
    exit_x, exit_y = map(int, config["EXIT"].split(","))
    perfect: str | bool = config["PERFECT"]
    output_file = config["OUTPUT_FILE"]
    tmp_file = output_file.split(".", 1)
    if (len(tmp_file) != 2 or tmp_file[1] != "txt"):
        raise ValueError("OUT_PUT file must be txt extention.")

    if "ALGO" not in config.keys():
        algo = "DFS"
    else:
        algo = config["ALGO"]
    if "SEED" not in config.keys():
        seed = None
    else:
        try:
            seed = int(config["SEED"])
        except Exception:
            seed = None
    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive greater then 0.")
    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ValueError("ENTRY out of bounds")
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ValueError("EXIT out of bounds")
    if perfect in ['True', 'False']:
        if perfect == 'True':
            perfect = True
        else:
            perfect = False
    else:
        raise ValueError("Perfect should be True or False.")

    if entry_x == exit_x and entry_y == exit_y:
        raise TypeError(
            "Entry and Exit must be separated or make the maze abit bigger")

    return {
        "width": width,
        "height": height,
        "entry": (entry_y, entry_x),
        "exit": (exit_y, exit_x),
        "output_file": output_file,
        "perfect": perfect,
        "algo": algo,
        "seed": seed
    }
