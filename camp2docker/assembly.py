from output import Container
from config import Config
from plan import Plan
from fig.project import Project
import os
import utils
import shutil
import errno

class LinkException(Exception):
    pass

class PlanProcessor(object):
    def __init__(self, plan, config='config'):
        self.plan = plan
        self.config = Config.from_path(config)
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
                    component = self.assembly.add_component(service_specification, service)
                    component.artifacts.add(artifact.content)
                    self._temp_artifact_components.add(component)
                    action = requirement_config.find_action_by_service_name(service.name)
                    parameters = utils.mustach_dict(requirement.parameters)
                    parameters.update({'artifact': str(artifact.content)})
                    self._temp_actions.append({'action_config': action, 'parameters': parameters, 'component': component})
            else:
                requirement_config = artifact_config.get_default_requirement()
                service = self.config.find_service_by_name(requirement_config.default_service)
                component = self.assembly.add_component(None, service)
                component.artifacts.add(artifact.content)
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
                raise LinkException("Can't find service {service}".format(service=specification["service"]))

    
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
    def __init__(self, service_specification, service_config, container=None, artifacts=None):
        self.service_specification = service_specification
        self.service_config = service_config
        if container is not None:
            self.container = container
        else:
            self.container = Container.from_service(service_config)
        if artifacts is not None:
            self.artifacts = set(artifacts)
        else:
            self.artifacts = set()
        self.related_components = set()

    @property
    def service_dict(self):
        service = {'name': self.container.name }
        if self.container.needs_build:
            service['build'] = self.container.name
        else:
            service['image'] = self.container.base
            if self.container.volumes:
                volumes = []
                service['volumes'] = volumes
                for volume in self.container.volumes:
                    volumes.append(volume)
            if self.container.cmd is not None:
                service['command'] = self.container.cmd
            if self.container.entrypoint is not None:
                service['entrypoint'] = self.container.entrypoint
        if self.container.links:
            links = []
            service['links'] = links
            for link in self.container.links:
                links.append(link.name)
        if self.container.exposes:
            exposes = []
            service['ports'] = exposes
            for port in self.container.exposes:
                exposes.append('{port}:{port}'.format(port=port))
        return service


class Assembly(object):
    """
        Represents a set of containers and their links
    """
    def __init__(self, plan):
        self.plan = plan
        self.components = set()

    @classmethod
    def from_plan(cls, planfile, config='config'):
        plan = Plan.from_file(planfile)
        pp = PlanProcessor(plan, config)
        return pp.process_plan()

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
            if container.needs_build:
                rep += "  build: {foldername}\n".format(foldername=container.name)
            else:
                rep+= "  image: {image}\n".format(image=container.base)
            if container.links:
                rep += "  links:\n"
                for link in container.links:
                    rep += "    - {container_name}\n".format(container_name=link.name)
            if container.exposes:
                rep += "  ports:\n"
                for port in container.exposes:
                    rep+= "    - \"{port}:{port}\"\n".format(port=port)
        return rep
    
    @property
    def to_service_dicts(self):
        service_dicts = []
        for c in self.components:
            service_dicts.append(c.service_dict)
        return service_dicts

    def to_fig_project(self, client):
        return Project.from_dicts(self.plan.name, self.to_service_dicts, client)
    
    def run(self, client):
        self.to_fig_project(client).up()

    def stop(self, client):
        self.to_fig_project(client).stop()

    def start(self, client):
        self.to_fig_project(client).start()

    def rm(self, client):
        self.to_fig_project(client).remove_stopped()

    def generate_files(self, plan_directory, output_directory):
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
            for artifact in c.artifacts:
                try :
                    target = os.path.join(dirname, artifact.href)
                    if not os.path.exists(target):
                        shutil.copytree(os.path.join(plan_directory, artifact.href), target)
                except OSError as e:
                    if e.errno == errno.ENOTDIR:
                        shutil.copy(os.path.join(plan_directory, artifact.href), dirname)
                    else: raise

    def __repr__(self):
        res = "========== DOCKERFILES ==========\n\n" 
        res += '\n'.join(str(c.container) for c in self.components)
        res += "\n========== FIG ==========\n" 
        res += '\n'+self.to_fig()
        return res
