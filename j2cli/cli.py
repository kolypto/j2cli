import io, os, sys
import argparse

import jinja2
import jinja2.loaders
from . import __version__

import imp, inspect

from .context import read_context_data, FORMATS
from .extras import filters
from .extras.customize import CustomizationModule


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
        'jinja2.ext.i18n',
        'jinja2.ext.do',
        'jinja2.ext.loopcontrols',
    )

    def __init__(self, cwd, allow_undefined, no_compact=False, j2_env_params={}):
        # Custom env params
        j2_env_params.setdefault('keep_trailing_newline', True)
        j2_env_params.setdefault('undefined', jinja2.Undefined if allow_undefined else jinja2.StrictUndefined)
        j2_env_params.setdefault('trim_blocks', not no_compact)
        j2_env_params.setdefault('lstrip_blocks', not no_compact)
        j2_env_params.setdefault('extensions', self.ENABLED_EXTENSIONS)
        j2_env_params.setdefault('loader', FilePathLoader(cwd))

        # Environment
        self._env = jinja2.Environment(**j2_env_params)
        self._env.globals.update(dict(
            env=filters.env
        ))

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
    parser.add_argument('--customize', default=None, metavar='python-file.py', dest='customize',
                        help='A Python file that implements hooks to fine-tune the j2cli behavior')
    parser.add_argument('--no-compact', action='store_true', dest='no_compact',
                        help='Do not compact space around Jinja2 blocks.')
    parser.add_argument('-U', '--undefined', action='store_true', dest='undefined',
                        help='Allow undefined variables to be used in templates (no error will be raised.)')
    parser.add_argument('-o', metavar='outfile', dest='output_file', help="Output to a file instead of stdout")
    parser.add_argument('template', help='Template file to process')
    parser.add_argument('data', nargs='?', default=None, help='Input data file path; "-" to use stdin')
    args = parser.parse_args(argv)

    # Input: guess format
    if args.format == '?':
        if args.data is None or args.data == '-':
            args.format = 'env'
        else:
            args.format = {
                '.ini': 'ini',
                '.json': 'json',
                '.yml': 'yaml',
                '.yaml': 'yaml',
                '.env': 'env'
            }[os.path.splitext(args.data)[1]]

    # Input: data
    # We always expect a file;
    # unless the user wants 'env', and there's no input file provided.
    if args.format == 'env':
        # With the "env" format, if no dotenv filename is provided, we have two options:
        # either the user wants to use the current environment, or he's feeding a dotenv file at stdin.
        # Depending on whether we have data at stdin, we'll need to choose between the two.
        #
        # The problem is that in Linux, you can't reliably determine whether there is any data at stdin:
        # some environments would open the descriptor even though they're not going to feed any data in.
        # That's why many applications would ask you to explicitly specify a '-' when stdin should be used.
        #
        # And this is what we're going to do here as well.
        # The script, however, would give the user a hint that they should use '-'
        if args.data == '-':
            input_data_f = stdin
        elif args.data == None:
            input_data_f = None
        else:
            input_data_f = open(args.data)
    else:
        input_data_f = stdin if args.data is None or args.data == '-' else open(args.data)

    # Python 2: Encode environment variables as unicode
    if sys.version_info[0] == 2 and args.format == 'env':
        environ = dict((k.decode('utf-8'), v.decode('utf-8')) for k, v in environ.items())

    # Customization
    if args.customize is not None:
        customize = CustomizationModule(
            imp.load_source('customize-module', args.customize)
        )
    else:
        customize = CustomizationModule(None)

    # Read data
    context = read_context_data(
        args.format,
        input_data_f,
        environ,
        args.import_env
    )

    context = customize.alter_context(context)

    # Renderer
    renderer = Jinja2TemplateRenderer(cwd, args.undefined, args.no_compact, j2_env_params=customize.j2_environment_params())
    customize.j2_environment(renderer._env)

    # Filters, Tests
    renderer.register_filters({
        'docker_link': filters.docker_link,
        'env': filters.env,
    })
    for fname in args.filters:
        renderer.import_filters(fname)
    for fname in args.tests:
        renderer.import_tests(fname)

    renderer.register_filters(customize.extra_filters())
    renderer.register_tests(customize.extra_tests())

    # Render
    try:
        result = renderer.render(args.template, context)
    except jinja2.exceptions.UndefinedError as e:
        # When there's data at stdin, tell the user they should use '-'
        try:
            stdin_has_data = stdin is not None and not stdin.isatty()
            if args.format == 'env' and args.data == None and stdin_has_data:
                extra_info = (
                    "\n\n"
                    "If you're trying to pipe a .env file, please run me with a '-' as the data file name:\n"
                    "$ {cmd} {argv} -".format(cmd=os.path.basename(sys.argv[0]), argv=' '.join(sys.argv[1:]))
                )
                e.args = (e.args[0] + extra_info,) + e.args[1:]
        except:
            # The above code is so optional that any, ANY, error, is ignored
            pass

        # Proceed
        raise

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
    try:
        output = render_command(
            os.getcwd(),
            os.environ,
            sys.stdin,
            sys.argv[1:]
        )
    except SystemExit:
        return 1
    outstream = getattr(sys.stdout, 'buffer', sys.stdout)
    outstream.write(output)
