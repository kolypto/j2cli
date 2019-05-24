[![Build Status](https://travis-ci.org/kolypto/j2cli.svg)](https://travis-ci.org/kolypto/j2cli)
[![Pythons](https://img.shields.io/badge/python-2.6%20%7C%202.7%20%7C%203.4%E2%80%933.7%20%7C%20pypy-blue.svg)](.travis.yml)

j2cli - Jinja2 Command-Line Tool
================================

`j2cli` is a command-line tool for templating in shell-scripts, 
leveraging the [Jinja2](http://jinja.pocoo.org/docs/) library.

Features:

* Jinja2 templating
* INI, YAML, JSON data sources supported
* Allows the use of environment variables in templates! Hello [Docker](http://www.docker.com/) :)

Inspired by [mattrobenolt/jinja2-cli](https://github.com/mattrobenolt/jinja2-cli)

## Installation

```
pip install j2cli
```

To enable the YAML support with [pyyaml](http://pyyaml.org/):

```
pip install j2cli[yaml]
```

## Tutorial

Suppose, you want to have an nginx configuration file template, `nginx.j2`:

```jinja2
server {
  listen 80;
  server_name {{ nginx.hostname }};

  root {{ nginx.webroot }};
  index index.htm;
}
```

And you have a JSON file with the data, `nginx.json`:

```json
{
    "nginx":{
        "hostname": "localhost",
        "webroot": "/var/www/project"
    }
}
```

This is how you render it into a working configuration file:

```bash
$ j2 -f json nginx.j2 nginx.json > nginx.conf
```

The output is saved to `nginx.conf`:

```
server {
  listen 80;
  server_name localhost;

  root /var/www/project;
  index index.htm;
}
```

Alternatively, you can use the `-o nginx.conf` option.

## Tutorial with environment variables

Suppose, you have a very simple template, `person.xml`:

```jinja2
<data><name>{{ name }}</name><age>{{ age }}</age></data>
```

What is the easiest way to use j2 here?
Use environment variables in your bash script:

```bash
$ export name=Andrew
$ export age=31
$ j2 /tmp/person.xml
<data><name>Andrew</name><age>31</age></data>
```

## Usage

Compile a template using INI-file data source:

    $ j2 config.j2 data.ini
    
Compile using JSON data source:

    $ j2 config.j2 data.json
    
Compile using YAML data source (requires PyYAML):

    $ j2 config.j2 data.yaml

Compile using JSON data on stdin:

    $ curl http://example.com/service.json | j2 --format=json config.j2

Compile using environment variables (hello Docker!):
    
    $ j2 config.j2
    
Or even read environment variables from a file:

    $ j2 --format=env config.j2 data.env

    
# Reference
`j2` accepts the following arguments:

* `template`: Jinja2 template file to render
* `data`: (optional) path to the data used for rendering. The default is `-`: use stdin

Options:

* `--format, -f`: format for the data file. The default is `?`: guess from file extension.
* `--import-env VAR, -e EVAR`: import all environment variables into the template as `VAR`.
    To import environment variables into the global scope, give it an empty string: `--import-env=`.
    (This will overwrite any existing variables!)
* `-o outfile`: Write rendered template to a file
* `--undefined`: Allow undefined variables to be used in templates (no error will be raised)
* `--environment-config`: Provide a config file (format guessed from file
  extension) containing key/value pairs that can be passed to Jinja2's
  [Environment
  configuration](http://jinja.pocoo.org/docs/2.10/api/#jinja2.Environment). This
  can be handy for tweaking the way your templates are processed by Jinja2, for
  example providing a YAML file with "lstrip_blocks: true" can configure Jinja2
  to produce less whitespace in the output.

* `--filters filters.py`: Load custom Jinja2 filters and tests from a Python file.
    Will load all top-level functions and register them as filters.
    This option can be used multiple times to import several files.
* `--tests tests.py`: Load custom Jinja2 filters and tests from a Python file.

There is some special behavior with environment variables:

* When `data` is not provided (data is `-`), `--format` defaults to `env` and thus reads environment variables
* When `--format=env`, it can read a special "environment variables" file made like this: `env > /tmp/file.env`

## Formats


### env
Data input from environment variables.

Render directly from the current environment variable values:

    $ j2 config.j2

Or alternatively, read the values from a file:

```
NGINX_HOSTNAME=localhost
NGINX_WEBROOT=/var/www/project
NGINX_LOGS=/var/log/nginx/
```

And render with:

    $ j2 config.j2 data.env
    $ env | j2 --format=env config.j2.

This is especially useful with Docker to link containers together.

### ini
INI data input format.

data.ini:

```
[nginx]
hostname=localhost
webroot=/var/www/project
logs=/var/log/nginx/
```

Usage:

    $ j2 config.j2 data.ini
    $ cat data.ini | j2 --format=ini config.j2

### json
JSON data input format

data.json:

```
{
    "nginx":{
        "hostname": "localhost",
        "webroot": "/var/www/project",
        "logs": "/var/log/nginx/"
    }
}
```

Usage:

    $ j2 config.j2 data.json
    $ cat data.json | j2 --format=ini config.j2

### yaml
YAML data input format.

data.yaml:

```
nginx:
  hostname: localhost
  webroot: /var/www/project
  logs: /var/log/nginx
```

Usage:

    $ j2 config.j2 data.yml
    $ cat data.yml | j2 --format=yaml config.j2




Extras
======

## Filters


### `docker_link(value, format='{addr}:{port}')`
Given a Docker Link environment variable value, format it into something else.

This first parses a Docker Link value like this:

    DB_PORT=tcp://172.17.0.5:5432

Into a dict:

```python
{
  'proto': 'tcp',
  'addr': '172.17.0.5',
  'port': '5432'
}
```

And then uses `format` to format it, where the default format is '{addr}:{port}'.

More info here: [Docker Links](https://docs.docker.com/userguide/dockerlinks/)

### `env(varname, default=None)`
Use an environment variable's value inside your template.

This filter is available even when your data source is something other that the environment.

Example:

```jinja2
User: {{ user_login }}
Pass: {{ USER_PASSWORD|env }}
```

You can provide the default value:

```jinja2
Pass: {{ USER_PASSWORD|env("-none-") }}
```

