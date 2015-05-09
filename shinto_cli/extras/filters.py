""" Custom Jinja2 filters """

from jinja2 import is_undefined
import re


def docker_link(value, format='{addr}:{port}'):
    """ Given a Docker Link environment variable value, format it into something else.

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

    :param value: Docker link (from an environment variable)
    :param format: The format to apply. Supported placeholders: `{proto}`, `{addr}`, `{port}`
    :return: Formatted string
    """
    # pass undefined values on down the pipeline
    if(is_undefined(value)):
        return value

    # Parse the value
    m = re.match(r'(?P<proto>.+)://' r'(?P<addr>.+):' r'(?P<port>.+)$', value)
    if not m:
        raise ValueError('The provided value does not seems to be a Docker link: {}'.format(value))
    d = m.groupdict()

    # Format
    return format.format(**d)
