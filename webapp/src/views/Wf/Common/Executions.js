import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import ReactTable from 'react-table'
import Axios from 'axios';

import { StateLabel } from './StateLabel';
import Utils from './Utils';

import 'react-table/react-table.css'


const defaultProps = {
  wfName: "",
  pageSize: 10
}


class Executions extends Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      data: [],
      pageSize: props.pageSize,
      page: 0,
      pages: 1,
      startBefore: Date.now()
    };
    this.delimiter = [];
    this.path = "/wf/executions";
    this.columns = [
      {
        Header: "Start",
        accessor: "start",
        Cell: ({ value }) => Utils.dateString(new Date(value))
      },
      {
        Header: "Workflow Name",
        accessor: "name",
        Cell: ({ value, row }) => {
          if (!value) {
            value = "NAME NOT DEFINED"
          }
          return <Link to={this.path + "/" + row._original._id["$oid"]}>{value}</Link>
        }
      },
      {
        Header: "State",
        accessor: "execution.state",
        Cell: (({ value }) => StateLabel(value).label)
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
      <ReactTable
        data={this.state.data}
        sortable={false}
        loading={this.state.loading}
        columns={this.columns}
        manual

        pages={this.state.pages}
        pageSize={this.state.pageSize}

        showPaginationTop={true}
        showPaginationBottom={true}

        onFetchData={(state, instance) => {
          let skip = state.page * state.pageSize;
          this.setState({ loading: true });

          const url = "/tobot/executions";
          const params = {
            skip: skip,
            startBefore: this.state.startBefore,
            limit: this.state.pageSize
          }
          if (this.props.wfName) {
            params.name = this.props.wfName;
          }
          Axios.get(url, { params }).then((res) => {
            this.setState({
              loading: false,
              data: res.data,
              pages: state.page >= state.pages ? state.page + 2 : state.pages + 1
            })
          });
        }}
      />
    )
  }
}


Executions.defaultProps = defaultProps;


export default Executions;
