import React, { Component } from 'react';
import ReactTable from 'react-table'
import 'react-table/react-table.css'


class Variables extends Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      data: []
    }
    this.columns = [
      {
        Header: "Name",
        accessor: "name",
      }, {
        Header: "Value",
        accessor: "value"
      }, {
        Header: "Scope",
        accessor: "scope"
      }, {
        Header: "Description",
        accessor: "desc"
      }
    ]
  }

  fetch = () => {

  }

  componentDidMount = () => {

  }

  renderTable = () => {

  }

  render() {
    return (
      <ReactTable
        showPagination={false}
        loading={this.state.loading}
        columns={this.columns}
        data={this.state.data}
      />
    )
  }
}


export default Variables;