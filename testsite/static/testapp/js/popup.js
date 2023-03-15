function openModal() {
    document.getElementById("myModal").style.display = "block";
  }
  
  function closeModal() {
    document.getElementById("myModal").style.display = "none";
  }
  
  window.onclick = function(event) {
    // console.log(event.target)
    if (event.target == document.getElementById("cbtn") || event.target == document.getElementById("content")){
      closeModal();
    }
  }
  