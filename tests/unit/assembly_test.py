import unittest
from mock import Mock, patch
from camp2docker.plan import Plan
from camp2docker.assembly import Component

class PlanProcessorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = Plan.from_file('tests/fixtures/app.yaml')

    def setUp(self):
        self.pp = PlanProcessor(self.plan)

class ComponentTest(unittest.TestCase):
    @patch('camp2docker.assembly.Container.from_service', return_value=Mock(name='mongodb', base='dockerfile/mongodb'))
    @patch('camp2docker.config.ServiceConfig')
    @patch('camp2docker.plan.ServiceSpecification')
    def test_no_container_no_artifact(self, ServiceSpecification, ServiceConfig, container_mock):
        container_mock.return_value.name = 'mongodb'
        service_config = ServiceConfig()
        service_specification = ServiceSpecification()
        component = Component(service_specification, service_config)
        self.assertEqual(component.service_specification, service_specification)
        self.assertEqual(component.service_config, service_config)
        self.assertEqual(component.container, container_mock.return_value)
        self.assertEqual(len(component.artifacts), 0)

    @patch('camp2docker.config.ServiceConfig')
    @patch('camp2docker.plan.ServiceSpecification')
    @patch('camp2docker.output.Container')
    def test_container_artifact(self, Container, ServiceSpecification, ServiceConfig):
        service_config = ServiceConfig()
        service_specification = ServiceSpecification()
        container = Container()
        component = Component(service_specification, service_config, container, ["app.js"])
        self.assertEqual(component.service_specification, service_specification)
        self.assertEqual(component.service_config, service_config)
        self.assertEqual(component.container, container)
        self.assertEqual(component.artifacts, set(["app.js"]))
