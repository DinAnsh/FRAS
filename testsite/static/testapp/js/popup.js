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


window.onclick = function (event) {
  // console.log(event.target)
  if (
    event.target == document.getElementById("cbtn") ||
    event.target == document.getElementById("content") 
  ) {
    closeModal();
  }

  else if (event.target == document.getElementById("cbtn2") ||
  event.target == document.getElementById("content2")) {
    closeModal2();
  }
};
