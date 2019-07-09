import React, { Component } from 'react';
import Axios from 'axios';
import 'react-table/react-table.css'

import { StateLabel } from '../../Common';

class Subscriptions extends Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.columns = [
      {
        Header: "Event Name",
        accessor: "name",
      }, {
        Header: "State",
        accessor: "state",
        Cell: (props) => StateLabel(props.value).label
      }
    ]
  }

  fetch = () => {
    const url = `/tobot/workflows/${this.props.name}/subscriptions`;
    Axios.get(url).then(
      (res) => {

      }
    )
  }

  renderTable = () => {
  }

  componentDidMount = () => {

  }

  render() {
    return (
      <div>
        {this.state.subs == undefined ? "loading..." : this.renderTable()}
      </div>
    )
  }
}


export default Subscriptions;