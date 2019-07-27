import React, { Component } from 'react';
import { Badge } from 'reactstrap';


const states = {
  scheduling: {
    reason: 'the workflow is in the running queue of executor.',
    label: <Badge color="secondary">scheduling</Badge>
  },
  running: {
    reason: 'the workflow is running.',
    label: <Badge color="primary">running</Badge>
  },
  interacting: {
    reason: 'the workflow is waiting for user decision.',
    label: <Badge color="warning">interacting</Badge>
  },
  waiting: {
    reason: 'the workflow is waiting for specific event to occur.',
    label: <Badge color="warning">waiting</Badge>
  },
  asking: {
    reason: 'the workflow is asking the user for decision.',
    label: <Badge color="warning">asking</Badge>
  },
  successful: {
    reason: 'the workflow is successful with no exception.',
    label: <Badge color="success">successful</Badge>
  },
  succeed: {
    reason: 'the workflow is successful with no exception.',
    label: <Badge color="success">succeed</Badge>
  },
  failed: {
    reason: 'the workflow is failed with exception.',
    label: <Badge color="danger">failed</Badge>
  },
  crashed: {
    reason: 'the workflow is failed because system is crash.',
    label: <Badge color="dark">crashed</Badge>
  },
  unknown: {
    reason: 'unknown state.',
    label: <Badge color="dark">unknown</Badge>
  }
}


function StateLabel(state) {
  let label = states[state];
  if (label == undefined) {
    label = states.unknown
  }
  return label;
}


function EventStateLabel(state) {
  switch (state) {
    case "info":
      return <Badge color="success">{state}</Badge>
    case "warning":
      return <Badge color="warning">{state}</Badge>
    case "critical":
      return <Badge color="danger">{state}</Badge>
    default:
      return <Badge color="dark">{state}</Badge>
  }
}


export { StateLabel, EventStateLabel };