import React, { Component } from 'react';
import {
  Badge, Card, CardBody,
  CardFooter, CardHeader,
  Col, Row, Collapse, Fade,
  Nav, NavItem, NavLink
} from 'reactstrap';

import WorkflowDiagram from './WorkflowDiagram';


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


class Execution extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="animated fadeIn">
        <Row>
          <Col xs="12" xl="8">
            <Row>
              <Col xs="12">
                <Card>
                  <CardHeader>
                    Workflow introduction for {this.props.match.wfId}
			            </CardHeader>
                  <CardBody className="pb-0">
                    describe this workflow. Should we show the code on the browser?
  		            </CardBody>
                </Card>
              </Col>

              <Col xs="12">
                <Card>
                  <CardHeader>
                    Event Listening
			            </CardHeader>
                  <CardBody className="pb-0">
                    all the event this workflow is interested in.
  		            </CardBody>
                </Card>
              </Col>

              <Col xs="12">
                <Card>
                  <CardHeader>
                    Workflow Diagram
   			         </CardHeader>
                  <CardBody className="pb-0" style={{ "backgroundColor": "#8f9ba6" }}>
                    <WorkflowDiagram workflow={workflowData} />
                  </CardBody>
                </Card>
              </Col>
            </Row>
          </Col>

          <Col xs="12" xl="4">
            <Card>
              <CardHeader>
                Variable Info for this Workflow Execution Instance
            </CardHeader>
              <CardBody className="pb-0">
                here comes a table for the variable of this execution
              </CardBody>
            </Card>
          </Col>
        </Row>

        <Row>
          <Col xs="12">
            <Card>
              <CardHeader>
                Workflow Log
              </CardHeader>
              <CardBody className="pb-0">

                <Nav tabs>
                  <NavItem>
                    <NavLink href="#" active>All</NavLink>
                  </NavItem>
                  <NavItem>
                    <NavLink href="#">task 1</NavLink>
                  </NavItem>
                  <NavItem>
                    <NavLink href="#">task 2</NavLink>
                  </NavItem>
                  <NavItem>
                    <NavLink disabled href="#">task 3</NavLink>
                  </NavItem>
                  <NavItem>
                    <NavLink disabled href="#">user action</NavLink>
                  </NavItem>
                </Nav>

              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    );
  }
}


export default Execution;