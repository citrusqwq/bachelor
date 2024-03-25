//Moderator only
//https://github.com/hellopyplane/Progress-bar

const uploadForm = document.getElementById('upload-form')
const input = document.getElementById('id_videofile')

const progressBox = document.getElementById('upload-progress-box')
const cancelBox = document.getElementById('upload-chancel-box')
const cancelBtn = document.getElementById('upload-chanel-btn')

const csrf = document.getElementsByName('csrfmiddlewaretoken')

input.addEventListener('change', ()=>{

    if(video){
        if (!confirm('Bei erneuten hochladen werden alle erarbeiteten Daten gelöscht.')){
            return
        }
    }

    progressBox.classList.remove('not-visible')
    cancelBox.classList.remove('not-visible')

    const video_data = input.files[0]
    const url = URL.createObjectURL(video_data)

    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('videofile', video_data)

    $.ajax({
        type:'POST',
        url: uploadForm.action,
        enctype: 'multipart/form-data',
        data: fd,
        xhr: function(){
            const xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener('progress', e=>{
                // console.log(e)
                if (e.lengthComputable) {
                    const percent = e.loaded / e.total * 100
                    //console.log(percent)
                    progressBox.innerHTML = `<div class="progress">
                                                <div class="progress-bar" role="progressbar" style="width: ${percent}%" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"></div>
                                            </div>
                                            <p>${percent.toFixed(1)}%</p>`
                }

            })
            cancelBtn.addEventListener('click', ()=>{
                xhr.abort()
                setTimeout(()=>{
                    uploadForm.reset()
                    progressBox.innerHTML=""
                    cancelBox.classList.add('not-visible')
                }, 2000)
            })
            return xhr
        },
        success: function(response){
            console.log(response)
            cancelBox.classList.add('not-visible')
        },
        error: function(error){
            console.log(error)
        },
        cache: false,
        contentType: false,
        processData: false,
    })
})
