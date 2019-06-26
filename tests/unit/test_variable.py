import unittest
from random import randint
from collections import defaultdict

import mock

from wf.workflow import Workflow
from wf.executor import SimpleExecutor, set_cur_wf

import tests.utils.db as db
from wf.workflow import Variable, Scope, Workflow, Context
from wf.config import PropertyManager
from wf import service_router


var_local = Variable('local_var', scope=Scope.local)
var_wf = Variable('wf_var', scope=Scope.workflow)
var_overall = Variable('oa_var', scope=Scope.overall)


def task():
    var_local.set(randint(1, 10000000))
    var_wf.set(randint(1, 10000000))
    var_overall.set(randint(1, 10000000))

wf1 = Workflow('test_wf1')
wf2 = Workflow('test_wf2')

wf1.add_task('sole task', task, entrance=True)
wf2.add_task('sole task', task, entrance=True)


class TestVariable(unittest.TestCase):

    def setUp(self):
        db.connect()
        prop_mgr = PropertyManager()
        service_router.set_prop_mgr(prop_mgr)

        self.executor = SimpleExecutor()

    def test_variable_scope(self):
        wf1_1 = wf1.instance()
        wf1_2 = wf1.instance()
        wf2_1 = wf2.instance()

        self.executor.execute(wf1_1)
        self.executor.execute(wf1_2)
        self.executor.execute(wf2_1)

        var_pool = defaultdict(dict)
        n_local, n_wf, n_overall = var_local.name, var_wf.name, var_overall.name
        n_wf1_1, n_wf1_2, n_wf2_1 = 'wf1_1', 'wf1_2', 'wf2_1'
        for wf, name_wf in [(wf1_1, n_wf1_1), (wf1_2, n_wf1_2), (wf2_1, n_wf2_1)]:
            set_cur_wf(wf)
            for var in [var_local, var_wf, var_overall]:
                name_var = var.name
                var_pool[name_wf][name_var] = var.get()

        self.assertTrue(var_pool[n_wf1_1][n_local] != var_pool[n_wf1_2][n_local])

        self.assertTrue(var_pool[n_wf1_1][n_wf] == var_pool[n_wf1_2][n_wf])
        self.assertTrue(var_pool[n_wf1_1][n_wf] != var_pool[n_wf2_1][n_wf])

        self.assertTrue(var_pool[n_wf1_1][n_overall] == var_pool[n_wf1_2][n_overall])
        self.assertTrue(var_pool[n_wf1_1][n_overall] == var_pool[n_wf2_1][n_overall])


if __name__ == '__main__':
    unittest.main()
