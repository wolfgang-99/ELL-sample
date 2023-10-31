
  (function ($) {
  
  "use strict";

    // MENU
    $('#sidebarMenu .nav-link').on('click',function(){
      $("#sidebarMenu").collapse('hide');
    });
    
    // CUSTOM LINK
    $('.smoothscroll').click(function(){
      var el = $(this).attr('href');
      var elWrapped = $(el);
      var header_height = $('.navbar').height();
  
      scrollToDiv(elWrapped,header_height);
      return false;
  
      function scrollToDiv(element,navheight){
        var offset = element.offset();
        var offsetTop = offset.top;
        var totalScroll = offsetTop-navheight;
  
        $('body,html').animate({
        scrollTop: totalScroll
        }, 300);
      }
    });
  
  })(window.jQuery);
document.getElementById("copyBtn").textContent = "copy";
document.getElementById("copyBtn").addEventListener("click", function(){
  //select text to copy
  var textToCopy = document.getElementById("Address");

  //create temp textarea element to hold text
  var textArea = document.createElement("textArea");
  textArea.value = textToCopy.innerHTML;

  //append textarea to the document
  document.body.appendChild(textArea);

  //select text in textarea
  textArea.select();

  //copy selected text to the clipboard
  document.execCommand("copy");

  //remove the temporary textarea
  document.body.replaceChild(textArea);

  //alert user
  document.getElementById("copyBtn").textContent = "copied";
});


// progress 

document.addEventListener("DOMContentLoaded", function(){
  const steps = document.querySelectorAll(".step");
  const stepForms = document.querySelectorAll(".step-form");
  let currentStep = 0;

  function updateProgress(){
      steps.forEach((step, index) => {
          if(index < currentStep){
              step.classList.add("active");
          } else {
              step.classList.remove("active");
          }
      });
  }
  function showStep(stepIndex){
      stepForms.forEach((form, index) => {
          if(index === stepIndex){
              form.classList.add("active");
              console.log("success");
          } else {
              form.classList.remove("active");
              console.log("failed");
          }
      });
  }

  showStep(currentStep);

  const nextBtn = document.getElementById("nextBtn");
  const nextBtn2 = document.getElementById("nextBtn2");
  const prevBtn = document.getElementById("prevBtn");
  const prevBtn2 = document.getElementById("prevBtn2");
  const withdrawalAmountInput = document.getElementById("withdrawalAmount");
  const displayAmount = document.getElementById("displayAmount");

  nextBtn.addEventListener("click", function () {
    if (currentStep === 0 && withdrawalAmountInput.value.trim() !== "") {
      displayAmount.textContent = withdrawalAmountInput.value;
    }
    currentStep++;
    updateProgress();
    showStep(currentStep);
  });

  nextBtn2.addEventListener("click", function(){
          currentStep++;
          updateProgress();
          showStep(currentStep);
      });

  prevBtn.addEventListener("click", function(){
      currentStep--;
      updateProgress();
      showStep(currentStep);
  });

  prevBtn2.addEventListener("click", function(){
      currentStep--;
      updateProgress();
      showStep(currentStep);
  });
})
