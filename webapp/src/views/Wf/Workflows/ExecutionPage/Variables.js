import React, { Component } from 'react';
import ReactTable from 'react-table'
import 'react-table/react-table.css'


const defaultProps = {
  data: [],
  defaultPageSize: 5
};


class Variables extends Component {
  constructor(props) {
    super(props);
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

  render() {
    return (
      <ReactTable
        showPagination={false}
        columns={this.columns}
        data={this.props.data}
        defaultPageSize={this.props.defaultPageSize}
      />
    )
  }
}


Variables.defaultProps = defaultProps;


export default Variables;