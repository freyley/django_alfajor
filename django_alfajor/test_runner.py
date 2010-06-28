# This code adapted from nose_runner, found
# here: http://blog.jeffbalogh.org/post/57653515/nose-test-runner-for-django


"""
Django test runner that invokes nose.

Usage:
    ./manage.py test DJANGO_ARGS -- NOSE_ARGS

The 'test' argument, and any other args before '--', will not be passed
to nose, allowing django args and nose args to coexist.

You can use

    NOSE_ARGS = ['list', 'of', 'args']

in settings.py for arguments that you always want passed to nose.
"""
import sys

from django.conf import settings
from django.db import connection
from django.test import utils

import nose

SETUP_ENV = 'setup_test_environment'
TEARDOWN_ENV = 'teardown_test_environment'
import logging
log = logging.getLogger(__name__)
from nose.importer import add_path, remove_path
from nose.util import ispackage
from nose.failure import Failure
import os
op_abspath = os.path.abspath
op_join = os.path.join
op_isfile = os.path.isfile
op_isdir = os.path.isdir

class TestLoader(nose.loader.TestLoader):

    def loadTestsFromDir(self, path):
        log.debug("load from dir %s", path)
        plugins = self.config.plugins
        plugins.beforeDirectory(path)
        if self.config.addPaths:
            paths_added = add_path(path, self.config)
        entries = os.listdir(path)
        def no_func(x):
            return x not in settings.ALFAJOR_NAMES
        entries = filter(no_func, entries)
        for entry in entries:
            # this hard-coded initial-dot test will be removed:
            # http://code.google.com/p/python-nose/issues/detail?id=82
            if entry.startswith('.'):
                continue
            entry_path = op_abspath(op_join(path, entry))
            is_file = op_isfile(entry_path)
            wanted = False
            if is_file:
                is_dir = False
                wanted = self.selector.wantFile(entry_path)
            else:
                is_dir = op_isdir(entry_path)
                if is_dir:
                    # this hard-coded initial-underscore test will be removed:
                    # http://code.google.com/p/python-nose/issues/detail?id=82
                    if entry.startswith('_'):
                        continue
                    wanted = self.selector.wantDirectory(entry_path)
            is_package = ispackage(entry_path)
            if wanted:
                if is_file:
                    plugins.beforeContext()
                    if entry.endswith('.py'):
                        yield self.loadTestsFromName(
                            entry_path, discovered=True)
                    else:
                        yield self.loadTestsFromFile(entry_path)
                    plugins.afterContext()
                elif is_package:
                    # Load the entry as a package: given the full path,
                    # loadTestsFromName() will figure it out
                    yield self.loadTestsFromName(
                        entry_path, discovered=True)
                else:
                    # Another test dir in this one: recurse lazily
                    yield self.suiteClass(
                        lambda: self.loadTestsFromDir(entry_path))
        tests = []
        for test in plugins.loadTestsFromDir(path):
            tests.append(test)
        # TODO: is this try/except needed?
        try:
            if tests:
                yield self.suiteClass(tests)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            yield self.suiteClass([Failure(*sys.exc_info())])
        
        # pop paths
        if self.config.addPaths:
            map(remove_path, paths_added)
        plugins.afterDirectory(path)


def get_test_enviroment_functions():
    """The functions setup_test_environment and teardown_test_environment in
    <appname>.tests modules will be automatically called before and after
    running the tests.
    """
    setup_funcs = []
    teardown_funcs = []
    for app_name in settings.INSTALLED_APPS:
        mod = __import__(app_name, fromlist=['tests'])
        if hasattr(mod, 'tests'):
            if hasattr(mod.tests, SETUP_ENV):
                setup_funcs.append(getattr(mod.tests, SETUP_ENV))
            if hasattr(mod.tests, TEARDOWN_ENV):
                teardown_funcs.append(getattr(mod.tests, TEARDOWN_ENV))
    return setup_funcs, teardown_funcs


def setup_test_environment(setup_funcs):
    utils.setup_test_environment()
    for func in setup_funcs:
        func()


def teardown_test_environment(teardown_funcs):
    utils.teardown_test_environment()
    for func in teardown_funcs:
        func()


def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    setup_funcs, teardown_funcs = get_test_enviroment_functions()
    # Prepare django for testing.
    setup_test_environment(setup_funcs)
    old_db_name = settings.DATABASE_NAME
    connection.creation.create_test_db(verbosity, autoclobber=not interactive)

    # Pretend it's a production environment.
    settings.DEBUG = False

    for label in test_labels:
        if label in settings.ALFAJOR_NAMES:
            settings.ALFAJOR_NAMES.remove(label)

    nose_argv = ['nosetests']
    if hasattr(settings, 'NOSE_ARGS'):
        nose_argv.extend(settings.NOSE_ARGS)

    # Everything after '--' is passed to nose.
    if '--' in sys.argv:
        hyphen_pos = sys.argv.index('--')
        nose_argv.extend(sys.argv[hyphen_pos + 1:])

    if verbosity >= 1:
        print ' '.join(nose_argv)

    nose.run(argv=nose_argv, testLoader=TestLoader)

    # Clean up django.
    connection.creation.destroy_test_db(old_db_name, verbosity)
    teardown_test_environment(teardown_funcs)
