import os.path as op
import mongoengine as me
import logging
from ConfigParser import ConfigParser
from threading import RLock


HOME = op.abspath(op.join(op.dirname(__name__), '..'))


__all__ = [
    'Configuration', 'Property', 'PropertyManager'
]

_built_in_vars = [
    ('HOME', HOME)  # root dir of this project
]

_types = {
    'int': int,
    'float': float,
    'string': str
}

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

    def get(self, name, default=None):
        return self.props.get(name, default)

    def set(self, name, value):
        self.props[name] = value


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
        self.prop_pool = PropertyPool.new()

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

            prop = self.prop_pool.properties[namespace][name].copy()

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
        with self.lock:
            if self.prop_pool is None:
                self._load_prop_pool()
            return self.prop_pool.properties[namespace].get(name, default)
