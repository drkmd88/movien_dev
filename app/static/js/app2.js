var svg = d3.select("svg"),
    margin = {top: 20, right: 20, bottom: 30, left: 100},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom,
    g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

//var parseTime = d3.timeParse("%y");

var x = d3.scaleLinear()
    .rangeRound([0, width]);

var y = d3.scaleLinear()
    .rangeRound([height, 0]);

var line = d3.line()
    .x(function(d) { return x(d.year); })
    .y(function(d) { return y(d.gross); });

d3.csv("/static/js/year_gross.csv", function(d) {
  d.year = +d.year;
  d.gross = +d.gross;
  return d;
}, function(error, data) {
  if (error) throw error;

  x.domain(d3.extent(data, function(d) { return d.year; }));
  y.domain(d3.extent(data, function(d) { return d.gross; }));

  g.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

  g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y))
    .append("text")
      .attr("fill", "#000")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", "0.71em")
      .style("text-anchor", "end")
      .text("Box Office in USA ($)");

  g.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("d", line);

  g.append("text")
    .attr("x", (width / 2))
    .attr("y", margin.top / 2)
    .attr("text-anchor","middle")
    .style("font-size","20px")
    .text("Yearly Box Office in USA");

});
