//----------------------- calendar script -----------------------

$(document).ready(function () {
    $('#calendar').fullCalendar({
      // Options and callbacks
      // themeSystem: 'lux'
    });
  });


//---------------------- maxAtt-cls ------------------------------
var data = [150, 200, 250];

// append svg to the selected element with defined attributes
var svg = d3
  .select("#maxAtt-cls")
  .append("svg")
  .attr("width", 250)
  .attr("height", 250)
  .append("g")
  .attr("transform", "translate(" + 50 + "," + 0 + ")");

var xScale = d3.scalePoint().domain(["II", "III", "Iv"]).range([20, 125]);

// append rectangles to the svg element
svg
  .selectAll("rect")
  .data(data)
  .enter()
  .append("rect")
  // positions the rectangle horizontally & vertically
  .attr("x", function (d, i) {
    return i * 50; //with a gap of 50px between each
  })
  .attr("y", function (d) {
    return 300 - d;
  })
  //sets the height & width of each rectangle
  .attr("width", 40)
  .attr("height", function (d) {
    return d - 80;
  })
  .attr("fill", "#d0b49f");

svg
  .selectAll("text")
  .data(data)
  .enter()
  .append("text")
  .text(function (d) {
    return d;
  })
  .attr("x", function (d, i) {
    return i * 50 + 10;
  })
  .attr("y", function (d) {
    return 300 - d - 5;
  });

svg
  .append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + 230 + ")")
  .call(d3.axisBottom(xScale));



//-------------------------------- maxAtt-sub -------------------------
var data = [115, 180, 150];

// append svg to the selected element with defined attributes
var svg = d3
  .select("#maxAtt-sub")
  .append("svg")
  .attr("width", 250)
  .attr("height", 250)
  .append("g")
  .attr("transform", "translate(" + 50 + "," + 0 + ")");

var xScale = d3
  .scalePoint()
  .domain(["CS471", "CS352", "CS247"])
  .range([20, 125]);

// append rectangles to the svg element
svg
  .selectAll("rect")
  .data(data)
  .enter()
  .append("rect")
  // positions the rectangle horizontally & vertically
  .attr("x", function (d, i) {
    return i * 50; //with a gap of 50px between each
  })
  .attr("y", function (d) {
    return 300 - d;
  })
  //sets the height & width of each rectangle
  .attr("width", 40)
  .attr("height", function (d) {
    return d - 80;
  })
  .attr("fill", "#d0b49f");

svg
  .selectAll("text")
  .data(data)
  .enter()
  .append("text")
  .text(function (d) {
    return d;
  })
  .attr("x", function (d, i) {
    return i * 50 + 10;
  })
  .attr("y", function (d) {
    return 300 - d - 5;
  });

svg
  .append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + 230 + ")")
  .call(d3.axisBottom(xScale));


  

//   var video = document.getElementById('player');
//   navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
//     video.srcObject = stream;
//     video.play();
//     // OpenCV code to process video stream
//     cv.onRuntimeInitialized = function () {
//       var cap = new cv.VideoCapture(video);
//       function processVideo() {
//         cap.readAsync(function (frame) {
//           // Process frame here
//           cv.imshow('player', frame);
//           setTimeout(processVideo, 0);
//         });
//       }
//       processVideo();
//     }
//   });
