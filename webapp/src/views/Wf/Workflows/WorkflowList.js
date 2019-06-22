import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import { Card, CardBody, CardHeader, Row, Col, CardText } from 'reactstrap';
import Axios from 'axios';
import ReactTable from 'react-table'
import 'react-table/react-table.css'


let wfsForTest = {
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
    this.state = {
      data: [],
      loading: true,
      pageSize: 10
    }
    this.columns = [{
      Header: "Workflow Name",
      accessor: "name",
      Cell: (props) => <Link to={this.props.match.path + "/" + props.value}>{props.value}</Link>
    }, {
      Header: "Description",
      accessor: "description",
    }];
  }

  componentDidMount = () => {
    const path = '/tobot/workflows';
    this.setState({
      loading: true
    })
    Axios.get(path).then((res) => {
      let rows = Object.values(res.data);
      this.setState({
        loading: false,
        data: rows,
        pageSize: rows.length
      })
    });
  }

  render() {
    return (
      <div className="animated fadeIn">
        <Card>
          <CardHeader>
            Registered Workflow
          </CardHeader>
          <CardBody>
            <ReactTable
              showPagination={false}
              data={this.state.data}
              pageSize={this.state.pageSize}
              loading={this.state.loading}
              columns={this.columns}
            />
          </CardBody>
        </Card>
      </div >
    )
  }
}


export default WorkflowList;
