import React from 'react';


const WfDashboard = React.lazy(() => import('./views/Wf/Dashboard/Dashboard'))
const WfStatMTTR = React.lazy(() => import('./views/Wf/Dashboard/Statistic/MTTR'))
const WfStatCoverage = React.lazy(() => import('./views/Wf/Dashboard/Statistic/Coverage'))
const Events = React.lazy(() => import('./views/Wf/Events'))
const Properties = React.lazy(() => import('./views/Wf/Properties'))
const Executions = React.lazy(() => import('./views/Wf/Workflows/Executions'))
const ExecutionPage = React.lazy(() => import('./views/Wf/Workflows/ExecutionPage'))
const WorkflowList = React.lazy(() => import('./views/Wf/Workflows/WorkflowList'))
const Workflow = React.lazy(() => import('./views/Wf/Workflows/Workflow'))


const routes = [
  { path: '/wf/dashboard', exact: true, name: 'wfDashboard', component: WfDashboard },
  { path: '/wf/dashboard/statistic/mttr', exact: true, name: 'MTTR', component: WfStatMTTR },
  { path: '/wf/dashboard/statistic/coverage', exact: true, name: 'Coverage', component: WfStatCoverage },
  { path: '/wf/events', exact: true, name: 'wfEvents', component: Events },
  { path: '/wf/properties', exact: true, name: 'wfProperties', component: Properties },
  { path: '/wf/executions', exact: true, name: 'wfExecutions', component: Executions },
  { path: '/wf/executions/:wfId', exact: true, name: 'Workflow Execution Info', component: ExecutionPage },
  { path: '/wf/workflows', exact: true, name: 'wfWorkflows', component: WorkflowList },
  { path: '/wf/workflows/:name', exact: true, name: 'Workflow Info', component: Workflow }
];

export default routes;
