import React, { Component } from 'react';
import {
  Card, CardBody,
  CardHeader,
  Col, Row, Form,
  FormGroup, Label, Input, CustomInput
} from 'reactstrap';

import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

import RichTextEditor from 'react-rte';

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


class LogPannel extends Component {
  constructor(props) {
    super(props);
    this.state = {
      phases: {
        all: true
      }
    }
    this.phases = undefined;
  }

  getPhases = (logs) => {
    if (this.phases != undefined) {
      return this.phases;
    }
    let phases = new Set();
    for (let [time, phase, msg] of logs) {
      phases.add(phase);
    }
    this.phases = phases;
    return phases;
  }

  buildLogContent = () => {
    const logs = this.props.logs;
    const lines = [];
    const phases = this.state.phases;
    const all = phases.all;
    for (let [time, phase, msg] of logs) {
      if (all || phases[phase]) {
        lines.push(`${time} ${phase} ${msg}`)
      }
    }
    console.log(lines);
    return lines.join("\n");

  }

  render() {
    const logs = this.props.logs;
    let phases = new Array(...this.getPhases(logs));
    for (let p of phases) {
      if (this.state.phases[p] == undefined) {
        this.state.phases[p] = false;
      }
    }
    phases.splice(0, 0, "all");
    const content = this.buildLogContent();

    return (
      <>
        <FormGroup>
          <div>
            {
              phases.map((phase, i) => {
                return (
                  <CustomInput
                    id={phase} key={phase} inline
                    type="checkbox" label={phase}
                    checked={this.state.phases[phase]}
                    onChange={(e) => {
                      if (phase == "all") {
                        for (let key in this.state.phases) {
                          this.state.phases[key] = false;
                        }
                        this.state.phases["all"] = true;
                      } else {
                        this.state.phases[phase] = e.target.checked;
                        this.state.phases["all"] = false;
                      }
                      this.setState({});
                    }}
                  />
                )
              })
            }
          </div>
        </FormGroup>
        <div
          style={{
            height: "500px",
            overflow: "auto",
            "margin-top": "20px"
          }}
        >
          <Card>
            <textarea
              style={{
                width: "100%",
                height: "470px"
              }}
              value={content}
              spellCheck={false}
            />
          </Card>
        </div>
      </>
    )
  }
}


class Execution extends Component {

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
                  <CardBody className="pb-0" style={{ "backgroundColor": "#8f9ba6", height: "400px" }}>
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

                <LogPannel logs={[
                  [123, "p1", "fake data"],
                  [123, "p1", "fake data"],
                  [123, "p2", "fake data"],
                  [123, "p3", "fake data"],
                  [123, "p2", "fake data"],
                  [123, "p1", "fake data"]
                ]} />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    );
  }
}


export default Execution;
