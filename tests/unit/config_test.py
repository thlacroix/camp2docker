import unittest
import yaml
import os
from config import Config, ServiceConfig, NoServiceException, NoArtifactException
from plan import CharacteristicSpecification

def setUpModule():
    global artifacts
    global services
    global config_fixtures_dir 

    config_fixtures_dir = os.path.join('tests', 'fixtures', 'config')
    with open(os.path.join(config_fixtures_dir, 'services', 'services.yaml')) as f:
        services = yaml.load(f)

    with open(os.path.join(config_fixtures_dir, 'artifacts', 'artifacts.yaml')) as f:
        artifacts = yaml.load(f)

class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config.from_path(config_fixtures_dir)
    
    def test_number_services(self):
        self.assertEqual(len(self.config.services), 2)

    def test_number_artifacts(self):
        self.assertEqual(len(self.config.artifacts),  2)

    def test_find_existing_artifact(self):
        actual = self.config.find_artifact_config_by_type("Nodejs:Application")
        expected = self.config.artifacts[0]
        self.assertEqual(actual, expected)

    def test_find_non_existing_artifact(self):
        with self.assertRaises(NoArtifactException):
            self.config.find_artifact_config_by_type("Cat")

    def test_find_existing_service_by_name(self):
        actual = self.config.find_service_by_name("mongodb")
        expected = self.config.services[0]
        self.assertEqual(actual, expected)

    def test_find_non_existing_service_by_name(self):
        with self.assertRaises(NoServiceException):
            self.config.find_service_by_name("Restaurant")

    def test_find_existing_service_by_characteristics(self):
        """Test the search of a latest MongoDB database service"""
        characteristics = [CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': 'latest'}), CharacteristicSpecification(**{'characteristic_type': 'Database'})]
        actual = self.config.find_service_by_characteristics(characteristics)
        expected = self.config.services[0]
        self.assertEqual(actual, expected)

    def test_find_existing_service_by_empty_characteristics(self):
        actual = self.config.find_service_by_characteristics([])
        expected = self.config.services[0]
        self.assertEqual(actual, expected)

    def test_find_non_existing_service_by_characteristics(self):
        characteristics = [CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': "2.6"})]
        with self.assertRaises(NoServiceException):
            self.config.find_service_by_characteristics(characteristics)

class ServiceConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = ServiceConfig(**services[0])

    def test_fields(self):
        self.assertEqual(self.service.name, 'mongodb')
        self.assertEqual(self.service.base, 'dockerfile/mongodb')
        self.assertEqual(self.service.description, 'MongoDB NoSQL Database')
        self.assertEqual(len(self.service.characteristics), 3)

    def test_corresponds_to_characteristics(self):
        characteristics = [CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': 'latest'}), CharacteristicSpecification(**{'characteristic_type': 'Database'})]
        self.assertTrue(self.service.corresponds_to_characteristics(characteristics))

    def test_not_corresponds_to_characteristics_opt(self):
        characteristics = [CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': 'first'}), CharacteristicSpecification(**{'characteristic_type': 'Database'})]
        self.assertFalse(self.service.corresponds_to_characteristics(characteristics))

    def test_not_corresponds_to_characteristics_char(self):
        characteristics = [CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': 'latest'}), CharacteristicSpecification(**{'characteristic_type': 'SQL'})]
        self.assertFalse(self.service.corresponds_to_characteristics(characteristics))
