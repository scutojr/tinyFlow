import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import {Card, CardBody, CardHeader } from 'reactstrap';
import ReactTable from 'react-table'
import Axios from 'axios';

import StateLable from './StateLabel';

import 'react-table/react-table.css'


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
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      data: [],
      pageSize: 20,
      page: 0,
      pages: 1,
      startBefore: Date.now()
    };
    this.delimiter = [];
    this.path = this.props.match.path;
    this.columns = [
      {
        Header: "Start",
        accessor: "start",
        Cell: ({value}) => {
          let d = new Date(value);
          return `${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}/${d.getMonth() + 1}.${d.getDate()}/${d.getFullYear()}`;
        }
      },
      {
        Header: "Workflow Name",
        accessor: "wf",
        Cell: ({value, row}) => {
          if (!value) {
            value = "NAME NOT DEFINED"
          }
          return <Link to={this.path + "/" + row._original._id["$oid"]}>{value}</Link>
        }
      },
      {
        Header: "State",
        accessor: "state",
        Cell: (({value}) => StateLable(value).label)
      },
      {
        Header: "Trigger By",
      },
      {
        Header: "User Decision",
      }
    ];
    this.i = 0;
  }

  fetchExecutionHistory = (start, limit) => {
    Axios.get("").then(() => {
      this.setState({
        loading: false
      })
    });
  }

  componentDidMount = () => {
    // this.fetchExecutionHistory(Date.now(), 100);
  }

  generate = () => {
    let rows = [];
    do {
      this.i += 1;
      rows.push({
        name: `name-${this.i}`
      })
    } while (this.i % 10 != 0)
    return rows
  }

  render() {
    return (
      <Card>
        <CardHeader> Execution History </CardHeader>
        <CardBody>
          <ReactTable
            data={this.state.data}
            sortable={false}
            loading={this.state.loading}
            columns={this.columns}
            // columns={columns}
            manual

            pages={this.state.pages}
            pageSize={this.state.pageSize}

            showPaginationTop={true}
            showPaginationBottom={true}

            onFetchData={(state, instance) => {
              console.log(state.page)
              let skip = state.page * state.pageSize;
              this.setState({ loading: true });

              const url = "/tobot/workflows/execution";
              const params = {
                skip: skip,
                startBefore: this.state.startBefore,
                limit: this.state.pageSize
              }
              Axios.get(url, { params }).then((res) => {
                console.log("res: ", res);
                this.setState({
                  loading: false,
                  data: res.data,
                  pages: state.page >= state.pages ? state.page + 2 : state.pages + 1
                })
              });
            }}
          />
        </CardBody>
      </Card>
    )
  }
}


export default Executions;
