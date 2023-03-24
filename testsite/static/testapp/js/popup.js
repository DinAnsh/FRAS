// for registration
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
  if (
    event.target == document.getElementById("cbtn") 
  ) {
    closeModal();
  } else if (
    event.target == document.getElementById("cbtn2")
  ) {
    closeModal2();
  }
  else if (
    event.target == document.getElementById("cbtn3") ||
    event.target == document.getElementById("content3")
  ) {
    const tracks = stream.getTracks();
    tracks.forEach((track) => {
      track.stop();
    });
    video.srcObject = null;
    closeModal3();
  }


  else if (
    event.target == document.getElementById("cbtn4") ||
    event.target == document.getElementById("content4")
  ) {
    closeModal4();
  }
};


function handleFileSelect(event) {
  const files = event.target.files;
  for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.type === 'application/vnd.ms-excel' || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
          // Handle the selected Excel file(s) here
          console.log('Selected file:', file.name);
      } else {
          alert('Please select an Excel file');
      }
  }
}

function goDash(){
  window.location.pathname = "testapp/dashboard";
}