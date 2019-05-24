import io, os, sys
import argparse

import jinja2
import jinja2.loaders
from . import __version__

import imp, inspect

from .context import read_context_data, FORMATS
from .extras import filters


class FilePathLoader(jinja2.BaseLoader):
    """ Custom Jinja2 template loader which just loads a single template file """

    def __init__(self, cwd, encoding='utf-8'):
        self.cwd = cwd
        self.encoding = encoding

    def get_source(self, environment, template):
        # Path
        filename = os.path.join(self.cwd, template)

        # Read
        try:
            with io.open(template, 'rt', encoding=self.encoding) as f:
                contents = f.read()
        except IOError:
            raise jinja2.TemplateNotFound(template)

        # Finish
        uptodate = lambda: False
        return contents, filename, uptodate


class Jinja2TemplateRenderer(object):
    """ Template renderer """

    ENABLED_EXTENSIONS=(
        # TODO: some day, we will load custom extensions from the CLI. Will we?
        'jinja2.ext.i18n',
        'jinja2.ext.do',
        'jinja2.ext.loopcontrols',
    )

    def __init__(self, cwd, allow_undefined, environment_config=None):
        self._env = jinja2.Environment(
            extensions=self.ENABLED_EXTENSIONS,
            loader=FilePathLoader(cwd),
            undefined=jinja2.Undefined if allow_undefined else jinja2.StrictUndefined,  # raise errors for undefineds?
            keep_trailing_newline=True,
            **(environment_config or {})
        )

    def register_filters(self, filters):
        self._env.filters.update(filters)

    def register_tests(self, tests):
        self._env.tests.update(tests)

    def import_filters(self, filename):
        self.register_filters(self._import_functions(filename))

    def import_tests(self, filename):
        self.register_tests(self._import_functions(filename))

    def _import_functions(self, filename):
        m = imp.load_source('imported-funcs', filename)
        return dict((name, func) for name, func in inspect.getmembers(m) if inspect.isfunction(func))

    def render(self, template_path, context):
        """ Render a template
        :param template_path: Path to the template file
        :type template_path: basestring
        :param context: Template data
        :type context: dict
        :return: Rendered template
        :rtype: basestring
        """
        return self._env \
            .get_template(template_path) \
            .render(context) \
            .encode('utf-8')



def render_command(cwd, environ, stdin, argv):
    """ Pure render command
    :param cwd: Current working directory (to search for the files)
    :type cwd: basestring
    :param environ: Environment variables
    :type environ: dict
    :param stdin: Stdin stream
    :type stdin: file
    :param argv: Command-line arguments
    :type argv: list
    :return: Rendered template
    :rtype: basestring
    """
    parser = argparse.ArgumentParser(
        prog='j2',
        description='Command-line interface to Jinja2 for templating in shell scripts.',
        epilog=''
    )
    parser.add_argument('-v', '--version', action='version',
                        version='j2cli {0}, Jinja2 {1}'.format(__version__, jinja2.__version__))

    parser.add_argument('-f', '--format', default='?', help='Input data format', choices=['?'] + list(FORMATS.keys()))
    parser.add_argument('-e', '--import-env', default=None, metavar='VAR', dest='import_env',
                        help='Import environment variables as `var` variable. Use empty string to import into the top level')
    parser.add_argument('--filters', nargs='+', default=[], metavar='python-file', dest='filters',
                        help='Load custom Jinja2 filters from a Python file: all top-level functions are imported.')
    parser.add_argument('--tests', nargs='+', default=[], metavar='python-file', dest='tests',
                        help='Load custom Jinja2 tests from a Python file.')
    parser.add_argument('--undefined', action='store_true', dest='undefined', help='Allow undefined variables to be used in templates (no error will be raised)')
    parser.add_argument('--environment-config', required=False)
    parser.add_argument('-o', metavar='outfile', dest='output_file', help="Output to a file instead of stdout")
    parser.add_argument('template', help='Template file to process')
    parser.add_argument('data', nargs='?', default='-', help='Input data path')
    args = parser.parse_args(argv)

    def guess_format(filename):
        return {
            '.ini': 'ini',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.env': 'env'
        }[os.path.splitext(filename)[1]]

    # Input: guess format
    if args.format == '?':
        if args.data == '-':
            args.format = 'env'
        else:
            args.format = guess_format(args.data)

    # Input: data
    if args.data == '-' and args.format == 'env':
        input_data_f = None
    else:
        input_data_f = stdin if args.data == '-' else open(args.data)

    # Python 2: Encode environment variables as unicode
    if sys.version_info[0] == 2 and args.format == 'env':
        environ = dict((k.decode('utf-8'), v.decode('utf-8')) for k, v in environ.items())

    # Read data)
    context = read_context_data(
        args.format,
        input_data_f,
        environ,
        args.import_env
    )

    if args.environment_config:
        with open(args.environment_config) as env_config_f:
            env_config = read_context_data(guess_format(args.environment_config),
                                           env_config_f)

    else:
        env_config = None

    # Renderer
    renderer = Jinja2TemplateRenderer(cwd, args.undefined, env_config)

    # Filters, Tests
    renderer.register_filters({
        'docker_link': filters.docker_link,
        'env': filters.env,
    })
    for fname in args.filters:
        renderer.import_filters(fname)
    for fname in args.tests:
        renderer.import_tests(fname)

    # Render
    result = renderer.render(args.template, context)

    # -o
    if args.output_file:
        with io.open(args.output_file, 'wt', encoding='utf-8') as f:
            f.write(result.decode('utf-8'))
            f.close()
        return b''

    # Finish
    return result



def main():
    """ CLI Entry point """
    output = render_command(
        os.getcwd(),
        os.environ,
        sys.stdin,
        sys.argv[1:]
    )
    outstream = getattr(sys.stdout, 'buffer', sys.stdout)
    outstream.write(output)
