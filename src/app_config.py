import os
import re
import yaml

class AppConfig:
    def __init__(self, config: dict[str, str] = {}):
        self.config = config
    
    @staticmethod
    def from_file(file_path: dict[str, str]):
        try:
            with open(file_path, 'r') as f:
                configuration = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: The configuration file '{file_path}' was not found.")
            return None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return None
        return AppConfig(configuration)
    
    def get(self, *properties: str) -> str | dict[str, str]:
        values = {}
        for property in properties:            
            if property not in self.config:
                raise KeyError(f"Property: \"{property}\" is not set in config")
            
            value = self.config[property]
            
            env_pattern = r"\$\{(\w+)\}"
            match = re.match(env_pattern, value)
            if match is not None:
                env_var = match.group(1)
                value = os.environ.get(env_var) or match.group(0)
            
            values[property] = value
            
        return values[0] if len(values) == 1 else values
    
    def getAll(self) -> dict[str, str]:
        return {x: self.get(x) for x in self.config}
    
    def __getitem__(self, key: str) -> str:
        return self.get(key)
    
    def __setitem__(self, key: str, value: str) -> None:
        self.config[key] = value
