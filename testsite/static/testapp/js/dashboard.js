//----------------------- calendar script -----------------------

$(document).ready(function () {
  $("#calendar").fullCalendar({
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

//-------------------------------- cctv-video -------------------------
function getCSRFToken() {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // The CSRF token cookie name may vary depending on the server-side framework
      if (cookie.substring(0, 10) === "csrftoken=") {
        cookieValue = decodeURIComponent(cookie.substring(10));
        break;
      }
    }
  }
  return cookieValue;
}

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const saveBtn = document.getElementById("save-btn");

navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((streamObj) => {
    stream = streamObj;
    video.srcObject = stream;
    video.play();
  })
  .catch((error) => {
    console.log("Error accessing camera", error);
  });

function captureImage(event) {
  event.preventDefault();

  // #this should be deleted
  video.style.display = "none";

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
 
  // this should be deleted to not stop the camera after capture image
  const tracks = stream.getTracks();
  tracks.forEach((track) => {
    track.stop();
  });

  // Convert the canvas to a base64 encoded string
  const class_image = canvas.toDataURL("image/jpeg");
  const csrftoken = getCSRFToken();

  // Send the image data to the Django server using AJAX
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "../dashboard/face_recognize/", true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  xhr.onload = function () {
    if (xhr.status === 200) {
      alert("Class Image saved successfully");
    }
  };

  xhr.send(JSON.stringify({ class_image: class_image }));
}

function RecogniseImage(event) {
  const files = event.target.files;
  const file = files[0];

  var formData = new FormData();
  formData.append("image", file);

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "../dashboard/face_recognize/", true);
  xhr.setRequestHeader("X-CSRFToken", getCSRFToken());

  xhr.onreadystatechange = function () {
    if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
      alert("Class Image saved successfully");
    } else {
      console.error("Failed to upload image");
    }
  };
  xhr.send(formData);
}

//  for capture image using button
saveBtn.addEventListener("click", function (event) {
  captureImage(event);
});

// Call captureImage function every 5 seconds
// setInterval(captureImage, 5000);
