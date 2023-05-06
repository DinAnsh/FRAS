var imgnum = document.querySelector("#imgnum");

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

function closeModal3() {
  const tracks = stream.getTracks();
  tracks.forEach((track) => {
    track.stop();
  });
  // video.srcObject = null;
  document.getElementById("myModal3").style.display = "none";
  imgnum.textContent = 0;
  captureBtn.style.display = 'block';
  retakeBtn.style.display = 'none';
  nextBtn.style.display = 'none';
  saveBtn.style.display = 'none';
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
  }
};

// Camera capture
let stream;
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

const captureBtn = document.getElementById("capture-btn");
const retakeBtn = document.getElementById("retake-btn");
const saveBtn = document.getElementById("save-btn");
const nextBtn = document.getElementById("next-btn");

let imageCounter = 0;
const finalCanvas = document.createElement('canvas');
const finalContext = finalCanvas.getContext('2d');
finalCanvas.width = canvas.width * 3;
finalCanvas.height = canvas.height * 2;

const captureWindow = document.querySelector('.capture-window');
const imageContainer = document.getElementById("image-container");
const imgElement = document.createElement('img');
const w = canvas.width;
const h = canvas.height;

//------------------ Capture image from video stream and display in canvas ---------------
captureBtn.addEventListener("click", () => {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext('2d');
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.style.display = 'block';
  video.style.display = 'none';

  captureBtn.style.display = 'none';
  nextBtn.style.display = 'block';
  retakeBtn.style.display = 'block';

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

  captureBtn.style.display = "block";
  nextBtn.style.display = "none";
  retakeBtn.style.display = "none";
});

// ------------------------- next button ---------------------------------
nextBtn.addEventListener("click", () => {
  imageCounter++;
  imgnum.textContent = imageCounter;
  canvas.style.display = 'none';
  video.style.display = 'block';

  retakeBtn.style.display = 'none';
  nextBtn.style.display = 'none';
  captureBtn.style.display = 'block';
  if (imageCounter < 5) {
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

  if (imageCounter < 4) {
    finalContext.drawImage(canvas, (imageCounter - 1) * w, 0, w, h);
  }
  if (imageCounter > 3 && imageCounter < 5) {
    finalContext.drawImage(canvas, (imageCounter - 4) * w, h, w, h);
  }
  if (imageCounter === 5) {
    finalContext.drawImage(canvas, (imageCounter - 4) * w, h, w, h);
    imageCounter = 0;

    const tracks = stream.getTracks();
    tracks.forEach((track) => {
      track.stop();
    });

    saveBtn.style.display = "block";
    captureBtn.style.display = "none";
    video.style.display = 'none';

    captureWindow.style.display = 'none';
    imageContainer.style.display = 'block';

    imgElement.width = 500;
    imgElement.height = 250;

    imgElement.src = finalCanvas.toDataURL();
    imageContainer.appendChild(imgElement);

    alert("Well done! You've captured the required number of images.");
  }
});


//----------------------- for student face register -------------------------
let enrollId = null;
function sregister() {
  captureWindow.style.display = 'block';
  imageContainer.style.display = 'none';

  const tdElement = this.parentElement.parentElement.firstElementChild;
  enrollId = tdElement.textContent;

  document.getElementById("myModal3").style.display = "block";
  canvas.style.display = "none";
  video.style.display = "block";
  bufferingElement.style.display = 'block';

  // Get video stream from user's camera
  video.srcObject = null;
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
  saveBtn.style.display = 'none';
  document.querySelector('.takebtn').lastElementChild.style.display = 'block';

  // Convert the canvas to a base64 encoded string
  const imageData = finalCanvas.toDataURL("image/jpeg");
  const csrftoken = getCSRFToken();

  // Send the image data to the Django server using AJAX
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/testapp/upload_image/", true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  xhr.onload = function () {
    if (xhr.status === 200) {
      captureBtn.style.display = "block";
      retakeBtn.style.display = "none";
      document.querySelector('.takebtn').lastElementChild.style.display = 'none';

      getStudents(currentPage);
      updateStatus();

      alert("Image saved successfully");
    } else{
      var response = JSON.parse(xhr.responseText);
      alert(response.status);
    }
    closeModal3();
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
        location.reload();
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

function getStudents(page = 1) {
  sortBtn.style.display = '';

  // Get the class ID from the select box
  var classId = document.getElementById('class-dropdown').value;
  var xhr = new XMLHttpRequest();

  // to display export button
  if (classId) {
    document.getElementById('export-btn').style.display = 'none';
    document.getElementById('train-btn').style.display = 'block';
    document.getElementById('note').style.display = 'block';
  }

  // Make an AJAX request to the Django view
  xhr.open('GET', '../students/get-student-data/?class=' + classId, true);
  xhr.setRequestHeader('X-CSRFToken', getCSRFToken());

  xhr.onload = function () {
    if (xhr.status === 200) {
      // currentPage = 1;
      var response = JSON.parse(xhr.responseText);
      data = response.data;

      headers.innerHTML = "<th class='tcol1'>Enrollment ID</th><th class='tcol2'>Name</th><th class='tcol3'>Email</th><th class='tcol4'>Mobile</th><th class='tcol6'>Status</th>"
      renderData(page);
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
      html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + "</td><td class='sregisterBtn'>" + '</td></tr>';
    } else {
      html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + "</td><td class='okStatus'>" + '</td></tr>';
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


// updating the status to register and OK based on the absence of img
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
  okStatus.title = 'Registered! (Click again if you want to re-register)';

  var okays = document.querySelectorAll('.okStatus');
  okays.forEach(function (element) {
    if (!element.hasChildNodes()) {
      element.appendChild(okStatus.cloneNode(true)).addEventListener('click', sregister);
    }
  });
}


//-------------------------- sort button -------------------------
const sortBtn = document.getElementById('sortBtn');
sortBtn.addEventListener('click', () => {
  var classId = document.getElementById('class-dropdown').value;
  if (classId) {
    const columnToSort = 'img'; // the column to sort by
    data.sort((a, b) => {
      const aVal = a[columnToSort] ? 0 : 1;
      const bVal = b[columnToSort] ? 0 : 1;

      return bVal - aVal; // sort in descending order of button presence
    });
    renderData(currentPage);
  }
  else {
    document.getElementById('pagination').style.display = '';
    document.getElementById('page-btn').style.display = 'none';
    document.querySelector('.page-label').textContent = "Please select class!";
  }
})


//---------------------- search button --------------------------
const searchInput = document.getElementById('searchId');
searchInput.addEventListener('keyup', function () {
  var classId = document.getElementById('class-dropdown').value;
  var detailsVal = document.getElementById('all-details').value;

  if (classId && detailsVal === '0') {
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
        html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + "</td><td class='sregisterBtn'>" + '</td></tr>';
      } else {
        html += '<tr><td>' + student.enroll + '</td><td>' + student.name + '</td><td>' + student.email + '</td><td>' + student.mobile + "</td><td class='okStatus'>" + '</td></tr>';
      }
    });

    tableBody.innerHTML = html;
    updateStatus();
    document.getElementById('pagination').style.display = 'none';

    // to remain on the same page after clearing the search
    if (searchInput.value === '') {
      renderData(currentPage);
      document.getElementById('pagination').style.display = '';
    }
  } else if (classId && detailsVal === '1') {
    const searchText = searchInput.value.toLowerCase();

    const searchData = [];
    for (let i = 0; i < attd.length; i++) {
      const enrollText = attd[i][0].toLowerCase();

      if (enrollText.includes(searchText)) {
        searchData.push(attd[i]);
      }
    }

    tableBody.innerHTML = '';
    let html = '';

    searchData.forEach(student => {
      html += '<tr><td>' + student[0] + '</td>';

      for (let i = 1; i < student.length; i++) {
        html += '<td>' + student[i] + String('%') + '</td>';
      }

      html += '</tr>';
    });

    tableBody.innerHTML = html;
    document.getElementById('pagination').style.display = 'none';

    // to remain on the same page after clearing the search
    if (searchInput.value === '') {
      renderAttendance(currentPage);
      document.getElementById('pagination').style.display = '';
    }
  } else {
    document.getElementById('pagination').style.display = '';
    document.getElementById('page-btn').style.display = 'none';
    document.querySelector('.page-label').textContent = "Please select class!";
  }

});

// to remain on the same page after clearing the search using close btn
searchInput.addEventListener('search', (event) => {
  var classId = document.getElementById('class-dropdown').value;
  var detailsVal = document.getElementById('all-details').value;

  if (classId && detailsVal === '0') {
    if (event.target.value === '') {
      // The close button was clicked
      renderData(currentPage);
      document.getElementById('pagination').style.display = '';
    }
  } else if (classId && detailsVal === '1') {
    if (event.target.value === '') {
      // The close button was clicked
      renderAttendance(currentPage);
      document.getElementById('pagination').style.display = '';
    }
  } else {
    document.getElementById('pagination').style.display = '';
    document.getElementById('page-btn').style.display = 'none';
    document.querySelector('.page-label').textContent = "Please select class!";
  }
});


// -------------------------- buffering ---------------------------
var bufferingElement = document.getElementById('buffering');
var globalBuffering = document.querySelector('.bufferModal');


// -------------------- export student's data to excel sheet ------------------
function downloadExcel() {
  // Create a new workbook & worksheet
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Sheet1');

  document.getElementById('export-btn').style.display = 'none';
  document.getElementById('buffer').style.display = 'block';
  // to center align the text - not working
  // worksheet.properties.defaultCellStyle = {
  //   alignment: { horizontal: 'center' }
  // };

  // Add title to worksheet
  worksheet.mergeCells('A1:F1');
  const titleCell = worksheet.getCell('B1');
  titleCell.value = 'COLLEGE OF TECHNOLOGY AND ENGINEERING, UDAIPUR';
  titleCell.font = { size: 16, bold: true };

  // to include the class and session info
  const selectClass = document.getElementById('class-dropdown');
  const selectedIndex = selectClass.selectedIndex;
  const selectedOption = selectClass.options[selectedIndex];
  const now = new Date();
  const currentYear = now.getFullYear() - selectClass.value;
  const nextYear = currentYear + 1;

  // add the title
  worksheet.mergeCells('A2:F2');
  const sub_titleCell = worksheet.getCell('B2');
  sub_titleCell.value = 'B.Tech. ' + selectedOption.textContent + ' Attendance Sheet';  // + currentYear.toString() + '-' + nextYear.toString();
  sub_titleCell.font = { size: 14, bold: false };

  // Parse the HTML table and extract its data
  const table = document.getElementById('students-table');
  const rows = table.getElementsByTagName('tr');
  const headerRow = Array.from(rows[0].children);

  // Add header row to worksheet
  const headerValues = headerRow.map((th) => th.textContent.trim());
  worksheet.addRow(headerValues);

  // set the column widths
  // const columnWidths = [];
  // for (let i = 0; i < headerRow.length; i++) {
  //   const width = headerRow[i].offsetWidth;
  //   columnWidths.push(width);
  // }
  worksheet.columns.forEach((column, index) => {
    column.width = 15;
  });

  // parse the whole data of the selected class
  // const array = data.map(item => ([
  //   item.enroll,
  //   item.name,
  //   item.email,
  //   item.mobile,
  // ]));

  // Add data rows to worksheet
  attd.forEach((row) => {
    worksheet.addRow(row);
  });



  // Save workbook as binary Excel file
  workbook.xlsx.writeBuffer().then((buffer) => {
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(blob);
    downloadLink.download = 'table.xlsx';
    downloadLink.click();
    document.getElementById('export-btn').style.display = 'block';
    document.getElementById('buffer').style.display = 'none';
  });
}


// -----------------------Upload Faces Grid---------------------------
function uploadGrid(event) {
  const files = event.target.files;
  const file = files[0];

  var formData = new FormData();
  formData.append("image", file);
  formData.append("enrollId", enrollId);

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/testapp/upload_image/", true);
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


// ---------------------- train the model -------------------------------------
const progressBar = document.querySelector('.buffer');
const fill = progressBar.querySelector('.fill');
const text = progressBar.querySelector('.text');
const train = ["Fetching Images", "Calculating Embeddings", "Initializing SVM Classifier", "Model Training"];

let progress = 0;
const increment = 1;

function trainModel() {
  var year = document.querySelector("#class-dropdown").value;
  var xhr = new XMLHttpRequest();
  globalBuffering.style.display = 'block';
  
  const duration = (data.length + 2.5)*1000;
  const interval = duration / (100 / increment);
  
  const timer = setInterval(() => {
    progress += increment;
    fill.style.width = `${progress}%`;
    text.textContent = `${train[Math.floor(progress / 25)]}...`;

    if (progress >= 100) {
      clearInterval(timer);
      text.textContent = "Model Training Completed!"
    }
  }, interval);

  xhr.open("POST", "../students/train_model/", true);
  xhr.setRequestHeader("X-CSRFToken", getCSRFToken());

  xhr.onload = function () {
    globalBuffering.style.display = 'none';
    if (xhr.status === 200) {
      alert("Model Trained Successfully");
    } else {
      alert("Failed to Train Model");
      // console.error("Failed to Train Model");
    }
  };
  xhr.send(JSON.stringify({ "year": year }));
}


// ---------------------------- change details table --------------------------
function changeDetails() {
  var classId = document.getElementById('class-dropdown').value;
  var detailsVal = document.getElementById('all-details').value;

  if (classId && detailsVal) {
    if (detailsVal === '0') {
      getStudents();
    } else if (detailsVal === '1') {
      getAttendance();
    }
  }
}


// --------------------------------- get attendance and pagination -----------------------------
let attd = [];
let header = [];
let headers = document.querySelector('thead');
function getAttendance(page = 1) {
  sortBtn.style.display = 'none';

  // Get the class ID from the select box
  var classId = document.getElementById('class-dropdown').value;
  var xhr = new XMLHttpRequest();

  // to display export button
  if (classId) {
    document.getElementById('export-btn').style.display = 'block';
    document.getElementById('train-btn').style.display = 'none';
    document.getElementById('note').style.display = 'none';
  }

  // Make an AJAX request to the Django view
  xhr.open('GET', '../students/get-attendance-data/?class=' + classId, true);
  xhr.setRequestHeader('X-CSRFToken', getCSRFToken());

  xhr.onload = function () {
    if (xhr.status === 200) {
      var response = JSON.parse(xhr.responseText);
      if (response.success) {
        attd = response.data;
        header = response.header;

        headers.innerHTML = '';
        let html = '<tr><th>Enrollment ID</th>';

        header.forEach(heading => {
          html += '<th>' + heading + '</th>';
        });

        headers.innerHTML = html + '</tr>';

        renderAttendance(page);
      } else {
        alert(response.message);
      }
    }
  };
  xhr.send();
}


function renderAttendance(page) {
  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const pageData = attd.slice(startIndex, endIndex);
  currentPage = page;

  tableBody.innerHTML = '';
  let html = '';

  pageData.forEach(student => {
    html += '<tr><td>' + student[0] + '</td>';

    for (let i = 1; i < student.length; i++) {
      html += '<td>' + student[i] + String('%') + '</td>';
    }

    html += '</tr>';
  });

  tableBody.innerHTML = html;

  // update the previous and next buttons
  const totalPages = Math.ceil(attd.length / itemsPerPage);
  var prevLink = document.getElementById('prev-link');
  var nextLink = document.getElementById('next-link');

  const pageLabel = 'Page ' + currentPage + ' of ' + totalPages;
  const pageElement = document.querySelector('.page-label');
  pageElement.textContent = pageLabel;


  if (currentPage > 1) {
    previous_page = currentPage - 1;
    prevLink.setAttribute('onclick', 'renderAttendance(' + previous_page + ')');
    prevLink.style.display = 'inline-block';
  } else {
    prevLink.style.display = 'none';
  }
  if (currentPage < totalPages) {
    next_page = currentPage + 1;
    nextLink.setAttribute('onclick', 'renderAttendance(' + next_page + ')');
    nextLink.style.display = 'inline-block';
  } else {
    nextLink.style.display = 'none';
  }
}