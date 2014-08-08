"""camp2docker

Usage:
    camp2docker load <filename>
    camp2docker parse <filename>
    camp2docker process <filename>
    camp2docker generate <filename> <output_folder>
    camp2docker generun <filename> <output_folder>
    camp2docker start <filename>
    camp2docker stop <filename>
    camp2docker rm <filename>
    camp2docker services
    camp2docker service <service>
    camp2docker artifacts
    camp2docker artifact <artifact>
    camp2docker requirements <artifact>

Options:
    -h --help Show this
"""
from docopt import docopt
from plan import Plan
from assembly import PlanProcessor, Assembly
from config import Config
from fig.packages.docker.client import Client
from fig.cli.utils import docker_url
import pprint
import logging
import sys
import os

def setup_logging():
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter())
    console_handler.setLevel(logging.INFO)
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    setup_logging()
    args = docopt(__doc__)

    if args["load"]:
        with open(args["<filename>"], 'r') as f:
            pprint.pprint(load(f))
    elif args["parse"]:
        plan = Plan.from_file(args["<filename>"])
        print plan
    elif args["process"]:
        assembly = Assembly.from_plan(args["<filename>"])
        print assembly

    elif args["generate"]:
        assembly = Assembly.from_plan(args["<filename>"])
        assembly.generate_files(os.path.split(args["<filename>"])[0], args["<output_folder>"])
    elif args["generun"]:
        assembly = Assembly.from_plan(args["<filename>"])
        assembly.generate_files(os.path.split(args["<filename>"])[0], args["<output_folder>"])
        os.chdir(os.path.join(args["<output_folder>"], plan.name))
        assembly.run(client)
    elif args["start"]:
        assembly = Assembly.from_plan(args["<filename>"])
        client = Client(docker_url())
        assembly.start(client)
    elif args["stop"]:
        assembly = Assembly.from_plan(args["<filename>"])
        client = Client(docker_url())
        assembly.stop(client)
    elif args["rm"]:
        assembly = Assembly.from_plan(args["<filename>"])
        client = Client(docker_url())
        assembly.rm(client)
    elif args["services"]:
        config = Config.from_path()
        services = config.services
        for service in services:
            print service.name
    elif args["service"]:
        config = Config.from_path()
        try:
            pprint.pprint(config.find_service_by_name(args["<service>"]))
        except:
            print "No service {service}".format(service=args["<service>"])
    elif args["artifacts"]:
        config = Config.from_path()
        artifacts = config.artifacts
        for artifact in artifacts:
            print artifact.name
    elif args["artifact"]:
        config=Config.from_path()
        try:
            pprint.pprint(config.find_artifact_config_by_type(args["<artifact>"]))
        except:
            print "No artifact {artifact}".format(artifact=args["<artifact>"])
