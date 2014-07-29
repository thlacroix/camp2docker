from output import Container
from config import Config
import os
import utils

class LinkException(Exception):
    pass

class PlanProcessor(object):
    def __init__(self, plan):
        self.plan = plan
        self.config = Config()
        self.assembly = Assembly(plan)
        self._temp_artifact_components = set()
        self._temp_actions = []

    def process_plan(self):
        """
            Create an assembly from the plan and the configuration
        """
        for artifact in self.plan.artifacts:
            artifact_config = self.config.find_artifact_config_by_type(artifact.artifact_type)
            self._temp_artifact_components.clear()
            del self._temp_actions[:]
            if hasattr(artifact, 'requirements'):
                for requirement in artifact.requirements:
                    requirement_config = artifact_config.find_requirement_by_type(requirement.requirement_type)
                    requirement_config.validate_parameters(requirement.parameters)
                    service_specification = requirement.service(self.plan)
                    if service_specification is not None:
                        service = self.config.find_service_by_characteristics(service_specification.characteristics)
                    else:
                        service = self.config.find_service_by_name(requirement_config.default_service)
                    component = self.assembly.add_component(service_specification, service, artifact=artifact.content)
                    self._temp_artifact_components.add(component)
                    action = requirement_config.find_action_by_service_name(service.name)
                    parameters = utils.mustach_dict(requirement.parameters)
                    parameters.update({'artifact': str(artifact.content)})
                    self._temp_actions.append({'action_config': action, 'parameters': parameters, 'component': component})
            else:
                requirement_config = artifact_config.get_default_requirement()
                service = self.config.find_service_by_name(requirement_config.default_service)
                component = self.assembly.add_component(None, service, artifact=artifact.content)
                self._temp_artifact_components.add(component)
                action = requirement_config.find_action_by_service_name(service.name)
                parameters = {'artifact': str(artifact.content)}
                self._temp_actions.append({'action_config': action, 'parameters': parameters, 'component': component})
            self._process_actions()

        return self.assembly

    def _find_component_in_temp(self, specification):
        if specification.has_key('service'):
            for c in self._temp_artifact_components:
                if c.service_config.name == specification["service"]:
                    return c
            else:
                raise LinkException("Can't link to service {service}".format(service=specification["service"]))

    
    def _resolve_links(self):
        for component in self._temp_artifact_components:
            for k,link in enumerate(component.container.links):
                if isinstance(link, Container):
                    continue
                else:
                    c = self._find_component_in_temp(link)
                    component.container.links[k] = c.container
                    component.related_components.add(c)

    def _process_actions(self):
        for action in self._temp_actions:
            for instruction_list in action["action_config"].instructions:
                if instruction_list.target == ".":
                    action["component"].container.process_instructions(instruction_list.do, action["parameters"], action["component"].container)
                else:
                    c = self._find_component_in_temp(instruction_list.target)
                    c.container.process_instructions(instruction_list.do, action["parameters"], action["component"].container)
        self._resolve_links()

class Component(object):
    def __init__(self, service_specification, service_config, container=None, artifact=None):
        self.service_specification = service_specification
        self.service_config = service_config
        if container is not None:
            self.container = container
        else:
            self.container = Container.from_service(service_config)
        if artifact is not None:
            self.artifact = artifact
        self.related_components = set()

class Assembly(object):
    """
        Represents a set of containers and their links
    """
    def __init__(self, plan):
        self.plan = plan
        self.components = set()

    def add_component(self, service_specification, service_config, container=None, artifact=None):
        component = None if service_specification is None else self.search_component(service_specification)
        if component is None:
            component = Component(service_specification, service_config, container, artifact)
            self.components.add(component)
        return component

    def search_component(self, service_specification):
        for component in self.components:
            if component.service_specification is service_specification:
                return component
    def to_fig(self):
        rep = ""
        for c in self.components:
            container = c.container
            rep += container.name + ":\n"
            rep += "\tbuild: {foldername}\n".format(foldername=container.name)
            if container.links:
                rep += "\tlinks:\n"
                for link in container.links:
                    rep += "\t\t- {container_name}\n".format(container_name=link.name)
            if container._exposes:
                rep += "\tports:\n"
                for port in container._exposes:
                    rep+= "\t\t- \"{port}:{port}\"\n".format(port=port)

        return rep

    def generate_files(self, output_directory):
        dir = os.path.join(output_directory, self.plan.name)
        try:
            os.mkdir(dir)
        except OSError:
            if not os.path.isdir(dir):
                raise
        with open(os.path.join(dir, 'fig.yml'), 'w') as fig:
            fig.write(self.to_fig())

        for c in self.components:
            dirname = os.path.join(dir, c.container.name)
            try:
                os.mkdir(dirname)
            except OSError:
                if not os.path.isdir(dirname):
                    raise
            with open(os.path.join(dirname, 'Dockerfile'), 'w') as Dockerfile:
                Dockerfile.write(str(c.container))

    def __repr__(self):
        res = "========== DOCKERFILES ==========\n\n" 
        res += '\n'.join(str(c.container) for c in self.components)
        res += "\n========== FIG ==========\n" 
        res += '\n'+self.to_fig()
        return res
