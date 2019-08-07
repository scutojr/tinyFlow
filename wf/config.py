from socket import gethostbyname, getfqdn
import os.path as op
import mongoengine as me
import logging
from ConfigParser import ConfigParser
from threading import RLock


__all__ = [
    'Configuration', 'Property', 'PropertyManager'
]

HTTP_PORT = 'http_port'

HOME = op.abspath(op.join(op.dirname(__name__), '..'))
PACK_DIR = 'pack_dir'
PACK_LEGACY_DIR = 'pack_legacy_dir'

LOG_DIR = 'log_dir'
DB_HOST = 'db_host'
DB_PORT = 'db_port'
DB_NAME = 'test'

MQ_EVENT_LISTENER_ENABLE = 'mq_event_listener_enable'
MQ_TOPIC = 'mq_topic'
MQ_ADDRESS = 'mq_address'

EXECUTOR_POOL_SIZE = 'executor_pool_size'
EXECUTOR_MODE = 'executor_mode'
EXECUTOR_MASTER_TOPIC = 'executor_master_topic'
EXECUTOR_RUNNER_TOPIC = 'executor_runner_topic'
EXECUTOR_MASTER_HOST = 'executor_master_host'
EXECUTOR_MASTER_PORT = 'executor_master_port'


_built_in_vars = [
    ('HOME', HOME)  # root dir of this project
]
configuration = None


def _render(value):
    for tag, v in _built_in_vars:
        value.replace('$' + tag, v)
    return value


def load(file_path):
    """
    rtype: Configuration
    """
    global configuration
    section, conf = 'tinyFlow', Configuration()
    parser = ConfigParser()
    if parser.read(file_path) < 1:
        raise Exception('failed to load %s, it may not exist!' % (file_path))
    for name, value in parser.items(section):
        conf.set(name, _render(value))
    configuration = conf
    return conf


class Configuration(object):
    def __init__(self):
        self.props = {}
        self._master_host = None
        self._runner_host = None

    def get(self, name, default=None):
        return self.props.get(name, default)

    def set(self, name, value):
        self.props[name] = value

    def get_mq_host_and_ports(self):
        host_and_ports = self.get(MQ_ADDRESS, 'amq_test_server:61613')
        host_and_ports = [tuple(hp.strip().split(':', 1)) for hp in host_and_ports.split(',') if hp.strip()]
        return host_and_ports

    @property
    def role(self):
        """
        roles: runner, tobot
        """
        return self._role

    @role.setter
    def role(self, role_name):
        self._role = role_name

    @property
    def mode(self):
        return self.get(EXECUTOR_MODE, 'local').strip()

    @property
    def master_host(self):
        if not self._master_host:
            if self.role == 'tobot':
                self._master_host = gethostbyname(getfqdn())
            else:
                self._master_host = self.get(EXECUTOR_MASTER_HOST, 'localhost')
        return self._master_host

    @property
    def http_port(self):
        return self.get(HTTP_PORT, 54321)


class Property(me.EmbeddedDocument):
    name = me.StringField(default='')
    value = me.StringField(default='')
    description = me.StringField(default='')
    vtype = me.StringField(default='')

    def copy(self):
        return Property(
            name=self.name,
            value=self.value,
            vtype=self.vtype,
            description=self.description
        )


class PropertyPool(me.Document):
    id = me.StringField(default='property_pool', primary_key=True)
    properties = me.DictField(
        field=me.DictField(
            field=me.EmbeddedDocumentField(Property)
        )
    )

    @staticmethod
    def new():
        doc = PropertyPool.objects().first()
        if doc is None:
            #doc = PropertyPool(id=PropertyPool._default_id)
            doc = PropertyPool()
            doc.save()
        return doc

    def has_namespace(self, ns):
        return ns in self.properties

    def get_prop(self, ns, name=''):
        """
        :return: if name is omited, a list of property under ns is return
        """
        if not name:
            return [p.copy() for p in self.properties[ns].values()]
        prop = self.properties[ns].get(name, None)
        if prop:
            return prop.copy()
        else:
            return None


class PropertyManager(object):

    _default_ns = ':default'

    def __init__(self):
        self.lock = RLock()
        self.logger = logging.getLogger(PropertyManager.__name__)
        self._load_prop_pool()

    def get_property(self, name='', namespace=''):
        """
        :param name:
        :param namespace:
        :return: None if property does not exist
        """
        namespace = namespace or self._default_ns
        if not self.prop_pool.has_namespace(namespace):
            return None
        return self.prop_pool.get_prop(namespace, name)

    def get_property_from_db(self, name, namespace=''):
        namespace = namespace or self._default_ns
        return self.prop_pool.reload().properties[namespace].get(name, None)

    def _load_prop_pool(self):
        try:
            self.prop_pool = PropertyPool.new()
        except:
            msg = 'failed to read from MongoDB, please check DB status'
            self.logger.exception(msg)
            raise Exception(msg)

    def _reload_prop_pool(self, ops=''):
        try:
            self.prop_pool.reload()
        except Exception as e:
            self.logger.exception('failed to reload document after ' + ops)
            self.prop_pool = None
            raise e

    def create_property(self, name, value=None, description=None, vtype=None, namespace=''):
        # TODO: validate the namespace, name and vtype
        prop = Property(
            name=name, value=value, vtype=vtype,
            description=description
        )
        with self.lock:
            if self.prop_pool is None:
                self._load_prop_pool()
            prop_pool, namespace = self.prop_pool, namespace or self._default_ns
            path = '__'.join(['properties', namespace, name])
            qry = {path: {'$exists': False}}
            updater = {'set__' + path: prop}
            if prop_pool.modify(qry, **updater):
                self._reload_prop_pool('create property')
            else:
                raise Exception('Property with name <%s> is already existed in namespace <%s>' % (name, namespace))

    def remove_property(self, name, namespace=''):
        with self.lock:
            if self.prop_pool is None:
                self._load_prop_pool()
            namespace = namespace or self._default_ns
            flag = self.prop_pool.modify(**{
                '__'.join(['unset', 'properties', namespace, name]): ''
            })
            if flag:
                self._reload_prop_pool('remove property')
            else:
                raise Exception('failed to remove property: %s.%s' % (name, namespace))

    def update_property(self, name, new_name=None, value=None, description=None, vtype=None, namespace=''):
        """
        TODO: validate the maching of value and vtype; new_name has existed; it's wrong if new_name is empty?
        """
        with self.lock:
            if self.prop_pool is None:
                self._load_prop_pool()
            namespace = namespace or self._default_ns

            prop = self.get_property(name=name, namespace=namespace)
            if prop is None:
                prop = Property(name=name)

            value is not None and setattr(prop, 'value', value)
            description is not None and setattr(prop, 'description', description)
            vtype is not None and setattr(prop, 'vtype', vtype)

            def get_path(opt, name):
                return '__'.join([opt, 'properties', namespace, name])

            if new_name is None or name == new_name:
                flag = self.prop_pool.modify(**{get_path('set', name): prop})
            else:
                prop.name = new_name
                flag = self.prop_pool.modify(**{
                    get_path('set', new_name): prop,
                    get_path('unset', name): ''
                })
            if flag:
                self._reload_prop_pool('update property')
            else:
                raise Exception('failed to update property: %s.%s' % (name, namespace))

    def get_value(self, name, default='', namespace=''):
        prop = self.get_property(name, namespace)
        return prop and prop.value or default
