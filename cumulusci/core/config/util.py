import json
from pathlib import Path
from typing import Dict

from cumulusci.core.config import BaseProjectConfig
from cumulusci.core.config.sfdx_org_config import SfdxOrgConfig
from cumulusci.core.exceptions import CumulusCIException, ServiceNotConfigured
from cumulusci.core.sfdx import get_default_devhub_username


def get_devhub_config(project_config: BaseProjectConfig) -> SfdxOrgConfig:
    """
    @param project_config: a base project configuration
    @return: an SfdxOrgConfig tied to the devHub
    """
    try:
        devhub_service = project_config.keychain.get_service("devhub")
    except (ServiceNotConfigured, CumulusCIException):
        devhub_username = get_default_devhub_username()
    else:
        devhub_username = devhub_service.username
    return SfdxOrgConfig({"username": devhub_username}, "devhub")


def save_project_package_aliases(
    project_config: BaseProjectConfig, package_aliases: Dict[str, str]
) -> None:
    """
    @param project_config: a base project configuration
    @param package_aliases: a dictionary of package aliases
    """
    sfdx_project_config = project_config.sfdx_project_config.copy()
    sfdx_project_config["packageAliases"] = package_aliases
    projectStr = json.dumps(sfdx_project_config, indent=2)
    with open(
        Path(project_config.repo_root) / "sfdx-project.json", "w", encoding="utf-8"
    ) as f:
        f.write(projectStr)
