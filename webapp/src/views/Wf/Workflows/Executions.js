import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import TableBuilder from './TableBuilder';



const link = (
  <Link to={"/wf/executions/wfId"}>this is a link for execution info of this workflow</Link>
);

const headers = [
  "Time", "Workflow", "Triggered By", "State"
];

const datas = [
  [12345, link, "event info", "successful"]
]


class Executions extends Component {

  render() {
    return (
      <div className="animated fadeIn">
        <TableBuilder {...{ headers, datas }} />
      </div>
    )
  }
}

export default Executions;