import React, { Component } from 'react';
import { Card, CardBody, CardHeader } from 'reactstrap';

import { Executions } from '../Common';


class ExecutionsPage extends Component {
  render() {
    return (
      <Card>
        <CardHeader> Execution History </CardHeader>
        <CardBody>
          <Executions pageSize={20}/>
        </CardBody>
      </Card>
    )
  }
}


export default ExecutionsPage;
