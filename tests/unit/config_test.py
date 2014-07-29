import unittest
from config import Config

class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config()
    
    def test_services(self):
        services = self.config.services
        self.assertEqual(len(services), 2)
        self.assertEqual(services[0].name, "mongodb")
        self.assertEqual(services[0].base, "dockerfile/mongodb")
        self.assertEqual(services[0].type, "database")
        self.assertEqual(len(services[0].characteristics), 3)

    def test_artifacts(self):
        artifacts = self.config.artifacts
        self.assertEqual(len(artifacts),2)
        self.assertEqual(artifacts[0].name, "Nodejs:Application")
        self.assertEqual(artifacts[0].default_requirement, "Nodejs:Run")
        self.assertEqual(len(artifacts[0].requirements), 1)
        
