import React, { Component } from 'react';
import * as dagre from "dagre";
import * as _ from "lodash";

import {
	DiagramEngine,
	DiagramModel,
	DefaultNodeModel,
	LinkModel,
	DefaultPortModel,
	DiagramWidget,
	DefaultLinkModel
} from "storm-react-diagrams";

import "storm-react-diagrams/src/sass/main.scss";


let count = 1;

const size = {
	width: 60,
	height: 60
};


function distributeElements(model) {
	let clonedModel = _.cloneDeep(model);
	let nodes = distributeGraph(clonedModel);
	nodes.forEach(node => {
		let modelNode = clonedModel.nodes.find(item => item.id === node.id);
		modelNode.x = node.x - node.width / 2;
		modelNode.y = node.y - node.height / 2;
	});
	return clonedModel;
}


function distributeGraph(model) {
	let nodes = mapElements(model);
	let edges = mapEdges(model);
	let graph = new dagre.graphlib.Graph();
	graph.setGraph({});
	graph.setDefaultEdgeLabel(() => ({}));
	//add elements to dagre graph
	nodes.forEach(node => {
		graph.setNode(node.id, node.metadata);
	});
	edges.forEach(edge => {
		if (edge.from && edge.to) {
			graph.setEdge(edge.from, edge.to);
		}
	});
	//auto-distribute
	dagre.layout(graph);
	return graph.nodes().map(node => graph.node(node));
}


function mapElements(model) {
	// dagre compatible format
	return model.nodes.map(node => ({ id: node.id, metadata: { ...size, id: node.id } }));
}


function mapEdges(model) {
	// returns links which connects nodes
	// we check are there both from and to nodes in the model. Sometimes links can be detached
	return model.links
		.map(link => ({
			from: link.source,
			to: link.target
		}))
		.filter(
			item => model.nodes.find(node => node.id === item.from) && model.nodes.find(node => node.id === item.to)
		);
}





class WorkflowDiagram extends Component {
	constructor(props) {
		super(props);
		this.workflow = props.workflow;
	}

	createNode(name) {
		return new DefaultNodeModel(name, "rgb(192,255,255)");
	}

	createLink(nodeFrom, nodeTo, label = "") {
		// count++;
		// const portOut = nodeFrom.addPort(new DefaultPortModel(true, `${nodeFrom.name}-out-${count}`, "Out"));
		// const portTo = nodeTo.addPort(new DefaultPortModel(false, `${nodeFrom.name}-to-${count}`, "IN"));

		const portOut = nodeFrom.addPort(new DefaultPortModel(true, ""));
		const portTo = nodeTo.addPort(new DefaultPortModel(false, ""));

		const link = portOut.link(portTo);
		if (label) {
			link.addLabel(label);
		}
		return link;
	}

	getDistributedModel(engine, model) {
		const serialized = model.serializeDiagram();
		const distributedSerializedDiagram = distributeElements(serialized);

		//deserialize the model
		let deSerializedModel = new DiagramModel();
		deSerializedModel.deSerializeDiagram(distributedSerializedDiagram, engine);
		return deSerializedModel;
	}

	initializePos(entrance, nodeMap, graph) {
		let levels = new Array(nodeMap.size);
		let flags = new Set();
		const stepX = 200, stepY = 200;
		levels.fill(0);

		function genPos(level, nodeName) {
			let posX = levels[level] + stepX, posY = level * stepY;
			levels[level] = posX;
			let node = nodeMap.get(nodeName);
			node.x = posX;
			node.y = posY;

			for (let name of Object.values(graph[nodeName])) {
				if (!flags.has(name)) {
					flags.add(name);
					genPos(level + 1, name);
				}
			}
		}
		genPos(0, entrance);
	}

	render() {
    const workflowData = this.props.workflow;
		let engine = new DiagramEngine();
		engine.installDefaultFactories();
		let model = new DiagramModel();

		let nodes = new Map();
		let links = new Array();

		const graph = workflowData.graph;
		let x = 100, y = 100;
		for (let task in graph) {
			let node = this.createNode(task);
			nodes.set(task, node)
		}

		this.initializePos(workflowData.entrance, nodes, graph);

		nodes.forEach((node, name) => {
			for (let [state, nextTaskName] of Object.entries(graph[name])) {
				links.push(
					this.createLink(node, nodes.get(nextTaskName), state)
				);
			}
		});

		for (let node of nodes.values()) {
			model.addNode(node);
		}
		links.forEach((link) => { model.addLink(link) });
		// engine.setDiagramModel(this.getDistributedModel(engine, model));
		engine.setDiagramModel(model);

		return (
			<div className="srd-demo-workspace">
				<div className="srd-demo-workspace__toolbar">
					{/* <Button/> */}
				</div>
				<div className="srd-demo-workspace__content">
					<DiagramWidget className="srd-demo-canvas" diagramEngine={engine} />
					{/* <DiagramWidget className="srd-demo-canvas" smartRouting={true} diagramEngine={engine} /> */}
				</div>
			</div>
		);
	}
}


export default WorkflowDiagram;