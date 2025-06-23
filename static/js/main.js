function toggleMenu() {
    const menu = document.getElementById("menu_container");
    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}

// Functions are called straight from the HTML