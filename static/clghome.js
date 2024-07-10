var slideIndex = 0;
showSlides();

function showSlides() {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) { slideIndex = 1 }
    slides[slideIndex - 1].style.display = "block";
    setTimeout(showSlides, 5000); // Change slide every 2 seconds
}

// Manual control functions
function plusSlides(n) {
    showSlides(slideIndex += n);
}

let achievementsSlideIndex = 0;
showAchievementsSlides();

function showAchievementsSlides() {
    let achievementsSlides = document.getElementsByClassName("slide");
    for (let i = 0; i < achievementsSlides.length; i++) {
        achievementsSlides[i].style.display = "none";
    }
    achievementsSlideIndex++;
    if (achievementsSlideIndex > achievementsSlides.length) {
        achievementsSlideIndex = 1;
    }
    achievementsSlides[achievementsSlideIndex - 1].style.display = "block";
    setTimeout(showAchievementsSlides, 7000); // Change achievements slide every 3 seconds (adjust as needed)
}

// ... (other JavaScript functions remain unchanged) ...
