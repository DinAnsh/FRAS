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

const video1 = document.getElementById("video1");
const video2 = document.getElementById("video2");
const video3 = document.getElementById("video3");
const canvas1 = document.getElementById("canvas1");
const canvas2 = document.getElementById("canvas2");
const canvas3 = document.getElementById("canvas3");
const saveBtn1 = document.getElementById("save-btn1");
const saveBtn2 = document.getElementById("save-btn2");
const saveBtn3 = document.getElementById("save-btn3");

// navigator.mediaDevices
//   .getUserMedia({ video: true })
//   .then((streamObj) => {
//     stream = streamObj;
//     video.srcObject = stream;
//     video.play();
//   })
//   .catch((error) => {
//     console.log("Error accessing camera", error);
//   });

// Get available cameras
navigator.mediaDevices.enumerateDevices().then(devices => {
  let cameras = devices.filter(device => device.kind === 'videoinput');
  console.log(cameras)
  // Switch to next camera
  let currentCameraIndex = 0;
  function switchCamera() {
    currentCameraIndex = (currentCameraIndex + 1) % cameras.length;
  }
  
  // Start stream with selected camera
  function startStream() {
    let constraints = {
      video: {
        deviceId: cameras[currentCameraIndex].deviceId
      }
    };
    navigator.mediaDevices.getUserMedia(constraints).then(streamObj => {
      stream = streamObj;
      video1.srcObject = stream;
      video1.play();
    });
  }
  function startStream2() {
    switchCamera()
    let constraints = {
      video: {
        deviceId: cameras[currentCameraIndex].deviceId
      }
    };
    navigator.mediaDevices.getUserMedia(constraints).then(streamObj => {
      stream = streamObj;
      video2.srcObject = stream;
      video2.play();
    });
  }
  function startStream3() {
    switchCamera()
    let constraints = {
      video: {
        deviceId: cameras[currentCameraIndex].deviceId
      }
    };
    navigator.mediaDevices.getUserMedia(constraints).then(streamObj => {
      stream = streamObj;
      video3.srcObject = stream;
      video3.play();
    });
  }
  // Call the function to start stream with default camera
  startStream();
  startStream2();
  startStream3();
  // Add event listener to switch camera on button click
  document.getElementById('switchCameraButton').addEventListener('click', switchCamera);
});


var imagesPayload = new FormData();

function captureImage(event, camnum) {
  event.preventDefault();
  var video=null;
  var canvas=null;

  if( camnum===1 ){
    video = video1;
    canvas = canvas1;
  }else if( camnum===2){
    video = video2; 
    canvas = canvas2;
  }else if( camnum===3){
    video = video3;  
    canvas = canvas3;
  }

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
  imagesPayload.append("image"+String(camnum), dataURItoBlob(class_image), "image"+String(camnum)+".jpg");
  
}


// Helper function to convert dataURI to Blob object
function dataURItoBlob(dataURI) {
  var byteString = atob(dataURI.split(',')[1]);
  var ab = new ArrayBuffer(byteString.length);
  var ia = new Uint8Array(ab);
  for (var i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  return new Blob([ab], { type: 'image/jpeg' });
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

function sendImages(data) {
  const csrftoken = getCSRFToken();

  // Send the image data to the Django server using AJAX
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "../dashboard/face_recognize/", true);
  // xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  xhr.onload = function () {
    if (xhr.status === 200) {
      alert("Class Image saved successfully");
    }
  };
  xhr.send(data);
}

//  for capture image using button
saveBtn1.addEventListener("click", function (event) {
  captureImage(event, 1);
});
saveBtn2.addEventListener("click", function (event) {
  captureImage(event, 2);
});
saveBtn3.addEventListener("click", function (event) {
  captureImage(event, 3);
});

var sendBtn = document.querySelector("#sendbtn");
sendBtn.addEventListener("click", function (event) {
  sendImages(imagesPayload);
});



// Call captureImage function every 5 seconds
// setInterval(captureImage, 5000);
