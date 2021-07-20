function deleteNote(noteId){
    // javascrip 发送表单 delete
    fetch('/delete-note',{
        method:'POST',
        body:JSON.stringify({noteId:noteId})
    }).then((_res)=>{
        window.location.href="/";
    })
}
function likeNote(noteId){
    // like note
    fetch('/like-note',{
        method:'POST',
        body:JSON.stringify({noteId:noteId})
    }).then((_res)=>{
        location.reload()
    })
}