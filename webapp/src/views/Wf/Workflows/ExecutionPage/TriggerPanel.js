import React, { Component } from 'react';
import {
  CardBody, Badge
} from 'reactstrap';


/**
 * class Event(me.Document):
    name = me.StringField(required=True)
    entity = me.StringField(required=True)
    tags = me.DictField()

    start = me.IntField(default=0)
    state = me.StringField(default=EventState.INFO)
    params = me.DictField()
    message = me.StringField(default='')

    source = me.StringField(default='')
 */

class TriggerPanel extends Component {
  constructor(props) {
    super(props);
  }

  _userReq = (trigger) => {
  }

  _event = (trigger) => {
  }

  _timeout = (trigger) => {

  }

  _userDecision = (trigger) => {

  }

  _error = (trigger) => {
    return <Badge color="dark">unknown trigger</Badge>
  }

  _renderTrigger = (trigger) => {

    /**
     * 1. event
     * 2. timeout
     * 3. user request
     * 4. user decision
     * 5. default: can not render this trigger
     */
    return this._error();
  }

  render() {
    const trigger = this.props.trigger
    return (
      <CardBody body outline color="danger" style={{ backgroundColor: '#F7F7F5', "margin-bottom": "10px" }}>
        {this._renderTrigger(trigger)}
      </CardBody>
    )
  }
}


export default TriggerPanel;