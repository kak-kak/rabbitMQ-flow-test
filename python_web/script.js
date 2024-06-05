function rotateArrow(direction) {
    const arrow = document.getElementById('arrow');
    arrow.style.transform = `translate(-50%, -100%) rotate(${direction}deg)`;
}

// Example: Rotate arrow to 90 degrees
rotateArrow(90);

// If you want to change the direction dynamically, you can use this function with any direction value (0-360)
