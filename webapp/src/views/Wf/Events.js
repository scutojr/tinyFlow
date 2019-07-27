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
  Label,
  Row,
  Card,
  CardHeader,
  CardBody,
  Badge
} from 'reactstrap';

import ReactTable from 'react-table'
import 'react-table/react-table.css'
import DateTimeRangePicker from '@wojtekmaj/react-datetimerange-picker';


class EventFilter extends Component {
  constructor(props) {
    super(props);

    let nowMs = Date.now();
    let { startBefore, startAfter } = props;
    startBefore = parseInt(startBefore);
    startAfter = parseInt(startAfter);

    startBefore = isNaN(startBefore) ? nowMs : startBefore;
    startAfter = isNaN(startAfter) ? nowMs - (7 * 24 * 3600 * 1000) : startAfter;

    this.state = {
      hideTimePicker: true,
      startBefore: startBefore,
      startAfter: startAfter
    }

    this.inputName = React.createRef();
    this.inputTags = React.createRef();
    this.inputEntity = React.createRef();
    this.eventState = "all";
    this.startBefore = 0;
    this.startAfter = 0;
  }

  _nameSelector() {
    const onChange = (value, items, setItems) => {
      Axios.get('/tobot/web/events/names').then(
        (res) => {
          setItems(res.data);
        }
      )
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
      Axios.get('/tobot/web/events/tags').then(
        (res) => {
          setItems(res.data);
        }
      )
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
      if (items.length == 0) {
        Axios.get('/tobot/web/events/entities').then(
          (res) => {
            setItems(res.data);
          }
        )
      }
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
        <Input type="select" id="cvv" required
          onChange={(e) => { this.eventState = e.target.value }}
        >
          <option value="all"> ALL </option>
          <option value="info"> INFO </option>
          <option value="warning"> WARNING </option>
          <option value="critical"> CRITICAL </option>
        </Input>
      </FormGroup>
    );
  }

  _timeSelector() {
    const { startAfter, startBefore } = this.state;
    return (
      <FormGroup>
        <Label htmlFor="cvv">Time</Label>
        <DateTimeRangePicker
          onChange={(value) => {
            this.setState({
              startAfter: value[0].getTime(),
              startBefore: value[1].getTime()
            })
          }}
          value={[
            new Date(startAfter),
            new Date(startBefore)
          ]} />
      </FormGroup>
    )
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
          const startBefore = this.state.startBefore.toString();
          const startAfter = this.state.startAfter.toString();
          let path = history.location.pathname + "?";
          if (name) params.name = name;
          if (tags) params.tags = tags;
          if (entity) params.entity = entity;
          if (this.eventState != "ALL") {
            console.log(this.eventState)
            params.state = this.eventState;
            console.log(params.state)
          }
          params.startBefore = startBefore;
          params.startAfter = startAfter;
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
          <Btn />
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
    if (this.props.history != undefined) {
      this.props.history.listen((location, action) => {
        this.setState({
          page: 0,
          data: [] // clear the history immediately
        })
        const url = this._buildQueryURL({ query: location.search });
        this.fetchEventData(url);
      });
    }
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
      Cell: (props) => {
        let d = new Date(props.value);
        return `${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}/
                ${d.getMonth() + 1}.${d.getDate()}/
                ${d.getFullYear()}`;
      }
    }
    ];
    // this.generateData();
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
      state: "info",
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
    console.log(state)
    switch (state) {
      case "info":
        return <Badge color="primary">INFO</Badge>;
      case "warning":
        return <Badge color="warning">WARNING</Badge>;
      case "critical":
        return <Badge color="danger">CRITICAL</Badge>;
      default:
        return <Badge color="dark">UNKNOWN</Badge>;
    }
  }


  _buildQueryURL = ({ startBefore, limit, query = this.props.query }) => {
    const params = new URLSearchParams(query);
    if (startBefore) {
      params.set("startBefore", startBefore);
    }
    return "/tobot/web/events?" + params.toString();
  }

  fetchEventData = (url) => {
    this.setState({
      loading: true
    })
    Axios.get(url).then(((res) => {
      let { data, pageSize } = this.state;
      let newData = [];
      newData.push(...data, ...res.data);
      this.setState({
        loading: false,
        pages: Math.ceil(newData.length * 1.0 / pageSize),
        data: newData
      })
    }));
  }

  componentDidMount = (() => {
    let startBefore = this.props.startBefore;
    let limit = this.limit;
    const url = this._buildQueryURL({ startBefore, limit })
    this.fetchEventData(url);
  });

  onPageChannge = ((pageIndex, pageSize) => {
    if (pageSize == undefined) {
      pageSize = this.state.pageSize;
    }
    let data = this.state.data;
    let pos = pageIndex * pageSize
    if (pos >= data.length) {
      let lastEvent = data[data.length - 1];
      const url = this._buildQueryURL({ startBefore: lastEvent.start - 1, limit: this.limit })
      this.fetchEventData(url);
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
  constructor(props) {
    super(props);
    props.history.listen((location, action) => {
      this.setState({});
    });
  }

  parseUrlParams() {
    let search = new URLSearchParams(this.props.location.search);
    let params = {};

    if (search.has("name")) params.name = search.get("name");
    if (search.has("tags")) params.tags = search.get("tags");
    if (search.has("entity")) params.entity = search.get("entity");
    if (search.has("state")) params.state = search.get("state");

    let nowMs = Date.now()
    params.startBefore = search.has("startBefore") ? search.get("startBefore") : nowMs;
    params.startAfter = search.has("startAfter") ? search.get("startAfter") : nowMs - (7 * 24 * 3600 * 1000);

    return params;
  }

  render() {
    let query = this.parseUrlParams();

    return (
      <div className="animated fadeIn">
        <Card>
          <CardHeader>
            Event Filter
          </CardHeader>
          <CardBody>
            <EventFilter {...query} />
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            Event Info
          </CardHeader>
          <CardBody>
            <ReactTableDemo query={query} history={this.props.history} />
          </CardBody>
        </Card>
      </div>
    )
  }
}


export default EventsPage;
