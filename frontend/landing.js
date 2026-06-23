const text =
"Hi! I'm Lumina 👋";

let i = 0;

function typeText() {

    if (i < text.length) {

        document.getElementById(
            "typing-text"
        ).innerHTML += text.charAt(i);

        i++;

        setTimeout(
            typeText,
            100
        );
    }
}

window.onload = typeText;