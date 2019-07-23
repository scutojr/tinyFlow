import unittest
from random import randint
from collections import defaultdict

import mock

from wf.workflow import Variable, Scope, wf_proxy, WorkflowBuilder
from wf.config import PropertyManager
from wf import service_router

import tests.utils.db as db

var_local = Variable('local_var', scope=Scope.local)
var_wf = Variable('wf_var', scope=Scope.workflow)
var_overall = Variable('oa_var', scope=Scope.overall)


def task():
    var_local.set(randint(1, 10000000))
    var_wf.set(randint(1, 10000000))
    var_overall.set(randint(1, 10000000))
    wf_proxy.end()


wf1 = WorkflowBuilder('wf1')
wf2 = WorkflowBuilder('wf2')

wf1.add_task('sole task', task, entrance=True)
wf2.add_task('sole task', task, entrance=True)


class TestVariable(unittest.TestCase):

    def setUp(self):
        db.connect()
        prop_mgr = PropertyManager()
        service_router.set_prop_mgr(prop_mgr)

    def test_variable_scope(self):
        wf1_1 = wf1.build()
        wf1_2 = wf1.build()
        wf2_1 = wf2.build()
        for wf in [wf1_1, wf1_2, wf2_1]:
            wf_proxy.set_workflow(wf)
            wf.execute()

        var_pool = defaultdict(dict)
        n_wf1_1, n_wf1_2, n_wf2_1 = 'wf1_1', 'wf1_2', 'wf2_1'
        for wf, name_wf in [(wf1_1, n_wf1_1), (wf1_2, n_wf1_2), (wf2_1, n_wf2_1)]:
            wf_proxy.set_workflow(wf)
            for var in [var_local, var_wf, var_overall]:
                value = var.get()
                self.assertTrue(isinstance(value, int))
                var_pool[name_wf][var.name] = value

        n_local, n_wf, n_overall = var_local.name, var_wf.name, var_overall.name

        self.assertTrue(var_pool[n_wf1_1][n_local] != var_pool[n_wf1_2][n_local])

        self.assertTrue(var_pool[n_wf1_1][n_wf] == var_pool[n_wf1_2][n_wf])
        self.assertTrue(var_pool[n_wf1_1][n_wf] != var_pool[n_wf2_1][n_wf])

        self.assertTrue(var_pool[n_wf1_1][n_overall] == var_pool[n_wf1_2][n_overall])
        self.assertTrue(var_pool[n_wf1_1][n_overall] == var_pool[n_wf2_1][n_overall])


if __name__ == '__main__':
    unittest.main()
