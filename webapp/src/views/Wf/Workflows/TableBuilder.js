import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Table } from 'reactstrap';


const propTypes = {
  headers: PropTypes.array,
  datas: PropTypes.array
};
const defaultProps = {
  headers: [],
  datas: []
};


class TableBuilder extends Component {
  constructor(props) {
    super(props);

    this.headers = props.headers;
    this.datas = props.datas;
  }

  render() {
    let numCol = this.datas.length > 0 ? this.datas[0].length : 0;
    return (
      <Table responsive>
        <thead>
          <tr>
            {
              this.headers.map((head, idx) => {
                return (
                  <th key={idx}>{head}</th>
                );
              })
            }
          </tr>
        </thead>

        <tbody>
          {
            this.datas.map((data, idx) => {
              return (
                <tr key={idx}>
                  {
                    data.map((col, idx) => {
                      return (
                        <td key={idx}>{col}</td>
                      )
                    })
                  }
                </tr>
              );
            })
          }
        </tbody>

      </Table>
    )
  }
}


TableBuilder.propTypes = propTypes;
TableBuilder.defaultProps = defaultProps;


export default TableBuilder;