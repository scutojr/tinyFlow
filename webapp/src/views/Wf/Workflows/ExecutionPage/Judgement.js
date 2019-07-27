import React, { Component } from 'react';
import {
  Row, Col,
  Form, FormGroup,
  Alert, Input, Label, CustomInput, Button
} from 'reactstrap';
import Axios from 'axios';
import { withRouter } from 'react-router-dom'
import { Exception } from 'handlebars';

import { Utils } from '../../Common';


const defaultProps = {
  wfId: "",
  judgement: undefined
};


class IdGenerator {
  constructor() {
    this.id = 0;
  }

  next() {
    this.id += 1;
    return this.id.toString();
  }
}


const generator = new IdGenerator();
const BEFORE_SUBMIT = 1;
const SUBMIT_FAILED = 3;


class Judgement extends Component {
  constructor(props) {
    super(props);

    let isRead;
    if (this.props.wfId != "") isRead = false;
    else if (this.props.judgement != undefined) isRead = true;
    else throw new Exception("at least one of wfId and judgement is provided");

    this.state = {
      comment: "",
      decision: undefined,
      procedure: BEFORE_SUBMIT,
      failedReason: undefined,
      judgement: undefined,
      isError: false,
      isRead: isRead
    }
  }

  componentDidMount = () => {
    const wfId = this.props.wfId;
    if (wfId) {
      const endpoint = `/tobot/userDecisions/${wfId}`;
      Axios.get(endpoint).then(
        (res) => {
          const j = res.data.judgement[0];
          this.setState({ judgement: j });
        },
        (res) => {
          this.setState({ isError: true });
        }
      )
    }
  }

  submit = (onSuccess) => {
    if (!this.state.decision) {
      return;
    }
    const body = {
      comment: this.state.comment,
      judge: this.state.decision
    }
    Axios.post(`/tobot/userDecision/${this.props.wfId}`, body).then(
      (res) => {
        console.log(res);
        onSuccess();
      },
      (res) => {
        console.log(res);
        this.setState({ procedure: SUBMIT_FAILED })
      }
    )
  }

  _btn = () => {
    return withRouter(route => (
      <FormGroup className="form-actions">
        <Button
          className="float-right"
          type="submit"
          size="sm"
          color="success"
          onClick={(e) => {
            this.submit(() => route.history.go(0));
          }}
        >
          Submit
        </Button>
      </FormGroup>
    ))
  }

  _alert = () => {
    return (
      <Alert color="danger">
        failed to submit.
      </Alert>
    )
  }

  render = () => {
    // const readMode = this.props.readMode;
    const j = this.props.judgement;

    const Btn = this._btn();
    const Error = this._alert;
    const { isRead, isError, judgement } = this.state;

    if (!isRead) {
      if (isError) {
        return <p>Error</p>
      } else if (judgement == undefined) {
        return <p>Loading......</p>
      }
    }

    return (
      <>
        {
          this.state.isRead ? (
            <Row>
              <Col md="3">
                <Label htmlFor="textarea-input">Time</Label>
              </Col>
              <Col xs="12" md="9">
                {Utils.dateString(new Date(j.judge_time))}
              </Col>
            </Row>
          ) : ""
        }

        <FormGroup row>
          <Col md="3">
            <Label htmlFor="textarea-input">Description</Label>
          </Col>
          <Col xs="12" md="9">
            <Input type="textarea" disabled name="textarea-input" id="textarea-input" rows="2" value={j.desc} />
          </Col>
        </FormGroup>

        <Form>
          <FormGroup row>
            <Col md="3">
              <Label>Options</Label>
            </Col>
            <Col md="9">
              {
                j.options.map((option, idx) => {
                  const c = (this.state.isRead ?
                    option == j.decision :
                    option == this.state.decision
                  )
                  const id = option + generator.next();
                  console.log(c, option, id);
                  return (
                    <CustomInput
                      type="radio" id={id} key={id}
                      name="customRadio" disabled={this.state.isRead}
                      checked={c} label={option}
                      onChange={(e) => {
                        this.setState({ decision: option })
                      }}
                    />
                  )
                })
              }
            </Col>
          </FormGroup>
        </Form>

        <FormGroup row>
          <Col md="3">
            <Label htmlFor="textarea-input">Comment</Label>
          </Col>
          <Col xs="12" md="9">
            <Input type="textarea" disabled={this.state.isRead}
              name="textarea-input" id="textarea-input"
              rows="2" value={
                this.state.isRead ?
                  j.comment :
                  this.state.comment
              }
              onChange={(e) => this.setState({ comment: e.value })}
            />
          </Col>
        </FormGroup>
        {
          this.state.isRead ? "" : (
            this.state.procedure == BEFORE_SUBMIT ? <Btn /> : <Error />
          )
        }
      </>
    )
  }
}

Judgement.defaultProps = defaultProps;


export default Judgement;