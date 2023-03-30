// Camera capture
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("capture-btn");
const retakeBtn = document.getElementById("retake-btn");
const saveBtn = document.getElementById("save-btn");

let stream;

// Capture image from video stream and display in canvas
captureBtn.addEventListener("click", () => {
  video.style.display = "none";
  canvas.style.display = "block";
  retakeBtn.style.display = "block";

  saveBtn.style.visibility = "visible";
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const tracks = stream.getTracks();
  tracks.forEach((track) => {
    track.stop();
  });
});
// video.srcObject = null;

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
  saveBtn.style.visibility = "hidden";
  retakeBtn.style.display = "none";
});

// for student face register
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

//Save Button
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
