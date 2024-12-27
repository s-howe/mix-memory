// Set up the dimensions of the SVG container
const width = window.innerWidth;
const height = window.innerHeight;

// Create the SVG container
const svg = d3.select("#force-graph");

// Load the JSON data using d3.json()
d3.json("network.json").then(graphData => {
    // Create the force simulation
    const simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2));

    // Create links
    const link = svg.selectAll(".link")
        .data(graphData.links)
        .enter().append("line")
        .attr("class", "link");

    // Create nodes
    const node = svg.selectAll(".node")
        .data(graphData.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstart)
            .on("drag", dragged)
            .on("end", dragend));

    node.append("circle")
        .attr("r", 10);

    node.append("text")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .text(d => d.name);

    // Update positions every tick
    simulation.on("tick", function () {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstart(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragend(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}).catch(error => {
    console.error("Error loading the JSON data: ", error);
});
