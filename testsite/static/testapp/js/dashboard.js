//----------------------- calendar script -----------------------

$(document).ready(function () {
  $("#calendar").fullCalendar({
    // Options and callbacks
    // themeSystem: 'lux'
  });
});

//---------------------- maxAtt-cls ------------------------------
const maxCls = document.getElementById("maxCls");
const valuesCls = JSON.parse(maxCls.textContent);

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
  .data([
    valuesCls["Second Year"],
    valuesCls["Third Year"],
    valuesCls["Final Year"],
  ])
  .enter()
  .append("rect")
  // positions the rectangle horizontally & vertically
  .attr("x", function (d, i) {
    return i * 50; //with a gap of 50px between each
  })
  .attr("y", function (d) {
    return 220 - d;
  })
  //sets the height & width of each rectangle
  .attr("width", 40)
  .attr("height", function (d) {
    return d;
  })
  .attr("fill", "#d0b49f");

svg
  .selectAll("text")
  .data([
    valuesCls["Second Year"],
    valuesCls["Third Year"],
    valuesCls["Final Year"],
  ])
  .enter()
  .append("text")
  .text(function (d) {
    return d;
  })
  .attr("x", function (d, i) {
    return i * 50 + 10;
  })
  .attr("y", function (d) {
    return 215 - d;
  });

svg
  .append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + 230 + ")")
  .call(d3.axisBottom(xScale));

//-------------------------------- maxAtt-sub -------------------------
const maxSub = document.getElementById("maxSub");
const valuesSub = JSON.parse(maxSub.textContent);

// append svg to the selected element with defined attributes
var svg = d3
  .select("#maxAtt-sub")
  .append("svg")
  .attr("width", 250)
  .attr("height", 250)
  .append("g")
  .attr("transform", "translate(" + 50 + "," + 0 + ")");

var xScale = d3.scalePoint().domain(Object.keys(valuesSub)).range([20, 125]);

// append rectangles to the svg element
svg
  .selectAll("rect")
  .data(Object.values(valuesSub))
  .enter()
  .append("rect")
  // positions the rectangle horizontally & vertically
  .attr("x", function (d, i) {
    return i * 50; //with a gap of 50px between each
  })
  .attr("y", function (d) {
    return 220 - d;
  })
  //sets the height & width of each rectangle
  .attr("width", 40)
  .attr("height", function (d) {
    return d;
  })
  .attr("fill", "#d0b49f");

svg
  .selectAll("text")
  .data(Object.values(valuesSub))
  .enter()
  .append("text")
  .text(function (d) {
    return d;
  })
  .attr("x", function (d, i) {
    return i * 50 + 10;
  })
  .attr("y", function (d) {
    return 215 - d;
  });

svg
  .append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + 230 + ")")
  .call(d3.axisBottom(xScale));

//-------------------------------- CSRF Token-------------------------
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

//---------------To show all cameras Except the default--------------
navigator.mediaDevices
  .enumerateDevices()
  .then((devices) => {
    const videoDevices = devices.filter(
      (device) => device.kind === "videoinput"
    );
    const c = document.querySelector(".adminrights-container18");

    // i=1 need to be 0 if you want to show default(laptop) camera
    for (let i = 1; i < videoDevices.length; i++) {
      if (videoDevices[i].label.includes("OBS")) {
        continue;
      }
      const deviceId = videoDevices[i].deviceId;
      navigator.mediaDevices
        .getUserMedia({ video: { deviceId: deviceId } })
        .then((stream) => {
          const live = document.createElement("div");
          live.classList = "live";

          //Video element
          const video = document.createElement("video");
          // video.style.transform = "scaleX(-1)";
          video.id = "player" + i;
          video.style.width = "100%";

          //Canvas
          const canvas = document.createElement("canvas");
          // canvas.style.transform = "scaleX(-1)";
          canvas.id = "can" + i;
          canvas.style.width = "0";

          //camear id heading
          const h = document.createElement("h3");
          h.style.width = "fit-content";
          h.style.margin = "0 auto";
          h.textContent = "Camera ID: " + String(100 + i);

          live.appendChild(video);
          live.appendChild(canvas);
          live.appendChild(h);

          //class heading
          var h2 = h.cloneNode(true);
          var data = {
            get_class: 1,
            cam_id: String(100 + i),
          };
          var xhr = new XMLHttpRequest();
          xhr.open("POST", "../dashboard/", true);
          xhr.setRequestHeader("Content-Type", "application/json");
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
          xhr.onload = function () {
            let resp = xhr.response;
            if (xhr.status === 200) {
              resp = JSON.parse(resp);
              h2.textContent = "Class: " + resp.class;
              h2.classList.add("classes");
              live.appendChild(h2);
            } else {
            }
          };
          xhr.send(JSON.stringify(data));

          c.appendChild(live);

          document.querySelector("#player" + String(i)).srcObject = stream;
          document.querySelector("#player" + String(i)).play();
        })
        .catch((error) => {
          console.error("Error accessing user media: ", error);
        });
    }
  })
  .catch((error) => {
    console.error(error);
  });

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

//when click on send images all cameras images will be captured and send to server
function sendImages(data) {
  const csrftoken = getCSRFToken();

  // Send the image data to the Django server using AJAX
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "../dashboard/face_recognize/", true);
  // xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  xhr.onload = function () {
    if (xhr.status === 200) {
      console.log(JSON.parse(xhr.response)["status"]);
    }
  };
  xhr.send(data);
}

function get_classes(start) {
  var elements = document.getElementsByClassName("classes");

  if (elements[start].textContent.includes("Final Year")) {
    var num = "4";
  } else if (elements[start].textContent.includes("Third Year")) {
    var num = "3";
  }
  if (elements[start].textContent.includes("Second Year")) {
    var num = "2";
  }

  return num;
}

//Capture img btn call
function capture_images() {
  navigator.mediaDevices.enumerateDevices().then((devices) => {
    const videoDevices = devices.filter(
      (device) => device.kind === "videoinput"
    );
    for (let i = 1; i < videoDevices.length; i++) {
      if (videoDevices[i].label.includes("OBS")) {
        continue;
      }

      var video = document.querySelector("#player" + String(i));
      var canvas = document.querySelector("#can" + String(i));

      // #this should be deleted
      video.style.display = "none";
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      var context = canvas.getContext("2d");
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.style.width = "100%";

      // Convert the canvas to a base64 encoded string
      const class_image = canvas.toDataURL("image/jpeg");
      //because default camera has no class assigned
      if (i != 0) {
        var class_id = get_classes(i - 1);
      } else {
        var class_id = "0";
      }

      //need to add class id with image to know which image is for which class
      imagesPayload.append(
        "image_" + class_id,
        dataURItoBlob(class_image),
        "image" + String(i) + ".jpg"
      );

      console.log("Image of class " + class_id + " Captured");
    }
  });
}

//send images btn call
function sendImagesreq(event) {
  // console.log(imagesPayload);
  sendImages(imagesPayload);
}

// Define a callback function to run every minute
function checkTime() {
  // Get the current time
  var now = new Date();
  var currentHour = now.getHours();
  // if (currentHour == 19) {
  //   console.log("Current hour is 1 PM, skipping action.");
  //   return; // exit function if current hour is not 1 PM
  // }
  // Check if the current minute is one of the target minutes
  var minute = now.getMinutes();
  // 15 30 45 50
  if (minute == 4 || minute == 5 || minute == 6 || minute == 8) {
    // Perform the desired action
    capture_images();
    setTimeout(function () {
      sendImages(imagesPayload);
    }, 5000);
    imagesPayload = new FormData();
    console.log("Performing action at " + now.toLocaleString());
  }
}

// Run the callback function every minute
var imagesPayload = new FormData(); //FormData needs some time to load the data into it
setInterval(checkTime, 60 * 1000);


//-------------------------------------------------END-----------------------------------------------------------
