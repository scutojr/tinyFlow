import json
import unittest
import os.path as op
from copy import deepcopy
from threading import Thread

from mock import patch, Mock
from mongoengine.connection import MongoEngineConnectionError

import wf.config as config
import tests.utils.db as db
import tests.utils.http as http
import tests.utils.server as server

FAIL = 'FAILED'
SUCC = 'SUCCESSFUL'


class TestConfig(unittest.TestCase):
    def setUp(self):
        pass

    def test_built_in_vars(self):
        home_dir = op.abspath(op.join(op.dirname(__name__), '..'))
        self.assertTrue(
            home_dir == config.HOME,
            'home dir is wrong, you may change the path of config module'
        )


class TestPropertyManager(unittest.TestCase):

    def setUp(self):
        self.props = [
            config.Property(name='p1', value='p1'),
            config.Property(name='p2', value='p2'),
            config.Property(name='p3', value='p3'),
        ]
        self.p1 = {
            'name': 'p1', 'value': 'p1'
        }

        self.p2 = {
            'name': 'p2', 'value': 'p2'
        }
        self.conn = db.connect()
        self.prop_mgr = config.PropertyManager()

    def tearDown(self):
        cls = [
            config.PropertyPool
        ]
        db.drop(*cls)

    def _ensure_db_and_memory_consistency(self):
        prop_pool = self.prop_mgr.prop_pool
        self.assertTrue(
            prop_pool == prop_pool.reload()
        )

    def test_all(self):
        for func in [
            self._test_create_property,
            self._test_remove_property,
            self._test_update_property
        ]:
            try:
                self.setUp()
                func()
            finally:
                self.tearDown()

    def _test_create_property(self):
        """
        1. repeatedly add
        2. failed if mongoengine is closed
        3. different namespace
        """
        prop_mgr, p1, p2 = self.prop_mgr, self.p1, self.p2
        n1, n2 = 'n1', 'n2'

        self.assertTrue(prop_mgr.get_property(p1['name']) == None)
        prop_mgr.create_property(**p1)
        self.assertTrue(prop_mgr.get_property(p1['name']).name == p1['name'])

        try:
            prop_mgr.create_property(**p1)
            self.assertTrue(False, 'add the same property repeatedly is wrong!')
        except:
            pass

        prop_mgr.create_property(namespace=n1, **p1)
        prop_mgr.create_property(namespace=n2, **p1)
        p1_in_n1, p1_in_n2 = prop_mgr.get_property(p1['name'], n1), prop_mgr.get_property(p1['name'], n2)
        self.assertTrue(
            p1_in_n1 != None and p1_in_n2 != None and id(p1_in_n1) != id(p1_in_n2) and \
            p1_in_n1.name == p1_in_n2.name,
            'same property are different object if added to different namespace'
        )

        self._ensure_db_and_memory_consistency()

        db.disconnect(conn=self.conn)
        try:
            with patch.object(prop_mgr, 'prop_pool')as mock:
                mock.modify = Mock(side_effect=Exception)
                prop_mgr.create_property(**p2)
                self.assertTrue(
                    False,
                    'MongoDB is closed, exception should be raised while trying to updating DB'
                )
        except Exception as e:
            self.assertTrue(
                prop_mgr.get_property(p2['name']) == None,
                'DB connection is closed, property must not be added'
            )

    def _test_remove_property(self):
        prop_mgr, p1, p2 = self.prop_mgr, self.p1, self.p2
        prop_mgr.create_property(**p1)
        prop_mgr.create_property(**p2)

        prop_mgr.remove_property(p1['name'])
        self.assertTrue(prop_mgr.get_property(p1['name']) == None, 'prop should be removed!')
        self.assertTrue(prop_mgr.get_property_from_db(p1['name']) == None, 'prop should be removed from DB!')

        prop_mgr.remove_property(p2['name'])
        self.assertTrue(prop_mgr.get_property(p2['name']) == None, 'prop should be removed!')
        self.assertTrue(prop_mgr.get_property_from_db(p2['name']) == None, 'prop should be removed from DB!')

        self._ensure_db_and_memory_consistency()

    def _test_update_property(self):
        prop_mgr, p1, p2 = self.prop_mgr, self.p1, self.p2
        prop_mgr.create_property(**p1)
        prop_mgr.create_property(**p2)


        new_val = 'this is a new value to be updated'
        prop_mgr.update_property(p1['name'], value=new_val)
        self.assertTrue(prop_mgr.get_property(p1['name']).value == new_val)

        new_name, old_p2 = 'p3', prop_mgr.get_property(p2['name']).to_mongo()
        prop_mgr.update_property(p2['name'], new_name=new_name)
        self.assertTrue(prop_mgr.get_property(p2['name']) == None)
        self.assertTrue(prop_mgr.get_property(new_name) != None)

        self._ensure_db_and_memory_consistency()


class PropMgrHttpApi():
    def __init__(self, host, port):
        self.h = host
        self.p = port

    def get_property(self, name, namespace=''):
        endpoint = '/properties/' + name
        if namespace:
            endpoint += '?namespace=' + namespace
        status, reason, msg = http.get(self.h, self.p, endpoint)
        return json.loads(msg)

    def list_property(self, namespace=''):
        endpoint = '/properties/?namespace=' + namespace
        status, reason, msg = http.get(self.h, self.p, endpoint)
        return json.loads(msg)

    def remove_property(self, name, namespace=''):
        endpoint = '/properties/' + name
        if namespace:
            endpoint += '?namespace=' + namespace
        return http.delete(self.h, self.p, endpoint)

    def update_property(self, name, new_name='', value='', description='', vtype='', namespace=''):
        body = {}
        new_name and body.update(name=new_name)
        value and body.update(value=value)
        description and body.update(description=description)
        vtype and body.update(vtype=vtype)

        endpoint = '/properties/' + name
        if namespace:
            endpoint += '?namespace=' + namespace

        status, reason, msg = http.post(self.h, self.p, endpoint, json.dumps(body))
        return json.loads(msg)


class TestPropertyManagerByHttp(unittest.TestCase):

    def _create_prop(self, name, value='', description='', vtype=''):
        return dict(name=name, value=value, description=description, vtype=vtype)

    def setUp(self):
        self.api = PropMgrHttpApi('localhost', 54321)

        self.p1 = self._create_prop(name='p1', value='value-p1')
        self.p2 = self._create_prop(name='p2', value='value-p2')
        self.p3 = self._create_prop(name='p3', value='value-p3')
        self.p4 = self._create_prop(name='p4', value='value-p4')

        self.props = self._sort_props([self.p1, self.p2, self.p3, self.p4])

        self.ns = ['', 'n1', 'n2']

        server.start_server()

    def tearDown(self):
        db.drop(config.PropertyPool)

    def test_all(self):
        self._test_prop_create_and_list()
        self._test_get_prop()
        self._test_update_prop()
        self._test_prop_remove()

    def _test_prop_create_and_list(self):
        n0, n1, n2 = self.ns
        for prop in self.props:
            self.api.update_property(namespace=n1, **prop)

        for prop in self.props[:3]:
            self.api.update_property(namespace=n2, **prop)

        list1 = self.api.list_property(n1)['response']
        list2 = self.api.list_property(n2)['response']

        self._sort_props(list1)
        self._sort_props(list2)

        self.assertTrue(list1 == self.props)
        self.assertTrue(list2 == self.props[:3])

    def _test_get_prop(self):
        # case that get a non-existed property
        # case test exception for special case

        n1 = self.ns[1]
        for prop in self.props:
            p = self.api.get_property(prop['name'], n1)['response']
            self.assertTrue(prop == p)

    def _test_update_prop(self):
        n1 = self.ns[1]
        new_val = 'value updated'
        new_p = deepcopy(self.p1)
        new_p['description'] = new_val

        self.assertTrue(
            self.api.update_property(
                namespace=n1,
                name=new_p['name'],
                description=new_val
            )['status'] == SUCC
        )
        p_from_server = self.api.get_property(new_p['name'], n1)['response']
        self.assertTrue(p_from_server == new_p)

        # case that update the name
        new_name = 'new_p1'
        self.assertTrue(
            self.api.update_property(
                namespace=n1,
                name=new_p['name'],
                new_name=new_name
            )['status'] == SUCC
        )
        new_p['name'] = new_name
        p_from_server = self.api.get_property(new_p['name'], n1)['response']
        self.assertTrue(p_from_server == new_p)

    def _sort_props(self, props):
        props.sort(key=lambda p: p['name'])
        return props

    def _test_prop_remove(self):
        n2 = self.ns[2]
        props = self.api.list_property(n2)['response']
        self.assertTrue(self._sort_props(props) == self.props[:3])

        self.api.remove_property(self.p3['name'], n2)
        props = self.api.list_property(n2)['response']
        self.assertTrue(self._sort_props(props) == self.props[:2])


if __name__ == '__main__':
    unittest.main()
