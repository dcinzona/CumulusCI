from unittest import mock

import pytest

from cumulusci.core.config import ServiceConfig, TaskConfig
from cumulusci.core.exceptions import CumulusCIException
from cumulusci.tasks.github.base import BaseGithubTask
from cumulusci.tasks.github.tests.util_github_api import GithubApiTestMixin
from cumulusci.tests.util import create_project_config

DUMMY_SHA = "21e04cfe480f5293e2f7103eee8a5cbdb94f7982"


class MockBaseGithubTask(BaseGithubTask):

    task_options = {}
    salesforce_task = False

    def _run_task(self):
        pass


@mock.patch("cumulusci.tasks.github.release.time.sleep", mock.Mock())
class TestBaseGithubTaskEnterprise(GithubApiTestMixin):
    def setup_method(self):
        self.repo_owner = "TestOwner"
        self.repo_name = "TestRepo"
        self.repo_api_url = "https://api.github.com/repos/{}/{}".format(
            self.repo_owner, self.repo_name
        )
        self.project_config = create_project_config(
            self.repo_name,
            self.repo_owner,
            repo_commit="21e04cfe480f5293e2f7103eee8a5cbdb94f7982",
        )
        self.set_service("github", "test_alias_github", True)

    def set_service(self, type, alias, default: bool = False):
        service_config = ServiceConfig(
            {
                "username": "TestUserGithub",
                "token": "TestPass",
                "email": "test@testdomain.com",
            }
        )

        if type == "github_enterprise":
            service_config = ServiceConfig(
                {
                    "username": "testusername",
                    "email": "test@domain.com",
                    "token": "ATOKEN",
                    "server_domain": "git.enterprise.domain.com",
                }
            )

        self.project_config.keychain.set_service(type, alias, service_config)

        if default:
            self.project_config.keychain.set_default_service(type, alias)

    def test_init_task_github(self):
        """_summary_ : Test that the task initializes correctly when the github service is used."""
        task = MockBaseGithubTask(self.project_config, TaskConfig({"options": {}}))
        task()
        assert task.github_config is not None

    def test_init_task_github_enterprise(self):
        """_summary_ : Tests to verify the first check is for the github_enterprise service."""
        self.set_service("github_enterprise", "test_alias_github_enterprise", True)
        task = MockBaseGithubTask(self.project_config, TaskConfig({"options": {}}))
        task()
        assert task.github_config is not None

    def test_exception_no_github_service(self):
        self.project_config.keychain.remove_service("github", "test_alias_github")
        with pytest.raises(CumulusCIException):
            task = MockBaseGithubTask(self.project_config, TaskConfig({"options": {}}))
            task()
