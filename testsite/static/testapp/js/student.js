// Camera capture
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("capture-btn");
const retakeBtn = document.getElementById("retake-btn");
const saveBtn = document.getElementById("save-btn");

let stream;

//------------------ Capture image from video stream and display in canvas ---------------
captureBtn.addEventListener("click", () => {
  video.style.display = "none";
  canvas.style.display = "block";
  retakeBtn.style.display = "block";

  captureBtn.style.display = "none";

  saveBtn.style.display = "block";
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const tracks = stream.getTracks();
  tracks.forEach((track) => {
    track.stop();
  });
});


// --------------------- retake button ---------------------------
retakeBtn.addEventListener("click", () => {
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
  video.style.display = "block";
  canvas.style.display = "none";
  saveBtn.style.display = "none";
  captureBtn.style.display = "block";
  retakeBtn.style.display = "none";
});


//----------------------- for student face register -------------------------
function sregister() {
  document.getElementById("myModal3").style.display = "block";
  video.srcObject = null;
  canvas.style.display = "none";
  video.style.display = "block";

  // Get video stream from user's camera
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
}


//------------------ Save Button -------------------------
saveBtn.addEventListener("click", () => {
  if (canvas.style.display != "block") {
    alert("Please capture the student image first!");
    return;
  }

  //Backend code to save the image with enrollment ids

  //After the image is successfully saved in db
  //change the register button with a green tick

  closeModal3();
});


//---------------------- search button --------------------------
function search() { }


//-------------------------- sort button -------------------------
function sort() { }


// ---------------- to show the students list of selected class with pagination ---------------------

// Get the CSRF token from a cookie
function getCSRFToken() {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // The CSRF token cookie name may vary depending on the server-side framework
      if (cookie.substring(0, 10) === 'csrftoken=') {
        cookieValue = decodeURIComponent(cookie.substring(10));
        break;
      }
    }
  }
  return cookieValue;
}

function getStudents(pageNumber) {
  // Get the class ID from the select box
  var classId = document.getElementById('class-dropdown').value;

  // Make an AJAX request to the Django view
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '../students/get-student-data/?class=' + classId + '&page=' + pageNumber, true);
  xhr.setRequestHeader('X-CSRFToken', getCSRFToken());
  xhr.onload = function () {
    if (xhr.status === 200) {
      // Parse the JSON response
      var response = JSON.parse(xhr.responseText);

      // Update the student table with the new data
      var tableBody = document.getElementById('student-list');
      tableBody.innerHTML = '';
      for (var i = 0; i < response.data.length; i++) {
        var student = response.data[i];
        var row = '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + '</td></tr>';
        tableBody.innerHTML += row;
      }

      // Update the pagination links
      var prevLink = document.getElementById('prev-link');
      var nextLink = document.getElementById('next-link');
      const currentPage = response.page_obj.current_page;
      const totalPages = response.page_obj.total_pages;
      const pageLabel = 'Page ' + currentPage + ' of ' + totalPages ;   //`Page ${currentPage} of ${totalPages}`;
      const pageElement = document.querySelector('.page-label');
      pageElement.textContent = pageLabel;

      if (response.page_obj.has_previous) {
        prevLink.setAttribute('onclick', 'getStudents(' + response.page_obj.previous_page_number + ')');
        prevLink.style.display = 'inline-block';
      } else {
        prevLink.style.display = 'none';
      }
      if (response.page_obj.has_next) {
        nextLink.setAttribute('onclick', 'getStudents(' + response.page_obj.next_page_number + ')');
        nextLink.style.display = 'inline-block';
      } else {
        nextLink.style.display = 'none';
      }
    }
  };
  xhr.send();
}
