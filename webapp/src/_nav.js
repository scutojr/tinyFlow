export default {
  items: [
    {
      name: 'Dashboard',
      url: '/dashboard',
      icon: 'icon-speedometer',
      badge: {
        variant: 'info',
        text: 'NEW',
      },
    },
    {
      name: 'WfDashboard',
      url: '/wf/dashboard',
      icon: 'icon-calculator'
    },
    {
      name: 'Events',
      url: '/wf/events',
      icon: 'icon-calculator'
    },
    {
      name: 'Workflow',
      url: '/',
      icon: 'icon-puzzle',
      children: [
        {
          name: 'Execution',
          url: '/wf/executions',
          icon: 'icon-puzzle',
        },
        {
          name: 'Definition',
          url: '/wf/workflows',
          icon: 'icon-puzzle',
        },
      ]
    },
    {
      name: 'Properties',
      url: '/wf/properties',
      icon: 'icon-calculator'
    },
  ],
};
