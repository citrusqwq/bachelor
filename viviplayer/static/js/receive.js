//for MODERATOR and USER

socket.onmessage = function (e) {
    var recv = JSON.parse(e.data)
    console.log("From Backend: ", recv);

    if (recv.cmd == "error") {
        createErrorToast(recv.data[0]);
        return;
        
    }

    switch (recv.type) {
        //recv.data ist ein array der empfangenen daten
        case "video":
            videoOnMessage(recv);
            break;
        case "shot":
            if (recv.cmd == "export") {
                saveExportData(recv.data, 'shot');
            } else if (recv.cmd == "new" && recv.data.length != 0) {
                shotsOnMessage(recv);
            }
            break;
        case "userstory":
            if (recv.cmd == "export") {
                saveExportData(recv.data, 'userstory');
            }
            if (recv.cmd == "new" || recv.cmd == "update" || recv.cmd == "del") {
                UserStoryOnMessage(recv)
            }
            break;
        case "satz":
            if (recv.cmd == "export") {
                saveExportData(recv.data, 'satz');
            }
            if (recv.cmd == "new" || recv.cmd == "update" || recv.cmd == "del") {
                SatzOnMessage(recv);
            }
            break;
        case "control":
            if (recv.cmd == "end") {
                window.location.href += "end"
            } else if (recv.cmd == "reload") {
                location.reload()
            } else if (recv.cmd == "loadShot") {
                if (recv.data) {
                    loadingShotsActivate();
                }else{
                    loadingShotsDeactivate();
                }
            } 
            break;
        case "poll":
            ListUmfrageOnMessage(recv);
            if (recv.cmd == "new") {
                umfrageOnMessage(recv);
            }
            else if (recv.cmd == "result"){
                umfrageResultMod(recv);
            }
            else if (recv.cmd == "close"){
                umfrageHide();
            }
            break;
        case "annotation":
            if(recv.cmd == "new" || recv.cmd == "update"){
                annosOnMessage(recv);
            }
            else if (recv.cmd == "del"){
                annosOnDeleteMessage(recv);
            }
            break;
        default:
            console.log("unknown type from backend");
    }
}

/**
 * Creates a new Error Toast in a list.
 * @param {String} message 
 */
function createErrorToast(message) {

    var toastContainer = document.getElementById("error-container");

    var toastDiv = document.createElement("div");
    toastContainer.append(toastDiv);
    toastDiv.className = "toast align-items-center bg-danger text-white border-0";
    toastDiv.setAttribute("role", "alert");
    toastDiv.setAttribute("aria-live", "assertive");
    toastDiv.setAttribute("aria-atomic", "true");
    toastDiv.setAttribute("data-bs-autohide", "false")

    var toastFlex = document.createElement("div");
    toastDiv.append(toastFlex);
    toastFlex.className = "d-flex";

    var toastBody = document.createElement("div");
    toastFlex.append(toastBody);
    toastBody.className = "toast-body";
    toastBody.innerHTML = "Error: " + message;

    var closeButton = document.createElement("button");
    toastFlex.append(closeButton);
    closeButton.type = "button";
    closeButton.className = "btn-close btn-close-white me-2 m-auto";
    closeButton.setAttribute("data-bs-dismiss", "toast");
    closeButton.setAttribute("aria-label", "Close");


    var errorToast = new bootstrap.Toast(toastDiv);
    errorToast.show();

}

/**
 * This is the first/own error toast. Doesn't overwrite the error toasts created with createErrorToast().
 * But it overwrites messages created with this function createErrorToastOverwrite().
 * This should be used for short and not so important messages, like clipboard failed.
 * @param {string} message 
 */
 function createErrorToastOverwrite(message) {

    var toastDiv = document.getElementById("error-toast");
    var toastBody = document.getElementById("error-toast-body");
    var errormsg = message;
    toastBody.innerHTML = "Error: " + errormsg;

    var errorToast = new bootstrap.Toast(toastDiv);
    errorToast.show();
}
