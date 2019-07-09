import React, { Component } from 'react';
import { Badge, Card, CardBody, CardHeader, Row, Col } from 'reactstrap';
import Axios from 'axios';
import ReactTable from 'react-table'

import 'react-table/react-table.css'

import { StateLabel, WorkflowDiagram } from '../Common';


class ExecutionHistory extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      loading: true,
      pageSize: 5
    }
    this.wfName = this.props.name;

    this.columns = [{
      Header: "Start at",
      accessor: "start",
    }, {
      Header: "State",
      accessor: "state",
      Cell: (props) => {
        const state = StateLabel(props.value);
        if (state == undefined) {
          return (<Badge color="dark">unknown</Badge>)
        } else {
          return state.label;
        }
      }
    }];
  }

  componentDidMount = () => {
    this.setState({ loading: true })
    const url = "/tobot/executions?name=" + this.wfName;
    Axios.get(url).then((res) => {
      const executions = res.data;
      executions.forEach((element) => {
        if (element.start == undefined) {
          element.start = Date.now();
        }
      })
      this.setState({
        loading: false,
        data: executions,
        pageSize: executions.length > 0 ? executions.length : 5
      })
    });
  }

  render() {
    return (
      <ReactTable
        data={this.state.data}
        loading={this.state.loading}
        columns={this.columns}
        showPagination={false}
        pageSize={this.state.pageSize}
      />
    )
  }
}



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
    const wf = this.state.workflowInfo;
    const name = this.props.match.params.name;
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
                Execution History
            </CardHeader>
              <CardBody className="pb-0">
                {/* here comes a table for the latest execution info of this workflow */}
                <ExecutionHistory name={name} />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    );
  }
}


export default Workflow;
