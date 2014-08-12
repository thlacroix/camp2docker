import unittest
from yaml import load
from camp2docker.plan import Plan, ServiceSpecification, ArtifactSpecification, RequirementSpecification, CharacteristicSpecification, ArtifactSpecificationSet, ServiceSpecificationSet

def setUpModule():
    global plan
    with open('tests/fixtures/app.yaml', 'r') as f:
        plan = load(f)

class PlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = Plan.from_file('tests/fixtures/app.yaml')

    def test_fields(self):
        self.assertEqual(self.plan.name, 'app')
        self.assertEqual(self.plan.description, 'camp2docker test application')
        self.assertEqual(self.plan.camp_version, 'CAMP 1.1')
        self.assertEqual(len(self.plan.artifacts), 2)
        self.assertEqual(len(self.plan.services), 1)

    def test_artifacts_or_empty(self):
        self.assertEqual(self.plan.artifacts_or_empty, self.plan.artifacts)

    def test_empty_artifacts_or_empty(self):
        plan_without_artifacts = Plan(camp_version="CAMP 1.1")
        self.assertEqual(len(plan_without_artifacts.artifacts_or_empty), 0)
        self.assertIsInstance(plan_without_artifacts.artifacts_or_empty, ArtifactSpecificationSet)

    def test_services_or_empty(self):
        self.assertEqual(self.plan.services_or_empty, self.plan.services)

    def test_empty_services_or_empty(self):
        plan_without_services = Plan(camp_version="CAMP 1.1")
        self.assertEqual(len(plan_without_services.services_or_empty), 0)
        self.assertIsInstance(plan_without_services.services_or_empty, ServiceSpecificationSet)

class ServiceSpecificationTest(unittest.TestCase):
    def runTest(self):
        service = ServiceSpecification(**plan["services"][0])
        self.assertEqual(service.id, 'Nodejs.runtime')
        self.assertEqual(len(service.characteristics), 1)

class ArtifactSpecificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = ArtifactSpecification(**plan["artifacts"][0])

    def test_fields(self):
        self.assertEqual(self.artifact.name, 'Server file')
        self.assertEqual(self.artifact.artifact_type, 'Nodejs:Application')
        self.assertEqual(self.artifact.content.href, 'app.js')
        self.assertEqual(len(self.artifact.requirements), 2)

    def test_requirements_or_empty(self):
        self.assertIs(self.artifact.requirements_or_empty, self.artifact.requirements)

    def test_empty_requirements_or_empty(self):
        artifact = ArtifactSpecification(**{'artifact_type': 'Rock', 'content': {'href': 'meow.py'}})
        self.assertEqual(len(artifact.requirements_or_empty), 0)

class RequirementSpecificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requirement = RequirementSpecification(**plan["artifacts"][0]["requirements"][0])

    def test_fields(self):
        self.assertEqual(self.requirement.requirement_type, 'Nodejs:Run')
        self.assertEqual(getattr(self.requirement, 'Nodejs.Port'), 3000)
        self.assertEqual(self.requirement.fulfillment, 'id:Nodejs.runtime')

    def test_parameters(self):
        self.assertEqual(self.requirement.parameters, {'Nodejs.Port': 3000})
    
    def test_empty_parameters(self):
        requirement = RequirementSpecification(**plan["artifacts"][1]["requirements"][0])
        self.assertEqual(requirement.parameters, {})

    def test_service(self):
        p = Plan(**plan)
        actual = p.artifacts[0].requirements[0].service(p)
        expected = p.services[0]
        self.assertIs(actual, expected)

    def test_service_other_artifact(self):
        p = Plan(**plan)
        actual = p.artifacts[0].requirements[1].service(p)
        expected = p.artifacts[1].requirements[0].fulfillment
        self.assertIs(actual, expected)

class Characteristic_specification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.characteristic = CharacteristicSpecification(**plan["artifacts"][1]["requirements"][0]["fulfillment"]["characteristics"][0])

    def test_fields(self):
        self.assertEqual(self.characteristic.characteristic_type, 'MongoDB')
        self.assertEqual(getattr(self.characteristic, 'MongoDB:version'), 'latest')
        
