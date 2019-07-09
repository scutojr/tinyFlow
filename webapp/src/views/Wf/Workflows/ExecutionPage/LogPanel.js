import React, { Component } from 'react';
import {
  Card, FormGroup, CustomInput,
} from 'reactstrap';


class LogPannel extends Component {
  constructor(props) {
    super(props);
    this.state = {
      phases: {
        all: true
      }
    }
    this.phases = undefined;
  }

  getPhases = (logs) => {
    if (this.phases != undefined) {
      return this.phases;
    }
    let phases = new Set();
    for (let [time, phase, msg] of logs) {
      phases.add(phase);
    }
    this.phases = phases;
    return phases;
  }

  buildLogContent = () => {
    const logs = this.props.logs;
    const lines = [];
    const phases = this.state.phases;
    const all = phases.all;
    for (let [time, phase, msg] of logs) {
      if (all || phases[phase]) {
        lines.push(`${time} ${phase} ${msg}`)
      }
    }
    console.log(lines);
    return lines.join("\n");

  }

  render() {
    const logs = this.props.logs;
    let phases = new Array(...this.getPhases(logs));
    for (let p of phases) {
      if (this.state.phases[p] == undefined) {
        this.state.phases[p] = false;
      }
    }
    phases.splice(0, 0, "all");
    const content = this.buildLogContent();

    return (
      <>
        <FormGroup>
          <div>
            {
              phases.map((phase, i) => {
                return (
                  <CustomInput
                    id={phase} key={phase} inline
                    type="checkbox" label={phase}
                    checked={this.state.phases[phase]}
                    onChange={(e) => {
                      if (phase == "all") {
                        for (let key in this.state.phases) {
                          this.state.phases[key] = false;
                        }
                        this.state.phases["all"] = true;
                      } else {
                        this.state.phases[phase] = e.target.checked;
                        this.state.phases["all"] = false;
                      }
                      this.setState({});
                    }}
                  />
                )
              })
            }
          </div>
        </FormGroup>
        <div
          style={{
            height: "500px",
            overflow: "auto",
            "margin-top": "20px"
          }}
        >
          <Card>
            <textarea
              style={{
                width: "100%",
                height: "470px"
              }}
              value={content}
              spellCheck={false}
            />
          </Card>
        </div>
      </>
    )
  }
}


export default LogPannel;