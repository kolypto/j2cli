""" Custom Jinja2 filters """

import re
import gnupg
import contextlib
import os
import sys

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
    # Parse the value
    m = re.match(r'(?P<proto>.+)://' r'(?P<addr>.+):' r'(?P<port>.+)$', value)
    if not m:
        raise ValueError('The provided value does not seems to be a Docker link: {}'.format(value))
    d = m.groupdict()

    # Format
    return format.format(**d)

# 2017-08-20: https://stackoverflow.com/questions/977840/redirecting-fortran-called-via-f2py-output-in-python/978264#978264
# due to a bug in gnupg (see pgp function) we need to silence a traceback when we decrypt.
@contextlib.contextmanager
def stdchannel_redirected(stdchannel, dest_filename):
    """
    A context manager to temporarily redirect stdout or stderr

    e.g.:


    with stdchannel_redirected(sys.stderr, os.devnull):
        if compiler.has_function('clock_gettime', libraries=['rt']):
            libraries.append('rt')
    """
    try:
        oldstdchannel = os.dup(stdchannel.fileno())
        dest_file = open(dest_filename, 'w')
        os.dup2(dest_file.fileno(), stdchannel.fileno())

        yield
    finally:
        if oldstdchannel is not None:
            os.dup2(oldstdchannel, stdchannel.fileno())
        if dest_file is not None:
            dest_file.close()


def gpg(value, homedir='{}/.gnupg'.format(os.getenv('HOME'))):
    """ Given a GPG value tries to decrypt it 

        Decrypt the given value with registered gpg keys

        :param value: gpg encrypted string
        :param homedir: gnupg homedir (defaults to $HOME/.gnupg)
        :return: decrypted string
    """
    ggpg = gnupg.GPG(homedir=homedir)
    ggpg.encoding = 'utf-8'

    # decrypt the given value
    # looks like we have a bug in python gnupg which causes
    # an exception thrown: https://github.com/isislovecruft/python-gnupg/issues/157
    # we "silence" the exception by passing stderr to /dev/null
    with stdchannel_redirected(sys.stderr, os.devnull):
        decrypted_value = ggpg.decrypt(value)

    if not decrypted_value.data:
        raise ValueError('Unable to decrypt the given value: {}'.format(value))

    return decrypted_value.data
