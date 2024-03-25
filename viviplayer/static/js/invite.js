document.forms['sendMailForm'].addEventListener('submit', (event) => {
    event.preventDefault();
    fetch(window.location.origin + "/api" + window.location.pathname + "mail/", {
        method: 'POST',
        body: new URLSearchParams(new FormData(event.target)) // event.target is the form
    }).then((resp) => {
        if (resp.status != 200){
           resp.json().then(notifyUserOnPOST);
        }else{
            //TODO
            alert("Mails wurden versand.")
        }
    }).catch((error) => {
        console.log(error);
    });
});

// uses response of POST request and show msg from response
function notifyUserOnPOST(result) {
    
    var toastDiv = document.getElementById("error-toast");
    var toastBody = document.getElementById("error-toast-body");
    var errormsg = result.msg;
    toastBody.innerHTML = "Error: " + errormsg;

    var errorToast = new bootstrap.Toast(toastDiv);
    errorToast.show();

}

document.addEventListener("DOMContentLoaded", async function(){
    
    var response = await fetchAsync(window.location.origin + "/api/meeting/" + document.getElementById("GLOBAL_MEETING_NAME").value + "/info/");

    if(response){
        document.getElementById("invite_url").value = window.location.href + "join"
        document.getElementById("invite_pwd").value = response.password
    }
});

async function fetchAsync(url) {
    let response = await fetch(url);
    let data = await response.json();
    if(response.status != 200){
        alert(data.status)
        return 
    }else{
        console.log(data.status)
    }
    return data;
}