import yaml

def load_tests(path):
    with open(path) as f:
        return yaml.safe_load(f)
