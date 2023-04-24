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
//-------------------------------- cctv-video -------------------------
// test code

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
// const saveBtn = document.getElementById("save-btn");

// --------------testing-----------------

navigator.mediaDevices
  .enumerateDevices()
  .then((devices) => {
    const videoDevices = devices.filter(
      (device) => device.kind === "videoinput"
    );
    console.log(videoDevices);
    const c = document.querySelector(".adminrights-container18");

    for (let i = 0; i < videoDevices.length; i++) {
      if (videoDevices[i].label.includes("OBS") || i > 2) {
        break;
      }
      const deviceId = videoDevices[i].deviceId;
      navigator.mediaDevices
        .getUserMedia({ video: { deviceId: deviceId } })
        .then((stream) => {
          const live = document.createElement("div");
          live.classList = "live";

          const video = document.createElement("video");
          video.style.transform = "scaleX(-1)";
          video.id = "player" + i;
          video.style.width = "100%";

          const h = document.createElement("h3");
          h.style.width = "fit-content";
          h.style.margin = "0 auto";
          h.textContent = "Camera ID: " + String(100 + i);
          
          var h2 = h.cloneNode(true);
          
          var xhr = new XMLHttpRequest();
          xhr.open("GET", "../dashboard/?get_class=1&cam_id="+String(100 + i), true);
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
          xhr.onload = function () {
            let resp = xhr.response;
          
            if (xhr.status === 200) {
              resp = JSON.parse(resp);
              h2.textContent = "Class: " + resp.class;
            } else {
              console.error("Failed to upload image");
            }
          };
          xhr.send();
          
          live.appendChild(video);
          live.appendChild(h);
          live.appendChild(h2);

          //Save btn to capture images(Can delete later)
          const saveBtn = document.createElement("button");
          saveBtn.textContent = "Save";
          live.appendChild(saveBtn);

          c.appendChild(live);
          video.srcObject = stream;
          video.play();


        })
        .catch((error) => {
          console.error(error);
        });
    }
  })
  .catch((error) => {
    console.error(error);
  });

// var myVariable = document.getElementById("my-data").getAttribute("data-my-variable");
// console.log(myVariable); // prints "Hello World"

// console.log(myVariable["100"]);
// var dict = JSON.parse(myVariable);   //string->dict
// console.log(dict);
// console.log(typeof(dict));

var imagesPayload = new FormData();

function captureImage(event, camnum) {
  event.preventDefault();
  var video = null;
  var canvas = null;

  if (camnum === 1) {
    video = video1;
    canvas = canvas1;
  } else if (camnum === 2) {
    video = video2;
    canvas = canvas2;
  } else if (camnum === 3) {
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
  imagesPayload.append(
    "image" + String(camnum),
    dataURItoBlob(class_image),
    "image" + String(camnum) + ".jpg"
  );
}

// Helper function to convert dataURI to Blob object
function dataURItoBlob(dataURI) {
  var byteString = atob(dataURI.split(",")[1]);
  var ab = new ArrayBuffer(byteString.length);
  var ia = new Uint8Array(ab);
  for (var i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  return new Blob([ab], { type: "image/jpeg" });
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
// saveBtn1.addEventListener("click", function (event) {
//   captureImage(event, 1);
// });
// saveBtn2.addEventListener("click", function (event) {
//   captureImage(event, 2);
// });
// saveBtn3.addEventListener("click", function (event) {
//   captureImage(event, 3);
// });

var sendBtn = document.querySelector("#sendbtn");
sendBtn.addEventListener("click", function (event) {
  sendImages(imagesPayload);
});

// Call captureImage function every 5 seconds
// setInterval(captureImage, 5000);
