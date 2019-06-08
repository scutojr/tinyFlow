import React, { Component } from 'react';
import {
  Col,
  FormGroup,
  Input,
  Button,
  InputGroup,
  InputGroupAddon,
  Label,
  Row,
  Card,
  CardHeader,
  CardBody,
  Alert,
  Badge
} from 'reactstrap';

import TableBuilder from './Workflows/TableBuilder';


class EventFilter extends Component {

  _nameSelector() {
    return (
      <FormGroup>
        <Label htmlFor="ccmonth">Event Name</Label>
        <Input type="text" name="ccmonth" id="ccmonth" placeholder="ALL">
        </Input>
      </FormGroup>
    );
  }

  _tagsSlector() {
    return (
      <FormGroup>
        <Label htmlFor="ccyear">Tags</Label>
        <Input type="text" name="ccyear" id="ccyear" placeholder="ALL">
        </Input>
      </FormGroup>
    );
  }

  _endpointSelector() {
    return (
      <FormGroup>
        <Label htmlFor="cvv">Entity (Hostname/Ip)</Label>
        <Input type="text" id="cvv" placeholder="123" required />
      </FormGroup>
    );
  }

  _stateSelector() {
    return (
      <FormGroup>
        <Label htmlFor="cvv">Event State</Label>
        <Input type="select" id="cvv" placeholder="123" required >
          <option value="INFO"> INFO </option>
          <option value="WARN"> WARN </option>
          <option value="CRITICAL"> CRITICAL </option>
        </Input>
      </FormGroup>
    );
  }

  _timeSelector() {
    return (
      <FormGroup>
        <Label htmlFor="cvv">
          Time
        </Label>
        <InputGroup>
          <InputGroupAddon addonType="prepend">
            <Button type="button" color="dark">
              <i className="cui-calendar icons" />
            </Button>
          </InputGroupAddon>
          <Input type="text" id="input1-group2" name="input1-group2" placeholder="Now" />
        </InputGroup>
      </FormGroup>
    );
  }

  render() {
    return (
      <div>
        <Row>
          <Col xs="2">
            {this._nameSelector()}
          </Col>
          <Col xs="2">
            {this._tagsSlector()}
          </Col>
          <Col xs="2">
            {this._endpointSelector()}
          </Col>
          <Col xs="2">
            {this._stateSelector()}
          </Col>
          <Col xs="2">
            {this._timeSelector()}
          </Col>
        </Row>
        <Row>
          <Button> Submit </Button>
        </Row>
      </div>
    );
  }

}


class EventsTableWithPagination extends Component {
  constructor(props) {
    super(props);
    this.events = [{}, {}, {}, {}];
    this.headers = [
      "Event Name", "Entity (Hostname/IP)", "Tags",
      "State", "Params", "Message", "Source", "Happened At"
    ];
    this._generateData();
  }

  _generateData() {
    let event = {
      name: "disk error",
      entity: "10.20.30.40",
      tags: {
        dc: "guangzhou",
        business: "search"
      },
      start: 1234567890,
      state: "INFO",
      params: {
        p1: "p1",
        p2: "p2"
      },
      message: "describe what happens after this event",
      source: "nagios"
    }
    let events = this.events;
    events.forEach((element, idx) => {
      Object.assign(element, event);
    })
    events[1].state = "WARNING";
    events[2].state = "CRITICAL";
    events[3].state = "Some Wrong State";
    for (let i in events) {
      events[i] = this.serializeEvent(events[i]);
    }
  }

  serializeEvent(event) {
    function renderTags(tags) {
      let badges = [];
      for (let [key, value] of Object.entries(tags)) {
        badges.push(<Badge color="light">{`${key}=${value}`}</Badge>)
      }
      return (
        <span>{badges}</span>
      );
    }
    function renderState(state) {
      switch (state) {
        case "INFO":
          return <Badge color="primary">INFO</Badge>;
          break;
        case "WARNING":
          return <Badge color="warning">WARNING</Badge>;
          break;
        case "CRITICAL":
          return <Badge color="danger">CRITICAL</Badge>;
          break;
        default:
          return <Badge color="dark">UNKNOWN</Badge>;
      }
    }

    let { name, entity, tags, start, state, params, message, source } = event;
    return [
      name,
      entity,
      renderTags(tags),
      renderState(state),
      renderTags(params),
      message,
      source,
      start
    ];
  }

  render() {
    return (
      <TableBuilder headers={this.headers} datas={this.events} />
    )
  }
}


class Events extends Component {

  render() {
    return (
      <div className="animated fadeIn">
        <Card>
          <CardHeader>
            Event Filter
          </CardHeader>
          <CardBody>
            <EventFilter />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            Event Info
          </CardHeader>
          <CardBody>
            <EventsTableWithPagination />
          </CardBody>
        </Card>
      </div>
    )
  }
}

export default Events;
