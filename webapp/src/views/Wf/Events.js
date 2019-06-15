import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { withRouter } from 'react-router-dom'
import Axios from 'axios';
import Autocomplete from 'react-autocomplete'
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
  Badge
} from 'reactstrap';

import ReactTable from 'react-table'
import 'react-table/react-table.css'


function parseUrlParams(props) {
  let search = new URLSearchParams(props.location.search);
  let params = {};
  let { name, tags, entity, state, startBefore, startAfter } = search;
  if (name) params.name = name;
  if (tags) params.tags = tags;
  if (entity) params.entity = entity;
  if (state) params.state = state;
  if (startBefore) params.startBefore = startBefore;
  if (startAfter) params.startAfter = startAfter;
  return params;
}


class EventFilter extends Component {
  constructor(props) {
    super(props);
    this.inputName = React.createRef();
    this.inputTags = React.createRef();
    this.inputEntity = React.createRef();
    this.eventState = "INFO";
    this.startBefore = 0;
    this.startAfter = 0;
  }

  _nameSelector() {
    const onChange = (value, items, setItems) => {
      const newItems = [
        "name-1",
        "name-2",
        "name-3",
        "name-4",
        "name-5"
      ]
      setItems(newItems);
    }
    return (
      <FormGroup>
        <Label htmlFor="ccmonth">Event Name</Label>
        <AutoCompleteInput
          ref={this.inputName}
          onChange={onChange}
          inputProps={{ placeholder: "ALL" }}
        />
      </FormGroup>
    );
  }

  _tagsSlector() {
    const onChange = (value, items, setItems) => {
      const newItems = [
        "k1=v1",
        "k2=v2",
        "k3=v3",
        "k4=v4",
        "k5=v5"
      ]
      setItems(newItems);
    }
    return (
      <FormGroup>
        <Label htmlFor="ccyear">Tags</Label>
        <AutoCompleteInput
          ref={this.inputTags}
          onChange={onChange}
          inputProps={{ placeholder: "ALL" }}
        />
      </FormGroup>
    );
  }

  _endpointSelector() {
    const onChange = (value, items, setItems) => {
      const newItems = [
        "host1",
        "host2",
        "host3",
        "host4",
        "host5"
      ]
      setItems(newItems);
    }
    return (
      <FormGroup>
        <Label htmlFor="cvv">Entity (Hostname/Ip)</Label>
        <AutoCompleteInput
          ref={this.inputEntity}
          onChange={onChange}
          inputProps={{ placeholder: "ALL" }}
        />
      </FormGroup>
    );
  }

  _stateSelector() {
    return (
      <FormGroup>
        <Label htmlFor="cvv">Event State</Label>
        <Input type="select" id="cvv" required >
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
    const Btn = withRouter(({ history }) => (
      <Button
        type='button'
        onClick={() => {
          let params = {};
          const name = this.inputName.current.getInputValue();
          const tags = this.inputTags.current.getInputValue();
          const entity = this.inputEntity.current.getInputValue();
          let path = history.location.pathname + "?";
          if (name) params.name = name;
          if (tags) params.tags = tags;
          if (entity) params.entity = entity;
          const search = new URLSearchParams(params).toString();
          if (search) {
            history.replace(`${path}${search}`);
          }
        }}
      >
        Submit
      </Button>
    ))
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
          <Btn/>
        </Row>
      </div>
    );
  }

}


class ReactTableDemo extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      page: 0,
      pages: 1,
      loading: true,
      pageSize: 10,
    };
    this.limit = 100;
    this.columns = [{
      Header: "Event Name",
      accessor: "name",
    }, {
      Header: "Entity (Hostname/IP)",
      accessor: "entity",
    }, {
      Header: "Tags",
      accessor: "tags",
      Cell: this.renderKv
    }, {
      Header: "State",
      accessor: "state",
      Cell: this.renderState
    }, {
      Header: "Params",
      accessor: "params",
      Cell: this.renderKv
    }, {
      Header: "Message",
      accessor: "message",
    }, {
      Header: "Source",
      accessor: "source",
    }, {
      Header: "Happened At",
      accessor: "start",
    }
    ];
    this.generateData();
  }

  buildQueryURL() {
    let params = parseUrlParams(this.props);
    this.queryURL = "";
  }

  generateData(limit) {
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
    };
    let data = [];
    let offset = 0;
    if (this.state.data.length > 0) {
      offset = this.state.data.length;
    }
    for (let i = 0; i < limit; i++) {
      let e = {};
      Object.assign(e, event);
      e.start = i + offset;
      data.push(e);
    }
    return data;
  }

  renderKv(props) {
    let badges = [];
    let kvs = props.value;
    for (let [key, value] of Object.entries(kvs)) {
      badges.push(<Badge color="light">{`${key}=${value}`}</Badge>)
    }
    return (
      <span>{badges}</span>
    );
  }

  renderState(props) {
    let state = props.value;
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

  fetchEventData = (startBefore, limit) => {
    this.setState({
      loading: true
    })
    let callback = ((res) => {
      let { data, pageSize } = this.state;
      let newData = [];
      newData.push(...data, ...this.generateData(this.limit));
      this.setState({
        loading: false,
        pages: Math.ceil(newData.length * 1.0 / pageSize),
        data: newData
      })
    })
    Axios.get(this.queryURL).then(callback, callback);
  }

  componentDidMount = (() => {
    let timestamp = Math.floor(Date.now());
    this.fetchEventData(timestamp, this.limit);
  });

  onPageChannge = ((pageIndex, pageSize) => {
    if (pageSize == undefined) {
      pageSize = this.state.pageSize;
    }
    let data = this.state.data;
    let pos = pageIndex * pageSize
    if (pos >= data.length) {
      let lastEvent = data[data.length - 1];
      this.fetchEventData(lastEvent.start - 1, this.limit);
    }
    this.setState({
      page: pageIndex,
      pageSize: pageSize,
      pages: Math.ceil(data.length * 1.0 / pageSize),
    })
  })

  render() {
    let data = new Array(...this.state.data);
    return (
      <ReactTable
        sortable={false}
        defaultPageSize={this.state.pageSize}
        data={this.state.data}
        pages={this.state.pages + 1}
        loading={this.state.loading}
        columns={this.columns}
        page={this.state.page}
        onPageChange={(pageIndex) => { this.onPageChannge(pageIndex) }}
        onPageSizeChange={(pageSize, pageIndex) => { this.onPageChannge(pageIndex, pageSize) }}
      />
    )
  }
}


const propTypes = {
  items: PropTypes.array,
  getItemValue: PropTypes.func, // (item) => (item.xx)
  onChnage: PropTypes.func, // (value, items, setItems) => {}
  shouldItemRender: PropTypes.func, // (item, value) => {return boolean}
  inputProps: PropTypes.object
};

const defaultProps = {
  inputProps: {}
};

class AutoCompleteInput extends Component {
  constructor(props) {
    super(props);
    this.state = {
      value: "",
      items: props.items ? props.items : []
    }
  }

  getInputValue = () => {
    return this.state.value;
  }

  getItemValue = (item) => {
    return item;
  }

  setItems = (items) => {
    this.setState({ items: items })
  }

  onChange = (e) => {
    let value = e.target.value;
    if (this.props.onChange) {
      this.props.onChange(value, this.state.items, this.setItems);
    }
    this.setState({ value: value });
  }

  render() {
    const props = this.props;
    const getValue = props.getItemValue ? props.getItemValue : this.getItemValue;
    const renderItem = (item, isHighlighted) => (
      <div style={{ background: isHighlighted ? 'lightgray' : 'white' }}>
        {getValue(item)}
      </div>
    )
    const shouldItemRender = (state, value) => {
      return getValue(state).startsWith(value);
    }
    if (props.shouldItemRender) {
      shouldItemRender = props.shouldItemRender;
    }
    return (
      <Autocomplete
        // wrapperStyle={{ position: 'relative', display: 'inline-block' }}
        inputProps={props.inputProps ? props.inputProps : {}}
        getItemValue={getValue}
        items={this.state.items}
        renderItem={renderItem}
        value={this.state.value}
        onChange={this.onChange}
        onSelect={(val) => this.setState({ value: val })}
        shouldItemRender={shouldItemRender}
      />
    );
  }
}

AutoCompleteInput.propTypes = propTypes;
AutoCompleteInput.defaultProps = defaultProps;


class EventsPage extends Component {

  render() {
    let search = parseUrlParams(this.props);
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
              <ReactTableDemo />
            </CardBody>
          </Card>
      </div>
    )
  }
}


export default EventsPage;
