from pathlib import Path
import sys
import os
from unittest.mock import patch
from logging import Logger

from mkdocs.plugins import BasePlugin


class Plugin(BasePlugin):
    def on_config(self, config):
        pass

    def on_pre_build(self, config):
        root_dir = Path(__file__).parent.parent.parent.parent
        faker_docs_dir = root_dir / "docs/fakedata"
        faker_docs_dir.mkdir(exist_ok=True)
        new_sys_path = [*sys.path, str(root_dir)]
        print("Note: Hiding warnings during docs build")

        # make modules available
        sys_path_patch = patch.object(sys, "path", new_sys_path)
        warning = Logger.warning

        irritating_warning = "Numbers generated by this method are purely hypothetical."

        def new_warning(self, *args, **kwargs):
            if args == (irritating_warning,):
                return
            else:
                warning(self, *args, **kwargs)

        logger_patch = patch("logging.Logger.warning", new=new_warning)

        # speed up a critical function
        #
        #   Disabled due to Faker refactoring. After release can look into
        #   whether it is still needed.
        #
        # lru_patch = patch(
        #     "faker.factory.Factory._get_provider_class",
        #     lru_cache(maxsize=10_000)(Factory._get_provider_class),
        # )

        with sys_path_patch, logger_patch:  # lru_patch,
            from tools.faker_docs_utils.faker_markdown import (
                generate_markdown_for_all_locales,
                generate_markdown_for_fakers,
                generate_locales_index,
            )

            fakerdocs_md_header = (
                root_dir / "tools/faker_docs_utils/fakedata_header_full.md"
            )
            main_header = Path(fakerdocs_md_header).read_text()
            fakerdocs_md = root_dir / "docs/fakedata.md"
            with fakerdocs_md.open("w") as f:
                generate_markdown_for_fakers(f, "en_US", main_header)

            build_locales_env = os.environ.get(
                "SF_MKDOCS_BUILD_LOCALES"
            ) or self.config.get("build_locales", None)
            if build_locales_env in (False, "False", "false"):
                locales_list = ["en_US", "fr_FR"]
            elif build_locales_env in (True, "True", "true", None):
                locales_list = None  # means "all"
            elif isinstance(build_locales_env, str):
                locales_list = build_locales_env.split(",")
            else:
                assert 0, f"Unexpected build_locales_env {build_locales_env}"

            generate_markdown_for_all_locales(faker_docs_dir, locales_list)
            generate_locales_index("docs/locales.md", locales_list)
