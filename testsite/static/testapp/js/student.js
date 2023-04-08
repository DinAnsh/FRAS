function openModal() {
  document.getElementById("myModal").style.display = "block";
}

function closeModal() {
  document.getElementById("myModal").style.display = "none";
}

// for login
function openModal2() {
  document.getElementById("myModal2").style.display = "block";
}

function closeModal2() {
  document.getElementById("myModal2").style.display = "none";
}

function addcam() {
  document.getElementById("myModal4").style.display = "block";
}

function closeModal3() {
  const tracks = stream.getTracks();
  tracks.forEach((track) => {
    track.stop();
  });
  video.srcObject = null;
  document.getElementById("myModal3").style.display = "none";
}

function closeModal4() {
  document.getElementById("myModal4").style.display = "none";
}

window.onclick = function (event) {
  // console.log(event.target)
  if (event.target == document.getElementById("cbtn")) {
    closeModal();
  } else if (event.target == document.getElementById("cbtn2")) {
    closeModal2();
  } else if (
    event.target == document.getElementById("cbtn3") ||
    event.target == document.getElementById("content3")
  ) {
    closeModal3();
  } else if (
    event.target == document.getElementById("cbtn4") ||
    event.target == document.getElementById("content4")
  ) {
    closeModal4();
  }
};

// Camera capture
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("capture-btn");
const retakeBtn = document.getElementById("retake-btn");
const saveBtn = document.getElementById("save-btn");
let stream;

//------------------ Capture image from video stream and display in canvas ---------------
captureBtn.addEventListener("click", (event) => {
  video.style.display = "none";
  captureBtn.style.display = "none";

  canvas.style.display = "block";
  retakeBtn.style.display = "block";
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
  captureBtn.style.display = "block";

  canvas.style.display = "none";
  saveBtn.style.display = "none";
  retakeBtn.style.display = "none";
});


//----------------------- for student face register -------------------------
let enrollId = null;
function sregister() {

  const tdElement = this.parentElement.parentElement.firstElementChild;
  enrollId = tdElement.textContent;
  // console.log('ID value:', enrollId);


  document.getElementById("myModal3").style.display = "block";
  video.srcObject = null;
  canvas.style.display = "none";
  video.style.display = "block";

  bufferingElement.style.display = 'block';
  // Get video stream from user's camera
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((streamObj) => {
      stream = streamObj;
      video.srcObject = stream;
      video.addEventListener('loadedmetadata', onVideoMetadataLoaded);
      video.play();
    })
    .catch((error) => {
      console.log("Error accessing camera", error);
    });
}


// ------------------------------- Save Button ----------------------------------
saveBtn.addEventListener("click", (event) => {
  event.preventDefault();
  if (canvas.style.display != "block") {
    alert("Please capture the student image first!");
    return;
  }

  // Convert the canvas to a base64 encoded string
  const imageData = canvas.toDataURL("image/jpeg");
  const csrftoken = getCSRFToken();

  // Send the image data to the Django server using AJAX
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/testapp/upload_image/", true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  xhr.onload = function () {
    if (xhr.status === 200) {
      captureBtn.style.display = "block";
      saveBtn.style.display = "none";
      retakeBtn.style.display = "none";

      document.querySelectorAll('tr').forEach(function (row) {
        if (row.firstChild.textContent === enrollId) {
          row.lastChild.className = 'okStatus';
          row.lastChild.firstChild.remove();
        }
      })

      updateStatus();
      
      alert("Image saved successfully");
      closeModal3();
    }
  };

  xhr.send(JSON.stringify({ 'image_data': imageData, 'enrollId': enrollId }));
});

function onVideoMetadataLoaded() {
  bufferingElement.style.display = 'none';
  video.removeEventListener('loadedmetadata', onVideoMetadataLoaded);
}


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


// -------------------------  handle file-upload ------------------------
function uploadStudents(event) {
  const files = event.target.files;
  const file = files[0];
  if (
    file.type === "application/vnd.ms-excel" ||
    file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  ) {

    var formData = new FormData();
    formData.append('studentDetails', file);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '../students/');
    xhr.setRequestHeader('X-CSRFToken', getCSRFToken());

    xhr.onreadystatechange = function () {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        var response = JSON.parse(this.responseText);
        if (response.success) {
          alert(response.message);
        } else {
          alert(response.message);
        }
      }
    };

    xhr.send(formData);
  } else {
    alert("Please select an Excel file");
  }
}


// ---------------- to get the students data of selected class ---------------------
let currentPage = 1;
const itemsPerPage = 10;
let data = [];
const tableBody = document.getElementById('student-list');

function getStudents() {
  // Get the class ID from the select box
  var classId = document.getElementById('class-dropdown').value;
  var xhr = new XMLHttpRequest();

  // Make an AJAX request to the Django view
  xhr.open('GET', '../students/get-student-data/?class=' + classId, true);
  xhr.setRequestHeader('X-CSRFToken', getCSRFToken());

  xhr.onload = function () {
    if (xhr.status === 200) {
      currentPage = 1;
      var response = JSON.parse(xhr.responseText);
      data = response.data;
      renderData(currentPage);
    }
  };
  xhr.send();
}


// --------------------- rendering of students data with pagination -------------------------
function renderData(page) {
  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const pageData = data.slice(startIndex, endIndex);
  currentPage = page;

  tableBody.innerHTML = '';
  let html = '';

  pageData.forEach(student => {
    if (!student.img) {
      html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + '</td><td>' + "</td><td class='sregisterBtn'>" + '</td></tr>';
    } else {
      html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + '</td><td>' + "</td><td class='okStatus'>" + '</td></tr>';
    }
  });

  tableBody.innerHTML = html;

  updateStatus();

  // update the previous and next buttons
  const totalPages = Math.ceil(data.length / itemsPerPage);
  var prevLink = document.getElementById('prev-link');
  var nextLink = document.getElementById('next-link');

  const pageLabel = 'Page ' + currentPage + ' of ' + totalPages;
  const pageElement = document.querySelector('.page-label');
  pageElement.textContent = pageLabel;


  if (currentPage > 1) {
    previous_page = currentPage - 1;
    prevLink.setAttribute('onclick', 'renderData(' + previous_page + ')');
    prevLink.style.display = 'inline-block';
  } else {
    prevLink.style.display = 'none';
  }
  if (currentPage < totalPages) {
    next_page = currentPage + 1;
    nextLink.setAttribute('onclick', 'renderData(' + next_page + ')');
    nextLink.style.display = 'inline-block';
  } else {
    nextLink.style.display = 'none';
  }
}


// updating the status to register and OK based on the abscence of img
function updateStatus() {
  var registerBtn = document.createElement("button");
  registerBtn.innerHTML = "Register";
  registerBtn.classList.add("common_btn", "button2");

  var sregisterBtns = document.querySelectorAll(".sregisterBtn");
  sregisterBtns.forEach(function (element) {
    if (!element.hasChildNodes()) {
      element.appendChild(registerBtn.cloneNode(true)).addEventListener('click', sregister);
    }
  });

  var okStatus = document.createElement("span");
  okStatus.innerHTML = '&#9745;';
  okStatus.title = 'Registered!'

  var okays = document.querySelectorAll('.okStatus');
  okays.forEach(function (element) {
    if (!element.hasChildNodes()) {
      element.appendChild(okStatus.cloneNode(true));
    }
  });
}


//-------------------------- sort button -------------------------
const sortBtn = document.getElementById('sortBtn');
sortBtn.addEventListener('click', () => {
  const columnToSort = 'img'; // index of the column to sort by

  data.sort((a, b) => {
    const aVal = a[columnToSort] ? 0 : 1;
    const bVal = b[columnToSort] ? 0 : 1;

    return bVal - aVal; // sort in descending order of button presence
  });

  renderData(currentPage);
})


//---------------------- search button --------------------------
const searchInput = document.getElementById('searchId');
const tableRows = tableBody.getElementsByTagName('tr');

searchInput.addEventListener('keyup', function () {
  const searchText = searchInput.value.toLowerCase();

  const searchData = [];
  for (let i = 0; i < data.length; i++) {
    const enrollText = data[i].enroll.toLowerCase();

    if (enrollText.includes(searchText)) {
      searchData.push(data[i]);
    }
  }


  tableBody.innerHTML = '';
  let html = '';

  searchData.forEach(student => {
    if (!student.img) {
      html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + '</td><td>' + "</td><td class='sregisterBtn'>" + '</td></tr>';
    } else {
      html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + '</td><td>' + "</td><td class='okStatus'>" + '</td></tr>';
    }
  });

  tableBody.innerHTML = html;
  updateStatus();
  document.getElementById('pagination').style.display = 'none';

  if (searchInput.value === '') {
    renderData(currentPage);
    document.getElementById('pagination').style.display = '';
  }
});


searchInput.addEventListener('search', (event) => {
  if (event.target.value === '') {
    // The close button was clicked
    renderData(currentPage);
    document.getElementById('pagination').style.display = '';
  }
});


// -------------------------- buffering ---------------------------
var bufferingElement = document.getElementById('buffering');