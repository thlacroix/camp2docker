"""camp2docker

Usage:
    camp2docker load <filename>
    camp2docker parse <filename>
    camp2docker process <filename>
    camp2docker generate <filename> <output_folder>
    camp2docker services
    camp2docker service <service>
    camp2docker artifacts
    camp2docker artifact <artifact>
    camp2docker requirements <artifact>

Options:
    -h --help Show this
"""
from docopt import docopt
from input import Planfile
from assembly import PlanProcessor
from config import Config
import pprint

if __name__ == "__main__":
    args = docopt(__doc__)

    if args["load"]:
        planfile = Planfile(args["<filename>"])
        pprint.pprint(planfile.config)
    elif args["parse"]:
        plan = Planfile(args["<filename>"]).create_plan()
        print plan
    elif args["process"]:
        plan = Planfile(args["<filename>"]).create_plan()
        pp = PlanProcessor(plan)
        print pp.process_plan()
    elif args["generate"]:
        plan = Planfile(args["<filename>"]).create_plan()
        pp = PlanProcessor(plan)
        pp.process_plan().generate_files(args["<output_folder>"])

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
