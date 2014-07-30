import unittest
from config import Config, NoServiceException, NoArtifactException
from plan import CharacteristicSpecification

def setUpModule():
    global config
    config = Config.from_path('tests/fixtures/config')

class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = config
    
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

    def test_find_nin_existing_service_by_characteristics(self):
        characteristics = [CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': "2.6"})]
        with self.assertRaises(NoServiceException):
            self.config.find_service_by_characteristics(characteristics)
