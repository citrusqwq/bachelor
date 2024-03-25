//Moderator only

/**
 * Can be used across muliple HTML files.
 * input needs id invite_url
 * button needs id invite_url_button
 */
function copyUrl(){
    var data = document.getElementById("invite_url").value;
    if (navigator.clipboard && window.isSecureContext){
        navigator.clipboard.writeText(data)
        var button = document.getElementById("invite_url_button");
        button.classList.remove("btn-outline-primary");
        button.classList.remove("btn-primary")
        button.classList.add("btn-outline-success");
        button.innerHTML = "Kopiert";
    } else {
        createErrorToastOverwrite("Die Operation ist leider fehlgeschlagen. Bitte kopieren Sie den Text mit Strg+C.")
    }           
}

/**
 * Can be used across muliple HTML files.
 * input needs id invite_pwd
 * button needs id invite_pwd_button
 */
function copyPwd(){
    var data = document.getElementById("invite_pwd").value;
    if (navigator.clipboard && window.isSecureContext){
        navigator.clipboard.writeText(data)
        var button = document.getElementById("invite_pwd_button");
        button.classList.remove("btn-outline-primary");
        button.classList.remove("btn-primary")
        button.classList.add("btn-outline-success");
        button.innerHTML = "Kopiert";
    } else {
        createErrorToastOverwrite("Die Operation ist leider fehlgeschlagen. Bitte kopieren Sie den Text mit Strg+C.")
    }           
}
