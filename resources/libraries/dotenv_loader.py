from dotenv import dotenv_values

def load_env(file_path):
    """Load environment variables from .env file and return as a dictionary."""
    env_vars = dotenv_values(file_path)
    print("Loaded variables:", env_vars)  # Logovanie načítaných premenných
    return env_vars
