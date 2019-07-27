import React, { Component } from 'react';
import { Badge } from 'reactstrap';

import { StateLabel } from './StateLabel';


function renderKv(kvs) {
  let badges = [];
  for (let [key, value] of Object.entries(kvs)) {
    badges.push(<Badge color="light">{`${key}=${value}`}</Badge>)
  }
  return (
    <span>{badges}</span>
  );
}

/**
{
        "_id" : ObjectId("5d35ea26cb4e95f98bacc592"),
        "_cls" : "Event",
        "name" : "sleepy_test",
        "entity" : "ojr-test",
        "tags" : {
                "cluster" : "jy",
                "role" : "DataNode",
                "ip" : "10.11.12.13"
        },
        "start" : 0,
        "state" : "critical",
        "params" : {

        },
        "message" : "",
        "source" : ""
}
 */


const defaultProps = {
  event: {},
  id: ""
}

class Event extends Component {
  _fetch = () => {

  }

  componentDidMount = () => {
    if (this.props.id) {
      this._fetch();
    }
  }

  render() {
    const event = {
      "_id": "5d35ea26cb4e95f98bacc592",
      "_cls": "Event",
      "name": "sleepy_test",
      "entity": "ojr-test",
      "tags": {
        "cluster": "jy",
        "role": "DataNode",
        "ip": "10.11.12.13"
      },
      "start": 0,
      "state": "critical",
      "params": {},
      "message": "",
      "source": ""
    }
    return (
      <>
        <b>Name: </b> {event.name} <br />
        <b>Entity: </b> {event.entity} <br />
        <b>Tags: </b> {renderKv(event.tags)} <br />
        <b>Start: </b> {event.start} <br />
        <b>State: </b> {StateLabel(event.state).label} <br />
        <b>Params: </b> {renderKv(event.params)} <br />
        <b>Message: </b> {event.message} <br />
        <b>Source: </b> {event.source} <br />
      </>
    )
  }

}


Event.defaultProps = defaultProps;


export default Event;