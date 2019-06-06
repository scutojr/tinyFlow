import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import { Card, CardBody } from 'reactstrap';

import TableBuilder from './TableBuilder';


let wfs = {
  "sleepy_wf": {
    "description": "this is a sleepy workflow",
    "graph": {
      "sleepy task": {},
      "task end": {},
      "task start": {
        "fail": "task c",
        "succeed": "task b"
      }
    },
    "name": "sleepy_wf"
  },
  "permission_wf": {
    "description": "this is a permission workflow",
    "graph": {
      "sleepy task": {},
      "task end": {},
      "task start": {
        "fail": "task c",
        "succeed": "task b"
      }
    },
    "name": "permission_wf"
  }
}


class WorkflowList extends Component {

  constructor(props) {
    super(props);
  }

  render() {
    let path = this.props.match.path;
    let headers = ["Name", "Description"];
    let datas = [];
    for (let key in wfs) {
      let wf = wfs[key];
      datas.push([
        <Link to={path + "/" + wf.name}>{wf.name}</Link>,
        wf.description
      ]);
    }

    return (
      <div className="animated fadeIn">
        <Card>
          <CardBody>
            <TableBuilder {...{ headers, datas }} />
          </CardBody>
        </Card>
      </div>
    )
  }
}


export default WorkflowList;