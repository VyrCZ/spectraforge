const langs = ["en", "cz", "cn"];

async function setLanguage(lang) {
    // If the language is English, do nothing, as the page is already in English.
    const response = await fetch(`locales/${lang}.json`);
    const translations = await response.json();

    document.querySelectorAll("[lan-key]").forEach(elem => {
        const key = elem.getAttribute("lan-key");
        if (translations[key]) {
            elem.textContent = translations[key];
        }
    });
    document.cookie = `lang=${lang}; path=/`;
    const languageSelector = document.querySelector(".language-selector");
    if (languageSelector) {
        languageSelector.textContent = lang;
    }
}

function getLanguage(){
    let cookieValue = document.cookie.split('; ').find(row => row.startsWith('lang='));
    return cookieValue ? cookieValue.split('=')[1] : "en";
}

function changeLanguage(){
    console.log("Changing language");
    const currentLangIdx = langs.indexOf(getLanguage());
    const nextLangIdx = (currentLangIdx + 1) % langs.length;
    console.log(`Current language index: ${currentLangIdx}, Next language index: ${nextLangIdx}`);
    console.log(`Setting language to: ${langs[nextLangIdx]}`);
    setLanguage(langs[nextLangIdx]);
}

// Detect browser language or default to 'en'
const userLang = getLanguage();

// You can add a language switcher to let users change the language.
// For now, we'll just use the detected language.
// To test, you can manually set it: setLanguage("de");
setLanguage(userLang);