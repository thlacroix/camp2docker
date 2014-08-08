import unittest
from mock import Mock, patch
from plan import Plan
from assembly import Component

class ComponentTest(unittest.TestCase):
    @patch('assembly.Container.from_service', return_value=Mock(name='mongodb', base='dockerfile/mongodb'))
    @patch('config.ServiceConfig')
    @patch('plan.ServiceSpecification')
    def test_no_container_no_artifact(self, ServiceSpecification, ServiceConfig, container_mock):
        container_mock.return_value.name = 'mongodb'
        service_config = ServiceConfig()
        service_specification = ServiceSpecification()
        component = Component(service_specification, service_config)
        self.assertEqual(component.service_specification, service_specification)
        self.assertEqual(component.service_config, service_config)
        self.assertEqual(component.container, container_mock.return_value)
        self.assertFalse(hasattr(component, 'artifact'))

    @patch('config.ServiceConfig')
    @patch('plan.ServiceSpecification')
    @patch('output.Container')
    def test_container_artifact(self, Container, ServiceSpecification, ServiceConfig):
        service_config = ServiceConfig()
        service_specification = ServiceSpecification()
        container = Container()
        component = Component(service_specification, service_config, container, "app.js")
        self.assertEqual(component.service_specification, service_specification)
        self.assertEqual(component.service_config, service_config)
        self.assertEqual(component.container, container)
        self.assertEqual(component.artifact, "app.js")
