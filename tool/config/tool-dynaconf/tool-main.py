from dynaconf import Dynaconf
import os

if __name__ == "__main__":
    settings = Dynaconf(
        settings_files=['settings.yml'],
    )

    print(settings)
    print(settings)

