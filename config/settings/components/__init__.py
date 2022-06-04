from pathlib import Path

from decouple import AutoConfig

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Loading `.env` files
config = AutoConfig(search_path=BASE_DIR.joinpath('config'))
