import React, { Component } from 'react';
import { CardBody, Col, FormGroup, Alert } from 'reactstrap';

import { StateLabel } from '../../Common';


class Workflow extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <CardBody >
        <FormGroup row>
          <Col xs="1" md="1">
            <b>Name</b>
          </Col>
          <Col xs="11" md="11">
            <a href="">hehehe</a>
          </Col>
        </FormGroup>

        <FormGroup row>
          <Col xs="1" md="1">
            <b>State</b>
          </Col>
          <Col xs="11" md="11">
            {StateLabel("running").label}
          </Col>
        </FormGroup>

        <hr />

        <h6><b>Triggers</b></h6>
        {
          this.state.events.length > 0 ? (
            this.state.events.map((event, idx) =>
              <TriggerPannel event={event} id={idx} />
            )
          ) : (
              <Alert color="danger">
                No trigger related to this workflow found!
            </Alert>
            )
        }
      </CardBody>
    );
  }
}


export default Workflow;