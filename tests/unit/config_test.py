import unittest
import yaml
import os
from camp2docker.config import Config, ServiceConfig, CharacteristicConfig, ArtifactConfig, RequirementConfig, ParameterConfig, ActionConfig, NoServiceException, NoArtifactException, NoRequirementException, ParameterException
from camp2docker.plan import CharacteristicSpecification

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

class CharacteristicConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        characteristic_dict = services[0]["characteristics"][1]
        cls.characteristic = CharacteristicConfig(**characteristic_dict)

    def test_fields(self):
        self.assertEqual(self.characteristic.characteristic_type, "MongoDB")
        self.assertEqual(getattr(self.characteristic, 'MongoDB:version'), "latest")

    def test_parameters(self):
        self.assertEquals(self.characteristic.parameters, {"MongoDB:version": "latest", "MongoDB:SingleNode": True})

    def test_empty_parameters(self):
        characteristic = CharacteristicConfig(**{'characteristic_type': 'Dogecoin'})
        self.assertEqual(characteristic.parameters, {})

    def test_match_characteristic(self):
        characteristic = CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': 'latest'})
        self.assertTrue(self.characteristic.match_characteristic(characteristic))

    def test_no_match_characteristic(self):
        characteristic = CharacteristicSpecification(**{'characteristic_type': 'MongoDB', 'MongoDB:version': '2.6'})
        self.assertFalse(self.characteristic.match_characteristic(characteristic))

class ArtifactConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = ArtifactConfig(**artifacts[0])

    def test_fields(self):
        self.assertEqual(self.artifact.name, 'Nodejs:Application')
        self.assertEqual(self.artifact.default_requirement, 'Nodejs:Run')
        self.assertEqual(len(self.artifact.requirements),2)

    def test_get_default_requirement(self):
        actual = self.artifact.get_default_requirement()
        expected = self.artifact.requirements[0]
        self.assertEqual(actual, expected)

    def test_default_requirement_dont_exist(self):
        artifact = ArtifactConfig(**artifacts[1])
        with self.assertRaises(NoRequirementException):
            artifact.get_default_requirement()

    def test_find_existing_requirement_by_type(self):
        actual = self.artifact.find_requirement_by_type('ConnectTo')
        expected = self.artifact.requirements[1]
        self.assertEqual(actual, expected)

    def test_find_non_existing_requirement_by_type(self):
        with self.assertRaises(NoRequirementException):
            self.artifact.find_requirement_by_type('RunForest')

class RequirementConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requirement = RequirementConfig(**artifacts[0]["requirements"][1])

    def test_fields(self):
        self.assertEqual(self.requirement.requirement_type, 'ConnectTo')
        self.assertEqual(self.requirement.default_service, 'mongodb')
        self.assertEqual(len(self.requirement.actions), 1)
        self.assertTrue(isinstance(self.requirement.parameters, ParameterConfig))

    def test_validate_parameters(self):
        try:
            self.requirement.validate_parameters({'dbname': 'Woof', 'smallfiles': True})
        except ParameterException:
            self.fail("Parameters not valid")

    def test_validate_non_valid_type_parameters(self):
        with self.assertRaises(ParameterException):
            self.requirement.validate_parameters({'dbname': True})

    def test_validate_non_valid_key_parameter(self):
        with self.assertRaises(ParameterException):
            self.requirement.validate_parameters({'first_name': 'Thomas'})
