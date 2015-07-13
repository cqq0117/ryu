"""
This file define the domain in OXP communication.
Author:www.muzixing.com

The main component of OXP role.
    - Handle connection with Super Controller as a client socket
    - Gerenrate and route event to appropriate entitlies like ryu applications.

"""

import contextlib
from ryu import cfg
import logging
import ssl

from ryu.lib import hub
from ryu.lib.hub import StreamServer
import eventlet
from eventlet.green import socket

from ryu.openexchange import oxproto
from ryu.openexchange import oxproto_common
from ryu.openexchange import oxproto_parser
from ryu.openexchange import oxproto_protocol
from ryu.openexchange import oxproto_v1_0
from ryu.openexchange import oxp_event
from ryu.openexchange import oxp_super


LOG = logging.getLogger('ryu.lib.openexchange.oxp_domain')

CONF = cfg.CONF


def _deactivate(method):
    def deactivate(self):
        try:
            method(self)
        finally:
            self.is_active = False
    return deactivate


class Domain_Controller(object):
    def __init__(self):
        super(Domain_Controller, self).__init__()
        # role
        self.role = CONF.oxp_role
        self.server = CONF.oxp_server_ip
        self.port = CONF.oxp_server_port
        self.address = (self.server, self.port)

        self.socket = None
        self.is_active = True
        self.super_controller = None

    # entry point
    def __call__(self):
        self._connect()

    def _connect(self):
        self.socket = eventlet.connect((self.server, self.port))
        self.super_controller = super_connection(self.socket, self.address)

    def work_flow(self):
        # we should do something related.
        pass


class Super_Controller(oxp_super.Domain_Network):
    def __init__(self, socket, address):
        super(Super_Controller, self).__init__(socket, address)
        # role
        self.is_super = True


def super_connection(socket, address):
    LOG.info('Connect to Super Controller:%s address:%s', socket, address)
    with contextlib.closing(Super_Controller(socket, address)) as _super:
        try:
            # Domain_Network.serve()
            _super.serve()
            return _super
        except:
            # Something went wrong.
            # Especially malicious switch can send malformed packet,
            # the parser raise exception.
            # Can we do anything more graceful?

            # TODO: class domain and did_to_str
            if _super.id is None:
                domain_str = "%s" % _super.id
            else:
                domain_str = did_to_str(_super.id)
            LOG.error("Error in the domain %s from %s", domain_str, address)
            raise
