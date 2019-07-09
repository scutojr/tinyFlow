import React, { Component } from 'react';
import {
  Card, CardBody,
  CardHeader,
  Col,
  FormGroup,
  Nav, NavItem, NavLink, TabContent,
  Alert,
} from 'reactstrap';
import Axios from 'axios';

import { StateLabel, WorkflowDiagram } from '../../Common';
import TriggerPanel from './TriggerPanel';
import Variables from './Variables';
import LogPanel from './LogPanel';


class Execution extends Component {
  constructor(props) {
    super(props);
    this.state = {
      wf: undefined,
      exec: undefined,
      vars: undefined
    }
  }

  wfId = () => {
    return this.props.match.params.wfId;
  }

  fetchWfDefinition = () => {
    const url = `/tobot/executions/${this.wfId()}/workflow`;
    Axios.get(url).then(
      (res) => {
        console.log(res.data);
      }
    );
  }

  fetchWfExecData = () => {
    const url = `/tobot/executions/${this.wfId()}`;
    Axios.get(url).then(
      (res) => {
        console.log(res.data);
      }
    );
  }

  fetchWfVar = () => {
    const url = `/tobot/variables/?wf_id=${this.wfId()}`;
    Axios.get(url).then(
      (res) => {
        console.log(res.data);
      }
    );
  }

  componentDidMount = () => {
    this.fetchWfDefinition();
    this.fetchWfExecData();
    this.fetchWfVar();
  }

}


class ExecutionPage extends Component {

  constructor(props) {
    super(props);
    this.state = {
      activeTab: "wf",
      events: [1, 2, 3, 4]
    }
  }

  fetchEvents = () => {

  }

  tabContent = () => {
    return {
      wf: this._contentWorkflow(),
      var: this._contentVariables(),
      diagram: this._contentDiagram()
    }[this.state.activeTab]
  }

  _contentWorkflow = () => {

    return (
      <CardBody >
        <FormGroup row>
          <Col xs="1" md="1">
            <b>Name</b>
          </Col>
          <Col xs="11" md="11">
            <a href="">hehehe</a>
          </Col>
        </FormGroup>

        <FormGroup row>
          <Col xs="1" md="1">
            <b>State</b>
          </Col>
          <Col xs="11" md="11">
            {StateLabel("running").label}
          </Col>
        </FormGroup>

        <hr />

        <h6><b>Triggers</b></h6>
        {
          this.state.events.length > 0 ? (
            this.state.events.map((event, idx) =>
              <TriggerPanel event={event} id={idx} />
            )
          ) : (
              <Alert color="danger">
                No trigger related to this workflow found!
            </Alert>
            )
        }
      </CardBody>
    )
  }

  _contentVariables = () => {
    return (
      <Variables />
    )
  }

  _contentDiagram = () => {
    const workflowData = {
      "description": "this is a description of a workflow",
      "entrance": "task start",
      "graph": {
        "sleepy task": { "succeed": "task end" },
        "task end": {},
        "task start": {
          "fail": "task end",
          "succeed": "sleepy task"
        }
      },
      "name": "sleepy_wf"
    };
    return (
      <WorkflowDiagram workflow={workflowData} />
    )
  }

  toggle = (tab) => {
    this.setState({ activeTab: tab })
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