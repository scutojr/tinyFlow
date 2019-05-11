
# Workflow feature


# API

## Get workflow info

get list of registered workflow infomation from the server

**Endpoint**: /workflows
**Method**: GET


## Trigger workflows by providing an event

**Endpoint**: /reactor/workflows
**Method**: POST
**Body**
```
TODO: here comes an event
```


## Get information of a workflow with id

**Endpoint**: /workflows/info/<wf_id>
**Method**: GET


## 

**Endpoint**: /userDecisions/<ctx_id>

### GET

get all the workflows that are waiting for event, ctx_id is optional


### POST

**Params**:

Param | Required | Default Value | Description
--- | --- | --- | ---
decision | yes | | one of the decision provided by the workflow 
comment | yes | | the reason why you make this decision
