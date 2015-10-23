import unittest
import os.path

from shinto_cli.cli import render_command


class RenderTest(unittest.TestCase):
    def setUp(self):
        os.chdir(
            os.path.dirname(__file__)
        )

    #: The expected output
    expected_output = """server {
  listen 80;
  server_name localhost;

  root /var/www/project;
  index index.htm;

  access_log /var/log/nginx//http.access.log combined;
  error_log  /var/log/nginx//http.error.log;
}"""

    def _testme(self, argv, stdin=None, env=None):
        """ Helper test shortcut """
        result = render_command(os.getcwd(), env or {}, stdin, argv)
        if(isinstance(result, str)):
            self.assertEqual(self.expected_output, result)
        else:
            self.assertEqual(self.expected_output.encode('UTF-8'), result)

    def test_ini(self):
        # Filename
        self._testme(['resources/nginx.j2', 'resources/data.ini'])
        # Format
        self._testme(['--format=ini', 'resources/nginx.j2', 'resources/data.ini'])
        # Stdin
        self._testme(['--format=ini', 'resources/nginx.j2'], stdin=open('resources/data.ini'))

    def test_json(self):
        # Filename
        self._testme(['resources/nginx.j2', 'resources/data.json'])
        # Format
        self._testme(['--format=json', 'resources/nginx.j2', 'resources/data.json'])
        # Stdin
        self._testme(['--format=json', 'resources/nginx.j2'], stdin=open('resources/data.json'))

    def test_yaml(self):
        try:
            import yaml
        except ImportError:
            raise unittest.SkipTest('Yaml lib not installed')

        # Filename
        self._testme(['resources/nginx.j2', 'resources/data.yml'])
        self._testme(['resources/nginx.j2', 'resources/data.yaml'])
        # Format
        self._testme(['--format=yaml', 'resources/nginx.j2', 'resources/data.yml'])
        # Stdin
        self._testme(['--format=yaml', 'resources/nginx.j2'], stdin=open('resources/data.yml'))

    def test_env(self):
        # Filename
        self._testme(['resources/nginx-env.j2', 'resources/data.env'])
        # Format
        self._testme(['--format=env', 'resources/nginx-env.j2', 'resources/data.env'])

        # Environment!
        env = dict(NGINX_HOSTNAME='localhost', NGINX_WEBROOT='/var/www/project', NGINX_LOGS='/var/log/nginx/')
        self._testme(['--format=env', 'resources/nginx-env.j2'], env=env)
        self._testme(['--format=env', 'resources/nginx-env.j2'], env=env)

    def test_glob(self):
        self.assertTrue(render_command(os.getcwd(),
                                       {},
                                       None,
                                       ['-g',
                                        'resources/nginx-env*.j2',
                                        'resources/data.env']) in
                        ['[\'resources/nginx-env\', \'resources/nginx-env2\']',
                         '[\'resources/nginx-env2\', \'resources/nginx-env\']'])
        with open('resources/nginx-env', 'r') as f:
            result = f.read()
            if(isinstance(result, str)):
                self.assertEqual(self.expected_output, result)
            else:
                self.assertEqual(self.expected_output.encode('UTF-8'), result)
        with open('resources/nginx-env2', 'r') as f:
            result = f.read()
            if(isinstance(result, str)):
                self.assertEqual(self.expected_output, result)
            else:
                self.assertEqual(self.expected_output.encode('UTF-8'), result)
