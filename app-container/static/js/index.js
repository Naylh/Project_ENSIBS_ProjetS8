/*
    Function to send the file to the server
*/
document.getElementById("import_image").addEventListener("click", () => {
    let input_file = document.getElementById("input_file");

    if (!["png"].includes(input_file.files[0].name.split('.').pop())) {
        alert("Veuillez choisir un fichier de type png");
        return;
    }
    if (input_file.files.length === 0) {
        alert("Veuillez choisir un fichier");
        return;
    }
    if (input_file.files[0].size > 20000000) {
        console.log(input_file.files.size);
        alert("Fichier trop volumineux (20Mo max)");
        return;
    }

    let formData = new FormData();
    formData.append('input_file', input_file.files[0]);

    fetch("/uploadfile_index", {
        method: "POST",
        body: formData
    })
    .then(response => {
        response.json().then(data => console.log(data))
    });
});

/* 
    Function to send the passphrase to the server and create the unlock file
*/
document.getElementById("create_download_image").addEventListener("click", () => {
    let passphrase = document.getElementById("passphrase_file");
    
    if (passphrase.value === "") {
        alert("Veuillez entrer une passphrase");
        return;
    }

    let formData = new FormData();
    formData.append('passphrase_file', passphrase.value);

    alert("Attention cette action peut prendre plusieurs minutes");

    fetch("/createunlockfile_index", {
        method: "POST",
        body: formData
    })
    .then(response => {
        const disposition = response.headers.get('Content-Disposition');
        filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
        if (filename.toLowerCase().startsWith("utf-8''"))
            filename = decodeURIComponent(filename.replace("utf-8''", ''));
        else
            filename = filename.replace(/['"]/g, '');
        return response.blob();
    })
    .then(blob => {
        var imageUrl = window.URL.createObjectURL(blob);
        document.querySelector("#image").src = imageUrl;
    });
});

/*
    Function to download the unlock file
*/
document.getElementById("download_image").addEventListener("click", () => {
    fetch("/downloadfile_index", {
        method: "POST",
        headers: {
            'Accept': 'image/png',
            'Content-Type': 'image/png'
         }        
    })
    .then(response => {
        const disposition = response.headers.get('Content-Disposition');
        filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
        if (filename.toLowerCase().startsWith("utf-8''"))
            filename = decodeURIComponent(filename.replace("utf-8''", ''));
        else
            filename = filename.replace(/['"]/g, '');
        return response.blob();
    })
    .then(blob => {
        var imageUrl = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = imageUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
    });
});