import React from 'react';
import { objectExpression } from '@babel/types';


const WfDashboard = React.lazy(() => import('./views/Wf/Dashboard/Dashboard'))
const WfStatMTTR = React.lazy(() => import('./views/Wf/Dashboard/Statistic/MTTR'))
const WfStatCoverage = React.lazy(() => import('./views/Wf/Dashboard/Statistic/Coverage'))
const Events = React.lazy(() => import('./views/Wf/Events'))
const Properties = React.lazy(() => import('./views/Wf/Properties'))
const ExecutionsPage = React.lazy(() => import('./views/Wf/Workflows/ExecutionsPage'))
const ExecutionPage = React.lazy(() => import('./views/Wf/Workflows/ExecutionPage'))
const WorkflowList = React.lazy(() => import('./views/Wf/Workflows/WorkflowList'))
const Workflow = React.lazy(() => import('./views/Wf/Workflows/Workflow'))


const routes = {
  dashboard: { path: '/wf/dashboard', exact: true, name: 'wfDashboard', component: WfDashboard },
  mttr: { path: '/wf/dashboard/statistic/mttr', exact: true, name: 'MTTR', component: WfStatMTTR },
  coverage: { path: '/wf/dashboard/statistic/coverage', exact: true, name: 'Coverage', component: WfStatCoverage },
  events: { path: '/wf/events', exact: true, name: 'wfEvents', component: Events },
  properties: { path: '/wf/properties', exact: true, name: 'wfProperties', component: Properties },
  executions: { path: '/wf/executions', exact: true, name: 'wfExecutions', component: ExecutionsPage },
  execution: {
    path: '/wf/executions/:wfId',
    exact: true,
    name: 'Workflow Execution Info',
    component: ExecutionPage,
    urlBuilder: (wfId) => '/wf/executions/' + wfId
  },
  workflows: {
    path: '/wf/workflows',
    exact: true,
    name: 'wfWorkflows',
    component: WorkflowList
  },
  workflow: {
    path: '/wf/workflows/:name',
    exact: true,
    name: 'Workflow Info',
    component: Workflow,
    urlBuilder: (name) => '/wf/workflows/' + name
  }
};

export default routes;