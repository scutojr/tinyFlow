import React, { Component } from 'react';


/**
 * 
 * 
 class EventState(object):
     INFO = 'info'
     WARN = 'warning'
     CRITICAL = 'critical'

     alls = (INFO, WARN, CRITICAL)


 class Event(me.Document):
     name = me.StringField(required=True)
     entity = me.StringField(required=True)
     tags = me.DictField()

     start = me.IntField(default=0)
     state = me.StringField(default=EventState.INFO)
     params = me.DictField()
     message = me.StringField(default='')

     source = me.StringField(default='')

     meta = {
         'allow_inheritance': True
     }
 */


class Events extends Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="animated fadeIn">
        <p>
          this is a events page for workflow
        </p>
      </div>
    )
  }
}

export default Events;