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
        if (tagText.includes("2D")){
            element.classList.add('tag_2d');
        }
        else if (tagText.includes("3D")){
            element.classList.add('tag_3d');
        }
        else{
            element.classList.add('tag_other');
        }
    });
});
// Functions are called straight from the HTML