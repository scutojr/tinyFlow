import React, { Component } from 'react';
import {
  Card, CardBody,
  CardHeader,
  Row, Col,
} from 'reactstrap';
import ReactJson from 'react-json-view';

import {Event} from '../../Common';
import Judgement from './Judgement';


class Trigger extends Component {
  render() {
    let { req, judgement } = this.props.trigger;
    judgement = {
      "judge_time": 1564057454811,
      "desc": "try to stop service, but threshold has been reached today",
      "options": [
        "yes", "no"
      ],
      "decision": "no",
      "comment": "xx",
    };

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
    const style = { 'margin-top': "10px", "margin-left": "10px" }
    return (
      <div style={{ backgroundColor: '#e4e5e6', "margin-top": "10px" }} >
        <Row >
          {
            req && Object.keys(req).length > 0 ? (
              <Col xs="12" sm="6" md="4">
                <Card style={style}>
                  <CardHeader>
                    Request
                  </CardHeader>
                  <CardBody>
                    <ReactJson src={req} name={false} />;
                  </CardBody>
                </Card>
              </Col>
            ) : ""
          }
          {
            event ? (
              <Col xs="12" sm="6" md="4">
                <Card style={style}>
                  <CardHeader>
                    Event
                  </CardHeader>
                  <CardBody>
                    <Event event={event} />
                  </CardBody>
                </Card>
              </Col>
            ) : ""
          }
          {
            judgement ? (
              <Col xs="12" sm="6" md="4">
                <Card style={{ "margin-right": "10px", "margin-top": "10px" }}>
                  <CardHeader>
                    Judgement
                  </CardHeader>
                  <CardBody>
                    <Judgement judgement={judgement} />
                  </CardBody>
                </Card>
              </Col>
            ) : ""
          }
        </Row>
      </div>
    )
  }
}


export default Trigger;