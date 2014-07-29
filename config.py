import yaml
import os

class ConfigError(Exception):
    pass

class NoServiceException(Exception):
    pass

class ParameterException(Exception):
    pass

class BaseConfig(object):
    def __repr__(self):
        return str(self.__dict__)

class ServiceConfig(BaseConfig):
    def __init__(self, name, description, base, type, characteristics):
        self.name = name
        self.description = description
        self.base = base
        self.type = type
        self.characteristics = [CharacteristicConfig(**characteristic) for characteristic in characteristics]

    def corresponds_to_characteristics(self, characteristics):
        for characteristic in characteristics:
            if next((c for c in self.characteristics if c.match_characteristic(characteristic)), None) is None:
                return False
        return True

    def add_id(self, id):
        self.id = id

class CharacteristicConfig(BaseConfig):
    def __init__(self, characteristic_type, **kwargs):
        self.characteristic_type = characteristic_type
        self.__dict__.update(kwargs)

    @property
    def parameters(self):
        return dict((c,v) for c,v in self.__dict__.iteritems() if c != 'characteristic_type')

    def match_characteristic(self, characteristic):
        for k, v in characteristic.__dict__.iteritems():
            if self.__dict__.has_key(k):
                if self.__dict__.get(k) == v:
                    continue
                else:
                    return False
            else:
                return False
        return True

class ArtifactConfig(BaseConfig):
    def __init__(self, name, default_requirement, requirements):
        self.name = name
        self.default_requirement = default_requirement
        self.requirements = [RequirementConfig(**requirement) for requirement in requirements]
    def get_default_requirement(self):
        return next(r for r in self.requirements if r.requirement_type == self.default_requirement)
    def find_requirement_by_type(self, requirement_type):
        return next(r for r in self.requirements if r.requirement_type == requirement_type)

class RequirementConfig(BaseConfig):
    def __init__(self, requirement_type, default_service, actions, parameters=None):
        self.requirement_type = requirement_type
        if parameters is not None:
            self.parameters = ParameterConfig(parameters)
        else:
            self.parameters = {}
        self.default_service = default_service
        self.actions = [ActionConfig(**action) for action in actions]
    def validate_parameters(self, parameters):
        try:
            if len(parameters) > 0:
                return self.parameters.validate_parameters(parameters)
        except AttributeError:
            raise ParameterException("No parameters expected")

    def find_action_by_service_name(self, service_name):
        return next(a for a in self.actions if a.service == service_name)

class ParameterConfig(BaseConfig):
    TYPES = ('string', 'integer', 'boolean')
    def __init__(self, parameters):
        for value in parameters.itervalues():
            if value not in self.TYPES:
                raise ConfigError("Type not valid {type}".format(type=value))
        self.__dict__.update(parameters)

    def validate_parameters(self, parameters):
        for parameter, value in parameters.iteritems():
            try:
                expected_type = getattr(self, parameter)
            except:
                raise ParameterException("Parameter {parameter} is not valid".format(parameter=parameter))

            if expected_type == "string" and isinstance(value, str):
                pass
            elif expected_type == "integer" and isinstance(value, int):
                pass
            elif expected_type == "boolean" and isinstance(value, bool):
                pass
            else:
                raise ParameterException("Parameter {parameter} should be of type {expected_type}".format(parameter=parameter, expected_type=expected_type))

class ActionConfig(BaseConfig):
    def __init__(self, service, instructions):
        self.service = service
        self.instructions = [InstructionList(**instruction_list) for instruction_list in instructions]

class InstructionList(BaseConfig):
    def __init__(self, target, do):
        self.target = target
        self.do = do

class Config(object):
    def __init__(self, path='config'):
        self.path = path
        self.services = [ServiceConfig(**service) for service in self._parse_services_directory()]
        self.artifacts = [ArtifactConfig(**artifact) for artifact in self._parse_artifacts_directory()]

    def _parse_services_directory(self):
        services_path = os.path.join(self.path, 'services')
        files = os.listdir(services_path)
        services = []
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                services.extend(self._parse_services_file(os.path.join(services_path, file)))
        return services

    def _parse_services_file(self, filename):
        with open(filename, "r") as f:
            services = yaml.load(f)
        return services

    def _parse_artifacts_directory(self):
        artifacts_path = os.path.join(self.path, 'artifacts')
        files = os.listdir(artifacts_path)
        artifacts = []
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                artifacts.extend(self._parse_artifacts_file(os.path.join(artifacts_path, file)))
        return artifacts

    def _parse_artifacts_file(self, filename):
        with open(filename, "r") as f:
            artifacts = yaml.load(f)
        return artifacts

    def find_artifact_config_by_type(self, artifact_type):
        return next(artifact for artifact in self.artifacts if artifact.name == artifact_type)

    def find_service_by_name(self, name):
        return next(service for service in self.services if service.name == name)

    def find_service_by_characteristics(self, characteristics):
        for service in self.services:
            if service.corresponds_to_characteristics(characteristics):
                return service
        raise NoServiceException()

    def __repr__(self):
        return str(self.__dict__)
