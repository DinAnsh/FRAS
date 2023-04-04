// for registration
function openModal() {
  document.getElementById("myModal").style.display = "block";
}

function closeModal() {
  document.getElementById("myModal").style.display = "none";
  document.getElementsByClassName("warn")[0].style.display = "none";
  document.querySelector("#submitBtn").style.marginTop = "20px";
  document.querySelector("#register-form").reset();
}

// for login
function openModal2() {
  document.getElementById("myModal2").style.display = "block";
}

function closeModal2() {
  document.getElementById("myModal2").style.display = "none";
  document.getElementsByClassName("loginWarn")[0].style.display = "none";
  document.querySelector("#lsubmitBtn").style.marginTop = "20px";
  document.querySelector("#login-form").reset();
}


//for camera
function addcam(){
  document.getElementById("myModal4").style.display = "block";
}

function closeModal3() {
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
    const tracks = stream.getTracks();
    tracks.forEach((track) => {
      track.stop();
    });
    video.srcObject = null;
    closeModal3();
  } else if (
    event.target == document.getElementById("cbtn4") ||
    event.target == document.getElementById("content4")
  ) {
    closeModal4();
  }
};

// handle file-upload
function handleFileSelect(event) {
  const files = event.target.files;
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (
      file.type === "application/vnd.ms-excel" ||
      file.type ===
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) {
      // Handle the selected Excel file(s) here
      console.log("Selected file:", file.name);
    } else {
      alert("Please select an Excel file");
    }
  }
}

function goDash() {
  window.location.pathname = "testapp/dashboard";
}

var donthaveaccount = document.getElementById("dhaa");
donthaveaccount.addEventListener("click", function () {
  closeModal2();
  openModal();
});

var anchortagLogin = document.getElementById("anchor_login");
anchortagLogin.addEventListener("click", function () {
  closeModal();
  openModal2();
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// -------------------For registration -----------------
var register_btn = document.getElementById("submitBtn");
register_btn.addEventListener("click", function (event) {
  event.preventDefault();

  var formData = {
    dept: document.querySelector("#dept").value,
    name: document.querySelector("#fullname").value,
    email: document.querySelector("#email").value,
    password: document.querySelector("#password").value
  };

  var pass2 = document.getElementById("cpassword");

  if (formData["password"] !== pass2.value) {
    document.getElementsByClassName("warn")[0].style.display = "block";
    document.querySelector("#submitBtn").style.marginTop = "0px";
    document.getElementsByClassName("warn")[0].textContent = "* Your password doesn't match!"
    pass2.focus();
  } else {
    // var url = window.location.host;
    const csrftoken = getCookie("csrftoken");
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/testapp/register/", true);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onload = function () {
      if (xhr.status === 200) {
        //reset the form
        document.querySelector("#register-form").reset();
        closeModal();
        openModal2();
      } else if (xhr.status === 409) {
        // focus on email
        document.querySelector("#email").focus();
      } else {
        // internal error
      }
      document.getElementsByClassName("warn")[0].textContent = JSON.parse(
        this.responseText
      )["message"];
      document.getElementsByClassName("warn")[0].style.display = "block";
      document.querySelector("#submitBtn").style.marginTop = "0px";
    };
    xhr.send(JSON.stringify(formData));
  }
});

// ----------------------For login-------------
var login_btn = document.getElementById("lsubmitBtn");
login_btn.addEventListener("click", function (event) {
  event.preventDefault();

  var formData = {
    uname: document.querySelector("#username").value,
    password: document.querySelector("#lpassword").value,
  };

  const csrftoken = getCookie("csrftoken");
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/testapp/login/", true);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);
  xhr.onload = function () {
    if (xhr.status === 401) {
      document.querySelector("#lpassword").focus();
    } else if (xhr.status === 404) {
      document.querySelector("#username").focus();
    } else if(xhr.status === 200){
      document.getElementsByClassName("loginWarn")[0].style.display = "none";
      document.querySelector("#lsubmitBtn").style.marginTop = "20px";
      var url = window.location.href;
      if (url.includes("testapp")){
        window.location="dashboard";
      } else{
        window.location="testapp/dashboard";
      }
    }
    document.getElementsByClassName("loginWarn")[0].textContent = JSON.parse(this.responseText)["message"];
    document.getElementsByClassName("loginWarn")[0].style.display = "block";
    document.querySelector("#lsubmitBtn").style.marginTop = "0px";
  };
  xhr.send(JSON.stringify(formData));
});



var check = document.querySelector("#prof span").textContent;
if (check !== "0") {
  document.getElementById("log_reg_btns").style.display = "none";
  document.getElementById("prof").style.display = "block";
}

