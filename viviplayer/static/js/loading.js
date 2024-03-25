function loadingShotsActivate(){
    const loadingDivs = document.getElementById("shots-loading");

    if(loadingDivs == null){
        return;
    }
    loadingDivs.classList.add("active");
}

function loadingShotsDeactivate(){
    const loadingDivs = document.getElementById("shots-loading");
    if(loadingDivs == null){
        return;
    }

    loadingDivs.classList.remove("active");
}