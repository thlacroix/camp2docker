import unittest
from mock import Mock
from camp2docker.output import Container

class ContainerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instructions = [
                ['ADD', '{{artifact}} /usr/src'],
                ['RUN', 'npm install', True],
                ['ENV', '{{#Port}}PORT {{.}}{{/Port}}'],
                ['EXPOSE', 3000, False],
                ['CMD', 'node {{artifact}}'],
                ['ENTRYPOINT', '/bin/boot.sh'],
                ['LINK', {'self': True}],
                ['VOLUME', '/usr/src']
        ]

    def setUp(self):
        self.container = Container('nodejs', 'node')

    def test_from_service(self):
        service = Mock()
        service.name = 'nodejs'
        service.base = 'node'
        c = Container.from_service(service)
        self.assertEqual(c.name, 'nodejs')
        self.assertEqual(c.base, 'node')

    def test_fields(self):
        self.assertEqual(self.container.name, 'nodejs')
        self.assertEqual(self.container.base, 'node')

    def test_process_mustache_template_list(self):
        instruction = self.instructions[0]
        parameters = {'artifact': 'app.js', 'bga': 'bbr'}
        actual = Container.process_mustache_template_list(instruction, parameters)
        expected = ['ADD', 'app.js /usr/src']
        self.assertEqual(actual, expected)
        
    def test_process_mustache_template_list_not_str(self):
        instruction = self.instructions[1]
        parameters = {'artifact': 'app.js', 'bga': 'bbr'}
        actual = Container.process_mustache_template_list(instruction, parameters)
        expected = ['RUN', 'npm install', True]
        self.assertEqual(actual, expected)

    def test_process_mustache_template_list_empty(self):
        instruction = self.instructions[2]
        parameters = {'artifact': 'app.js', 'bga': 'bbr'}
        actual = Container.process_mustache_template_list(instruction, parameters)
        expected = ['ENV', '']
        self.assertEqual(actual, expected)

    def test_add_instruction(self):
        instruction1 = Container.process_mustache_template_list(self.instructions[0], {'artifact': 'app.js'})
        instruction2 = Container.process_mustache_template_list(self.instructions[1], {'artifact': 'app.js'})
        self.container.add_instruction(instruction1)
        self.container.add_instruction(instruction2)
        self.assertEqual(self.container.instructions, [instruction1, instruction2])

    def test_add_expose(self):
        expose1 = 3000
        expose2 = 1337
        self.container.add_expose(expose1)
        self.container.add_expose(expose2)
        self.assertEqual(self.container.exposes, [expose1, expose2])

    def test_add_link(self):
        source_container = Container('mongodb', 'dockerfile/mongodb')
        link1 = {'self': True}
        link2 = {'service': 'mongodb'}
        self.container.add_link(link1, source_container)
        self.container.add_link(link2, source_container)
        self.assertEqual(self.container.links, [source_container, link2])

    def test_add_volume(self):
        source_container = Container('app_data', 'ubuntu')
        volume1 = '/usr/src/'
        volume2 = '/home/app'
        self.container.add_volume(volume1, source_container)
        self.container.add_volume(volume2, source_container)
        self.assertEqual(self.container.volumes, [volume1, volume2])

    def test_process_instructions(self):
        source_container = Container('mongodb', 'dockerfile/mongodb')
        params = {'artifact': 'app.js', 'Port': 3000}
        self.container.process_instructions(self.instructions, params, source_container)
        self.assertEqual(self.container.volumes, [['/usr/src']])
        self.assertEqual(self.container.cmd, 'node app.js')
        self.assertEqual(self.container.entrypoint, '/bin/boot.sh')
        self.assertEqual(self.container.links, [source_container])
        self.assertEqual(self.container.exposes, [3000])
        self.assertEqual(self.container.instructions, [['ADD', 'app.js /usr/src'], ['RUN', 'npm install', True],['ENV', 'PORT 3000'], ['VOLUME', '/usr/src']])
        self.assertTrue(self.container.needs_build)

    def test_needs_build_add(self):
        self.container.add_instruction(['ADD', 'app.js /usr/src'])
        self.assertTrue(self.container.needs_build)

    def test_needs_build_run(self):
        self.container.add_instruction(['RUN', 'npm install'])
        self.assertTrue(self.container.needs_build)

    def test_needs_build_others(self):
        self.container.add_instruction(['VOLUME', '/usr/src'])
        self.container.add_instruction(['ENV', 'PORT 3000'])
        self.container.add_instruction(['EXPOSE', 3000])
        self.container.add_instruction(['LINK', {'self': True}])
        self.container.add_instruction(['ENTRYPOINT', '/bin/boot.sh'])
        self.container.add_instruction(['CMD', 'node app.js'])
        self.assertFalse(self.container.needs_build)

