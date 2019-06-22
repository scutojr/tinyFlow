
import React, { Component } from 'react';
import { Card, CardBody, CardHeader, Row, Col } from 'reactstrap';
import Axios from 'axios';

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


class Workflow extends Component {

  constructor(props) {
    super(props);
    this.state = {
      workflowInfo: undefined
    };
  }

  fetchWorkflowInfo = () => {
    const name = this.props.match.params.name;
    const endpoint = "/tobot/workflows/" + name;
    Axios.get(endpoint).then((res) => {
      const wf = res.data;
      if (wf != "null") {
        this.setState({
          workflowInfo: wf
        })
      }
    })
  }

  componentDidMount = () => {
    this.fetchWorkflowInfo();
  }

  render() {
    console.log(this.props);
    const wf = this.state.workflowInfo;
    return (
      <div className="animated fadeIn">
        <Row>

          <Col xs="12" xl="8">
            <Row>
              <Col xs="12">
                <Card>
                  <CardHeader>
                    Workflow introduction
               </CardHeader>
                  <CardBody className="pb-0">
                    {wf == undefined ? '' : wf.description}
                  </CardBody>
                </Card>
              </Col>

              <Col xs="12">
                <Card>
                  <CardHeader>
                    Event Listening
               </CardHeader>
                  <CardBody className="pb-0">
                    here is the event info
                </CardBody>
                </Card>
              </Col>

              <Col xs="12">
                <Card>
                  <CardHeader>
                    Workflow Diagram
               </CardHeader>
                  <CardBody className="pb-0" style={{ "backgroundColor": "#8f9ba6" }}>
                    <WorkflowDiagram workflow={wf} />
                  </CardBody>
                </Card>
              </Col>
            </Row>
          </Col>

          <Col xs="12" xl="4">
            <Card>
              <CardHeader>
                Brief View of Execution History
            </CardHeader>
              <CardBody className="pb-0">
                here comes a table for the latest execution info of this workflow
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    );
  }
}


export default Workflow;
