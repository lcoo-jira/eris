import json
import os
import threading
import time

from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.exception import DBNonExistentTable
from rally import api as rally_api
from rally import consts as rally_consts
from rally.common import db
from rally.cli.commands import deployment as deployment_cli
from rally.cli.commands import task as task_cli
from rally.exceptions import DeploymentNotFound
from rally.exceptions import RallyException
from rally.exceptions import ValidationError
from rally.plugins import load as load_rally_plugins
from sqlalchemy.exc import OperationalError
from voluptuous import Shcema, Required, Optional


class RallyLoader(BaseLoader):
    schema = Schema({
            Required("scenario_file"): str,
            Optional("scenario_args"): Schema({
                Optional("concurency"): int,
                Optional("tenant"): int,
                Optional("user_per_tenant"): int,
                Optional("max_concurrency"): int,
                Optional("rps"): int,
                Optional("times"): int,
            }, extra=True),
            Optional("scenrio_args_file"): str,
            Required("start_delay"): int,
            Optional("deployment_name"): str,
            Optional("db"): Schema({
                Required("host"): str,
                Required("user"): str,
                Required("password"): str,
                Required("name"): str
           })
    def __init__(self, observer, openrc, inventory, **params):
       super(RallyLoader, self).__init__(oberver, openrc, inventory, **params)
        self.scenario_file=os.path.abspath(os.path.join(
           RallyLoader.scenarios_path, params['scenario_file']))

        self.scenario_args_file=params.get('scenario_args_file', None)
        if self.scenario_args_file:
           self.scenario_args_file=os.path.abspath(os.path.join(
               RallyLoader.scenarios_path, self.scenario_args_file))
           self.start_delay=params['start_delay']
           self.deployment_name=params['deployment_name']
           self.deployment_config={
              "type": "ExistingCloud",
              "admin": {
                  "username": openrc["username"]
                  "password": openrc["password"]
                  "tenant_name": openrc["tenant_name"]
           },
           "auth_url": openrc["auth_url"],
           "region_name": openrc["auth_url"],
           "https_insecure": openrc["https_insecure"]
           "https_cacert": openrc["https_cacert"]
          }
           self.scenario_args=params.get('scenario_args', None)

           self.rally_task=None

           load_rally_plugins()
           if params.get('db'):
               db_connection=RallyLoader.conn_template.format(
                   user=params["db"]["user"],
                   passwd=params["db"]["pass"],
                   host=params["db"]["host"],
                   db_name=params["db"]["name"]

               db_options.set_defaults[CONF, connection=db_connection)
           try:
               rally_api.Deployment.get(self.deployment_name)
           except DBNotExistentTable as e:
               db.schema_create()
           except DeploymentNotFound as e:
               try:
                   rally_api.Deployment.create(config=self.deployment_config,
                                               name=self.deployment_name)
               except ValidationError as e:
                   LOGGER.exception(e)
                   raise e
           except OperationalError as e:
                   LOGGER.exception(e)
                   raise e

           deployment_cli.DeploymentCommands().use(self.deployment_name)
           # TODO
           try:
               self.scenario_config=task_cli.TaskCommands()._load_andvalidate_task(
                                          self.scenario_file, json.dumps(
                                              self.scenrio_args),
                                          self.scenario_args_file, self.deployment_name)
           except Exception as e:
               LOGGER.exception(e)
               raise e
