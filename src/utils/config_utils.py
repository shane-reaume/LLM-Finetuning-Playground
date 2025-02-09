import yaml
import os

def load_config(config_path: str = "config/default.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
