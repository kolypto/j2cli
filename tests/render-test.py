from __future__ import unicode_literals
from io import open # pylint: disable=redefined-builtin
import unittest
import os.path

from j2cli.cli import render_command

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
        self.assertEqual(self.expected_output,
                         render_command(os.getcwd(), env or {}, stdin, argv))

    def test_ini(self):
        # Filename
        self._testme(['resources/nginx.j2', 'resources/data.ini'])
        # Format
        self._testme(['--format=ini', 'resources/nginx.j2', 'resources/data.ini'])
        # Stdin
        self._testme(['--format=ini', 'resources/nginx.j2'], stdin=open('resources/data.ini', encoding='utf-8'))

    def test_json(self):
        # Filename
        self._testme(['resources/nginx.j2', 'resources/data.json'])
        # Format
        self._testme(['--format=json', 'resources/nginx.j2', 'resources/data.json'])
        # Stdin
        self._testme(['--format=json', 'resources/nginx.j2'], stdin=open('resources/data.json', encoding='utf-8'))

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
        self._testme(['--format=yaml', 'resources/nginx.j2'], stdin=open('resources/data.yml', encoding='utf-8'))

    def test_env(self):
        # Filename
        self._testme(['resources/nginx-env.j2', 'resources/data.env'])
        # Format
        self._testme(['--format=env', 'resources/nginx-env.j2', 'resources/data.env'])

        # Environment!
        env = dict(NGINX_HOSTNAME='localhost', NGINX_WEBROOT='/var/www/project', NGINX_LOGS='/var/log/nginx/')
        self._testme(['--format=env', 'resources/nginx-env.j2'], env=env)
        self._testme(['--format=env', 'resources/nginx-env.j2'], env=env)
