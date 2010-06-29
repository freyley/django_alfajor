from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import sys
from django.conf import settings

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=False,
            help='Tells Django to NOT use the auto-reloader.'),
        make_option('--adminmedia', dest='admin_media_path', default='',
            help='Specifies the directory from which to serve admin media.'),
    )
    help = "Starts a lightweight Web server for development."
    args = '[optional port number, or ipaddr:port]'

    # Validation is called explicitly each time the server is reloaded.
    requires_model_validation = False

    def set_test_environment(self):
        try:
            test_db_name = 'test_' + settings.DATABASES['default']['NAME']
            if settings.DATABASES['default']['TEST_NAME']:
                test_db_name = settings.DATABASES['default']['TEST_NAME']
            settings.DATABASES['default']['NAME'] = test_db_name
        except AttributeError, ae:
            if settings.TEST_DATABASE_NAME:
                settings.DATABASE_NAME = settings.TEST_DATABASE_NAME
            else:
                settings.DATABASE_NAME = 'test_' + settings.DATABASE_NAME


    def handle(self, addrport='', *args, **options):
        import django
        from django.core.servers.basehttp import run, AdminMediaHandler, WSGIServerException
        from django.core.handlers.wsgi import WSGIHandler
        if args:
            raise CommandError('Usage is runserver %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)

        use_reloader = options.get('use_reloader', True)
        admin_media_path = options.get('admin_media_path', '')
        shutdown_message = options.get('shutdown_message', '')
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        def inner_run():
            from django.conf import settings
            from django.utils import translation
            print "Validating models..."
            self.validate(display_num_errors=True)
            print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
            print "Alfajor test server is running at http://%s:%s/" % (addr, port)
            print "Changing settings to use test settings"
            self.set_test_environment()
            print "Quit the server with %s." % quit_command

            # django.core.management.base forces the locale to en-us. We should
            # set it up correctly for the first request (particularly important
            # in the "--noreload" case).
            translation.activate(settings.LANGUAGE_CODE)

            try:
                handler = AdminMediaHandler(WSGIHandler(), admin_media_path)
                run(addr, int(port), handler)
            except WSGIServerException, e:
                # Use helpful error messages instead of ugly tracebacks.
                ERRORS = {
                    13: "You don't have permission to access that port.",
                    98: "That port is already in use.",
                    99: "That IP address can't be assigned-to.",
                }
                try:
                    error_text = ERRORS[e.args[0].args[0]]
                except (AttributeError, KeyError):
                    error_text = str(e)
                sys.stderr.write(self.style.ERROR("Error: %s" % error_text) + '\n')
                # Need to use an OS exit because sys.exit doesn't work in a thread
                os._exit(1)
            except KeyboardInterrupt:
                if shutdown_message:
                    print shutdown_message
                sys.exit(0)

        if use_reloader:
            from django.utils import autoreload
            autoreload.main(inner_run)
        else:
            inner_run()
