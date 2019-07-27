import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import {
  Card, CardBody,
  CardHeader, Col,
  FormGroup,
  Nav, NavItem, NavLink, TabContent,
  Alert
} from 'reactstrap';
import Axios from 'axios';

import routes from '../../../../routes'

import {
  StateLabel,
  WorkflowDiagram,
} from '../../Common';
import Variables from './Variables';
import LogPanel from './LogPanel';
import Judgement from './Judgement';
import Trigger from './Trigger';


/**

{
    "topology": {
        "description": "",
        "entrance": "task start",
        "graph": {
            "task end": {},
            "task start": {}
        },
        "name": "define_param_wf"
    },
    "variables": [],
    "_id": {
        "$oid": "5d37763e5b62f32ca28ede0f"
    },
    "execution": {
        "exception": "Traceback (most recent call last):\n  File \"/tmp/ojr/wf/workflow/execution.py\", line 75, in execute\n    func(*self.parse_task_params(func, tri_chain))\n  File \"/var/run/tobot/4/define_param_wf.py\", line 17, in start\n    raise Exception('wrong input parameter')\nException: wrong input parameter\n",
        "exec_history": [
            "task start"
        ],
        "next_task": "",
        "props": {},
        "state": "failed",
        "wf_name": "define_param_wf"
    },
    "logger": {
        "content": []
    },
    "name": "define_param_wf",
    "start": 1563915838406,
    "tri_chain": {
        "_event": {
            "$oid": "5d37763e5b62f32ca28ede0e"
        },
        "_req": {
            "change": [
                "new_value"
            ]
        },
        "chain": [
            {
                "_cls": "TriggerFrame",
                "event": {
                    "$oid": "5d37763e5b62f32ca28ede0e"
                },
                "req": {
                    "change": "new_value"
                }
            }
        ]
    },
    "version": 4
}
 */


class ExecutionPage extends Component {

  constructor(props) {
    super(props);
    this.state = {
      activeTab: "wf",
      workflow: undefined
    }

    this.collumnsVar = [
      {
        Header: "Name",
        accessor: "name",
      },
      {
        Header: "Scope",
        accessor: "scope",
      },
      {
        Header: "Description",
        accessor: "desc",
      }
    ]
  }

  wfId = () => {
    return this.props.match.params.wfId;
  }

  componentDidMount = () => {
    const endpoint = "/tobot/web/executions/" + this.wfId();
    Axios.get(endpoint).then((res) => {
      this.setState({ workflow: res.data })
    })
  }

  toggle = (tab) => {
    this.setState({ activeTab: tab })
  }

  tabContent = () => {
    if (!this.state.workflow) {
      return this._error("loading workflow execution info", false);
    }
    const tab = this.state.activeTab;
    switch (tab) {
      case "wf":
        return this._workflow();
      case "var":
        return this._vars();
      case "diagram":
        return this._diagram();
      default:
        return this._error("unexpected error!");
    }
  }

  _error = (msg, isDanger = true) => {
    const color = isDanger ? "danger" : "primary";
    return (
      <CardBody>
        <Alert color={color}>
          {msg}
        </Alert>
      </CardBody>
    )
  }

  _workflow = () => {
    const wf = this.state.workflow;
    const wfId = wf._id['$oid']
    const name = wf.name;
    const state = wf.execution.state;
    const exception = wf.execution.exception;
    const chain = wf.tri_chain.chain;

    return (
      <CardBody >
        <FormGroup row>
          <Col xs="1" md="1">
            <b>Name</b>
          </Col>
          <Col xs="11" md="11">
            <Link to={routes.workflow.urlBuilder(name)} > {name} </Link>
          </Col>
        </FormGroup>

        <FormGroup row>
          <Col xs="1" md="1">
            <b>State</b>
          </Col>
          <Col xs="11" md="11">
            {StateLabel(state).label}
          </Col>
        </FormGroup>

        {
          exception ? (
            <FormGroup row>
              <Col xs="1" md="1">
                <b>Exception</b>
              </Col>
              <Col xs="11" md="11">
                <textarea
                  value={exception}
                  spellCheck={false}
                  style={{ "width": "70%", "height": "200px" }}
                />
              </Col>
            </FormGroup>
          ) : ""
        }

        {
          state == "waiting" ? (
            <FormGroup row>
              <Col xs="1" md="1">
                <b>Judgement</b>
              </Col>
              <Col xs="11" md="11">
                <Judgement wfId={wfId} />
              </Col>
            </FormGroup>
          ) : ""
        }

        <hr />

        <h6><b>Triggers</b></h6>
        {
          chain.length > 0 ? (
            chain.map((trigger, idx) => <Trigger trigger={trigger} />)
          ) : (
              <Alert color="danger">
                No trigger related to this workflow found!
            </Alert>
            )
        }
      </CardBody>
    )
  }

  _vars = () => {
    const data = this.state.workflow.variables;
    return (
      <Variables data={data} />
    )
  }

  _diagram = () => {
    const topology = this.state.workflow.topology;
    return (
      <WorkflowDiagram workflow={topology} />
    )
  }

  render() {
    const style = {
      width: "100%"
    };
    return (
      <>
        <Nav tabs>
          <NavItem>
            <NavLink
              active={this.state.activeTab == "wf"}
              onClick={() => { this.toggle("wf"); }}
            >
              Workflow
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink
              active={this.state.activeTab == "var"}
              onClick={() => { this.toggle("var"); }}
            >
              Variables
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink
              active={this.state.activeTab == "diagram"}
              onClick={() => { this.toggle("diagram"); }}
            >
              Diagram
            </NavLink>
          </NavItem>
        </Nav>
        <TabContent activeTab={this.state.activeTab[0]} style={style}>
          {this.tabContent()}
        </TabContent>

        <Card style={{ "margin-top": "20px" }}>
          <CardHeader>Log</CardHeader>
          <CardBody>
            <LogPanel logs={[
              [123, "p1", "fake data"],
              [123, "p1", "fake data"],
              [123, "p2", "fake data"],
              [123, "p3", "fake data"],
              [123, "p2", "fake data"],
              [123, "p1", "fake data"]
            ]} />
          </CardBody>
        </Card>
      </>
    )
  }

}


export default ExecutionPage;