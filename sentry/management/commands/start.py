"""
sentry.management.commands.start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option


class Command(BaseCommand):
    args = '<service>'
    help = 'Starts the specified service'

    option_list = BaseCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False),
        make_option('--noupgrade',
            action='store_false',
            dest='upgrade',
            default=True),
    )

    def handle(self, service_name='http', upgrade=True, **options):
        from sentry.services import http, udp

        services = {
            'http': http.SentryHTTPServer,
            'udp': udp.SentryUDPServer,
        }

        if service_name == 'worker':
            raise CommandError('The ``worker`` service has been replaced with ``celeryd``.')

        if upgrade:
            # Ensure we perform an upgrade before starting any service
            print "Performing upgrade before service startup..."
            call_command('upgrade', verbosity=0)

        try:
            service_class = services[service_name]
        except KeyError:
            raise CommandError('%r is not a valid service' % service_name)

        service = service_class(
            debug=options['debug'],
        )

        print "Running service: %r" % service_name
        service.run()
