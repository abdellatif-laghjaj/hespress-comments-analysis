// Fetch data from the Flask API
fetch("/api/data")
    .then((response) => response.json())
    .then((data) => {
        // Pie Chart - Sentiment Distribution
        const sentimentData = data.sentiments;
        const pieData = d3.pie()(sentimentData);
        const colors = ["green", "red", "orange"];
        const arc = d3.arc().innerRadius(50).outerRadius(100);

        const pieChart = d3
            .select("#pie-chart")
            .append("g")
            .attr("transform", "translate(250,150)"); // Adjusted to center the pie chart in the middle

        pieChart
            .selectAll("path")
            .data(pieData)
            .enter()
            .append("path")
            .attr("d", arc)
            .attr("fill", (d, i) => colors[i]);

        pieChart
            .selectAll("text")
            .data(pieData)
            .enter()
            .append("text")
            .attr("transform", (d) => `translate(${arc.centroid(d)})`)
            .attr("text-anchor", "middle")
            .attr("font-size", "12px")
            .attr("fill", "white")
            .text((d) => `${Math.round((d.data / d3.sum(sentimentData)) * 100)}%`);

        // Legend for the pie chart - Positioned below the pie chart
        const legendData = [
            {label: "Positive", color: "green"},
            {label: "Negative", color: "red"},
            {label: "Neutral", color: "orange"},
        ];

        // Append the legend container below the pie chart
        const legend = d3
            .select("#pie-chart")
            .append("g")
            .attr("transform", "translate(120, 280)"); // Move the legend below the pie chart by 100px more

        // Add the color boxes and labels for the legend
        legend
            .selectAll("rect")
            .data(legendData)
            .enter()
            .append("rect")
            .attr("x", (d, i) => i * 100) // Horizontal spacing between legend items
            .attr("y", 0)
            .attr("width", 20)
            .attr("height", 20)
            .attr("fill", (d) => d.color);

        legend
            .selectAll("text")
            .data(legendData)
            .enter()
            .append("text")
            .attr("x", (d, i) => i * 100 + 30) // Position text next to the color boxes
            .attr("y", 15)
            .attr("font-size", "12px")
            .text((d) => d.label);

        // Bar Chart - Comments Activity Over Time
        const activityData = data.activity;
        const dates = data.dates;

        // Set up the SVG dimensions for the bar chart
        const margin = {top: 20, right: 30, bottom: 40, left: 40};
        const width = 500 - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;

        // Create the SVG container for the bar chart
        const barChart = d3
            .select("#bar-chart")
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Define the x and y scales for the bar chart
        const xScale = d3.scaleBand().domain(dates).range([0, width]).padding(0.1); // You can adjust this padding value to control the space between bars

        const yScale = d3
            .scaleLinear()
            .domain([0, d3.max(activityData)])
            .nice()
            .range([height, 0]);

        // Append the bars to the bar chart
        barChart
            .selectAll(".bar")
            .data(activityData)
            .enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", (d, i) => xScale(dates[i])) // X-position is determined by the xScale
            .attr("y", (d) => yScale(d)) // Y-position is determined by the yScale
            .attr("width", xScale.bandwidth()) // Bar width is scaled based on the available width
            .attr("height", (d) => height - yScale(d)) // Bar height based on activity data
            .attr("fill", "steelblue");

        // Add activity number on top of each bar
        barChart
            .selectAll(".bar-text")
            .data(activityData)
            .enter()
            .append("text")
            .attr("class", "bar-text") // Added class for potential styling
            .attr("x", (d, i) => xScale(dates[i]) + xScale.bandwidth() / 2) // Center text on each bar
            .attr("y", (d) => yScale(d) - 5) // Position text slightly above the bar
            .attr("text-anchor", "middle")
            .attr("fill", "black")
            .attr("font-size", "12px")
            .text((d) => d);

        // Add x-axis labels (dates)
        barChart
            .append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");

        // Add y-axis label
        barChart.append("g").attr("class", "y-axis").call(d3.axisLeft(yScale));
    });
