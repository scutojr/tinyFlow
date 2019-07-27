import React, { Component } from 'react';
import {
  Badge, Card, CardBody, CardHeader,
  Row, Col, Nav, NavItem, NavLink,
  TabContent, FormGroup, Alert
} from 'reactstrap';
import Axios from 'axios';
import ReactTable from 'react-table'

import 'react-table/react-table.css'

import { StateLabel, EventStateLabel, WorkflowDiagram, Executions } from '../Common';


/**
  {
    "subscriptions": [
        {
            "name": "server_down",
            "state": "critical"
        }
    ],
    "topology": {
        "description": "",
        "entrance": "handle_server_down",
        "graph": {
            "check_server_health": {},
            "handle_server_down": {},
            "notify_admin": {},
            "reboot_failed": {},
            "reboot_succeed": {},
            "repair_the_server": {},
            "start_all_service": {}
        },
        "name": "waited_workflow"
    },
    "variables": [{name, desc, scope}]
  }
 */
class Workflow extends Component {

  constructor(props) {
    super(props);
    this.state = {
      workflowInfo: undefined,
      activeTab: "wf",
    };

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

  _fetchWorkflowInfo = () => {
    const name = this.props.match.params.name;
    const endpoint = "/tobot/web/workflows/" + name;
    Axios.get(endpoint).then((res) => {
      const wfInfo = res.data;
      if (wfInfo != "null") {
        this.setState({
          workflowInfo: wfInfo
        })
      }
    })
  }

  _fetchExecutionHistory = () => {
    const name = this.props.match.params.name;
    const endpoint = "/tobot/web/workflows/" + name;
    Axios.get(endpoint).then((res) => {
      const wfInfo = res.data;
      if (wfInfo != "null") {
        this.setState({
          workflowInfo: wfInfo
        })
      }
    })
  }

  componentDidMount = () => {
    this._fetchWorkflowInfo();
  }

  _workflow = () => {
    let { name, description } = this.state.workflowInfo.topology;
    return (
      <CardBody >
        <FormGroup row>
          <Col xs="1" md="1">
            <b>Name</b>
          </Col>
          <Col xs="11" md="11">
            {name}
          </Col>
        </FormGroup>

        <FormGroup row>
          <Col xs="1" md="1">
            <b>Description</b>
          </Col>
          <Col xs="11" md="11">
            <textarea
              style={{
                width: "50%",
                height: "100px"
              }}
              value={description}
              spellCheck={false}
            />
          </Col>
        </FormGroup>

        <hr />

        <h5>Event Subscription</h5>

        {
          this.state.workflowInfo.subscriptions.map((sub) => {
            return (
              <CardBody body outline color="danger"
                style={{ backgroundColor: '#F7F7F5', "margin-bottom": "10px", width: '25%' }}
              >
                <b>Name</b>: {sub.name}
                <br />
                <b>State</b>: {EventStateLabel(sub.state)}
              </CardBody>
            )
          })
        }
      </CardBody>
    )
  }

  _variables = () => {
    return (
      <ReactTable
        data={this.state.workflowInfo.variables}
        columns={this.collumnsVar}
        showPagination={false}
        defaultPageSize={5}
      />
    );
  }

  _diagram = () => {
    return (
      <Card>
        <CardBody className="pb-0" style={{ "backgroundColor": "#8f9ba6" }}>
          <WorkflowDiagram workflow={this.state.workflowInfo.topology} />
        </CardBody>
      </Card>
    )
  }

  _error = (msg) => {
    return (
      <CardBody>
        <Alert color="danger">
          Error: {msg}
        </Alert>
      </CardBody>
    )
  }

  toggle = (tabName) => {
    this.setState({ activeTab: tabName });
  }

  tabContent = () => {
    if (!this.state.workflowInfo) {
      return this._error("no workflow found!");
    }
    const tab = this.state.activeTab;
    if (tab == "wf") {
      return this._workflow();
    } else if (tab == "var") {
      return this._variables();
    } else if (tab == "diagram") {
      return this._diagram();
    } else {
      return this._error("Internal Error");
    }
  }

  render() {
    const wf = this.state.workflowInfo;
    const name = this.props.match.params.name;
    return (
      <>
        <Row>
          <Col>
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
            <TabContent activeTab={this.state.activeTab[0]}>
              {this.tabContent()}
            </TabContent>
          </Col>
        </Row>

        <Row style={{ "margin-top": "20px" }}>
          <Col>
            <Card>
              <CardHeader>
                Execution History
            </CardHeader>
              <CardBody className="pb-0">
                <Executions wfName={name} />
              </CardBody>
            </Card>
          </Col>
        </Row>

      </>
    );
  }
}


export default Workflow;
