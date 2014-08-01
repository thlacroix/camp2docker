from yaml import load
import os
from config import Config
from output import Container

class SpecificationException(Exception):
    pass

class ArtifactTypeError(Exception):
    pass

class ServiceReferenceException(Exception):
    pass

class Node(object):
    def __repr__(self):
        return str(self.__dict__)

class GeneralNode(Node):
    def __init__(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs.pop('name')
        if 'description' in kwargs:
            self.description = kwargs.pop('description')
        if 'tags' in kwargs:
            self.tags = kwargs.pop('tags')

class Plan(GeneralNode):
    def __init__(self, camp_version, **kwargs):
        self.camp_version = camp_version
        if 'origin' in kwargs:
            self.origin = kwargs.pop('origin')
        if 'artifacts' in kwargs:
            artifacts = kwargs.pop('artifacts')
            self.artifacts = ArtifactSpecificationSet.from_dict_array(artifacts)
        if 'services' in kwargs:
            services = kwargs.pop('services')
            self.services = ServiceSpecificationSet.from_dict_array(services)
        super(Plan, self).__init__(**kwargs)

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            plan = load(f)
            if not plan.has_key("name"):
                plan["name"] = os.path.split(filename)[1].split('.')[0]
            return cls(**plan)

    @property
    def artifacts_or_empty(self):
        return getattr(self, 'artifacts', ArtifactSpecificationSet())
    @property
    def services_or_empty(self):
        return getattr(self, 'services', ServiceSpecificationSet())

class ArtifactSpecification(GeneralNode):
    def __init__(self, artifact_type, content, **kwargs):
        self.artifact_type = artifact_type
        self.content = ContentSpecification(**content)
        if "requirements" in kwargs:
            requirements = kwargs.pop('requirements')
            self.requirements = [RequirementSpecification(**r) for r in requirements]
        super(ArtifactSpecification, self).__init__(**kwargs)

    @property
    def requirements_or_empty(self):
        return getattr(self, 'requirements', [])

class ServiceSpecification(GeneralNode):
    def __init__(self, **kwargs):
        if 'id' in kwargs:
            self.id = kwargs.pop('id')
        if 'href' in kwargs:
            self.href = kwargs.pop('href')
        if 'characteristics' in kwargs:
            characteristics = kwargs.pop('characteristics')
            self.characteristics = [CharacteristicSpecification(**c) for c in characteristics]
        super(ServiceSpecification, self).__init__(**kwargs)

class CharacteristicSpecification(Node):
    def __init__(self, characteristic_type, **kwargs):
        self.characteristic_type = characteristic_type
        self.__dict__.update(kwargs)
    @property
    def parameters(self):
        return dict((c,v) for c,v in self.__dict__.iteritems() if c != 'characteristic_type')

class RequirementSpecification(Node):
    def __init__(self, requirement_type, **kwargs):
        self.requirement_type = requirement_type
        if 'fulfillment' in kwargs:
            fulfillment = kwargs.pop('fulfillment')
            if isinstance(fulfillment, dict):
                self.fulfillment = ServiceSpecification(**fulfillment)
            else:
                self.fulfillment = fulfillment
        self.__dict__.update(kwargs)
    @property
    def parameters(self):
        return dict((c,v) for c,v in self.__dict__.iteritems() if c not in ['requirement_type', 'fulfillment'])

    def service(self, plan):
        if type(self.fulfillment) is ServiceSpecification:
            return self.fulfillment
        elif type(self.fulfillment) is str:
            id = self.fulfillment.split('id:')[1]
            for artifact in plan.artifacts_or_empty:
                for requirement in artifact.requirements_or_empty:
                    try:
                        if requirement.fulfillment.id == id:
                            return requirement.fulfillment
                    except:
                        pass
            for service in plan.services_or_empty:
                try:
                    if service.id == id:
                        return service
                except:
                    pass
            raise ServiceReferenceException("No service {id}".format(id=id))

class ContentSpecification(Node):
    def __init__(self, **kwargs):
        if 'href' in kwargs:
            self.href = URI(kwargs.get("href"))
        elif 'data' in kwargs:
            self.data = kwargs.get("data")
        else:
            raise SpecificationException("Content reference missing")

    def __repr__(self):
        try:
            return self.href
        except:
            return self.data

class URI(str):
    pass

class ResourceSet(list):
    pass

class ServiceSpecificationSet(ResourceSet):
    @classmethod
    def from_dict_array(cls, services):
        return cls([ServiceSpecification(**service) for service in services])

class ArtifactSpecificationSet(ResourceSet):
    @classmethod
    def from_dict_array(cls, artifacts):
        return cls([ArtifactSpecification(**artifact) for artifact in artifacts])
