function showprofile() {
  document.getElementById("profile-popup").style.display = "block";
}

function closeProfile() {
  document.getElementById("profile-popup").style.display = "none";
}

function handleChange() {
  const passwordInput = document.getElementById("new-password");
  const confirmPasswordInput = document.getElementById("confirm-password");
  const updateBtn = document.getElementById("update-btn");

  if (passwordInput.value !== "" && confirmPasswordInput.value !== "") {
    if (passwordInput.value === confirmPasswordInput.value) {
      updateBtn.style.display = "block";
    } else {
      alert("Confirm the new password correctly!");
      updateBtn.style.display = "none";
    }
  }
}

var closebtn = document.querySelector(".home-icon02");
closebtn.addEventListener("click", () => {
  document.querySelector(".home-mobile-menu").style.display = "none";
});

var burgerbtn = document.querySelector(".home-burger-menu");
burgerbtn.addEventListener("click", () => {
  document.querySelector(".home-mobile-menu").style.display = "block";
});


function resetRecords(){
  document.querySelector('.confirmation').style.display = 'block';
}

function closeReset(){
  document.querySelector('.confirmation').style.display = 'none';
}