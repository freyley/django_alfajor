import sys

from django.conf import settings

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

