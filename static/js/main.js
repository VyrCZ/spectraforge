function toggleMenu() {
    const menu = document.getElementById("menu_container");
    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const itemTags = document.querySelectorAll('.effect_tag');
    itemTags.forEach(element => {
        const tagText = element.textContent.trim();
        console.log(tagText);
        switch (tagText) {
            case "3D":
            case "3D Only":
                element.style.backgroundColor = "#f7ea36";
                break;
            case "2D":
            case "2D Only":
                element.style.backgroundColor = "#4577f7";
                break;
        }
    });
});
// Functions are called straight from the HTML