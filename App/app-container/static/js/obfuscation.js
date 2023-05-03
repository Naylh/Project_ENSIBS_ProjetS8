const wordList = document.getElementById('word-list');
const roleList = document.getElementById('role-list');
const select = document.getElementById("role_select");
const list_role = [];
let list_role2 = [];
const dict_role_word = {};
let xStartToSend, yStartToSend, xEndToSend, yEndToSend;

/*
    Function allowing to update the options of a select
*/
function updateSelectOptions(select, list) {
    // Efface les options précédentes
    select.innerHTML = '';

    //Fais l'élément vide
    const option = document.createElement("option");
    select.add(option);
    
    // Ajoute les nouvelles options à partir de la liste
    list.forEach(item => {
        const option = document.createElement("option");
        option.text = item;
        select.add(option);
    });
}  

/*
    Function that removes the selected role from the role list
*/
function addRoleToList() {
    const selectedRole = select.value;
  
    if (selectedRole==="") {
        return;
    }

    //remove role from list_role2
    for (let i = 0; i < list_role2.length; i++) {
        if (list_role2[i] === selectedRole) {
            list_role2.splice(i, 1);
        }
    }
    //update the select
    updateSelectOptions(select, list_role2);
}

/*
    Function to import an image
*/
document.getElementById("import_image").addEventListener("click", () => {
    let input_file = document.getElementById("input_file");

    if (!["png","jpg","jpeg","pdf"].includes(input_file.files[0].name.split('.').pop())) {
        alert("Veuillez choisir un fichier de type png, jpg, jpeg ou pdf");
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

    fetch("/uploadfile_obfuscation", {
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
    Function to create a role and add it to the list
*/
document.getElementById("create_roles").addEventListener("click", () => {
    let roleInput = document.getElementById("roles_input");
    const newRole = roleInput.value.trim();

    if (newRole === "") {
        alert("Veuillez entrer un rôle");
        return;
    }

    let formData = new FormData();
    formData.append('roles_input', newRole);
    
    if (newRole){
        if (roleList.querySelectorAll('li').length > 0) {
            const roleListItems = roleList.querySelectorAll('li');
            for (let i = 0; i < roleListItems.length; i++) {
                if (roleListItems[i].textContent.slice(0, -1) === newRole) {
                    alert('Ce rôle existe déjà!');
                return;
              }
            }
        }
    }

    fetch("/createroles_obfuscation", {
        method: "POST",
        body: formData
    })    
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur lors de la création du rôle');
        }
        const li = document.createElement('li');
        li.textContent = newRole;
        const deleteButton = document.createElement('span');
        deleteButton.className = 'delete-role';
        deleteButton.classList.add('delete-role');
        deleteButton.textContent = '❌';
        li.appendChild(deleteButton);
        roleList.appendChild(li);
        roleInput.value = '';

        list_role.push(newRole);
        list_role2.push(newRole);
        updateSelectOptions(select, list_role);
    });
});


/*
    Function to remove a role from the list
*/
roleList.addEventListener('click', (event) => {
    if (event.target.classList.contains('delete-role')) {
        const role = event.target.previousSibling.textContent;

        let formData = new FormData();
        formData.append('role_name', role);
        
        fetch('/deleteroles_obfuscation', {
            method: 'POST',
            body: formData
        })
        .then(response => {
        if (!response.ok) {
            throw new Error('Erreur lors de la suppression du rôle');
        }
        })
        .catch(error => {
            console.error(error);
        });

        event.target.parentElement.remove();
        
        //delete role from list_role
        for (let i = 0; i < list_role.length; i++) {
            if (list_role[i] === role) {
                list_role.splice(i, 1);
            }
        }
        for (let i = 0; i < list_role2.length; i++) {
            if (list_role2[i] === role) {
                list_role2.splice(i, 1);
            }
        }
        updateSelectOptions(select, list_role);
    }
});


/*
    Function to add a word and add it to the list
*/
document.getElementById("create_words").addEventListener("click", () => {
    let wordInput = document.getElementById("words_input");
    const newWord = wordInput.value.trim();

    if (newWord === "") {
        alert("Veuillez entrer un mot");
        return;
    }

    //compare list_role and list_role2 for each role which is in list_role but not in list_role2 add it as a value in the dict and the key is the word
    let list_role3 = [];
    for (let i = 0; i < list_role.length; i++) {
        if (list_role2.includes(list_role[i]) === false) {
            list_role3.push(list_role[i]);
        }
    }

    //check if newWord is already a key in dict_role_word
    if (newWord in dict_role_word) {
        dict_role_word[newWord].push([list_role3,[xStartToSend,yStartToSend],[xEndToSend,yEndToSend]])
    }   
    else {
        dict_role_word[newWord] = [[list_role3,[xStartToSend,yStartToSend],[xEndToSend,yEndToSend]]];
    }

    let formData = new FormData();
    formData.append('words_input', JSON.stringify(dict_role_word));

    fetch("/createwords_obfuscation", {
        method: "POST",
        body: formData
    })    
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur lors de la création du mot');
        }
        //get the list of roles and convert it to a string
        let list_role_string = "";
        for (let i = 0; i < list_role3.length; i++) {
            list_role_string += list_role3[i] + ", ";
        }
        list_role_string = list_role_string.slice(0, -2);

        const li = document.createElement('li');
        li.textContent = newWord + '{' + list_role_string + '}';
        const deleteButton = document.createElement('span');
        deleteButton.className = 'delete-word';
        deleteButton.classList.add('delete-word');
        deleteButton.textContent = '❌';
        li.appendChild(deleteButton);
        wordList.appendChild(li);
        wordInput.value = '';

        list_role2 = [];
        for (let i = 0; i < list_role.length; i++) {
            list_role2.push(list_role[i]);
        }
        updateSelectOptions(select, list_role);
    });
    document.getElementById("words_div").style.display = "none";
});


/*
    Function to delete a word from the list
*/
wordList.addEventListener('click', (event) => {
    if (event.target.classList.contains('delete-word')) {
        const word = event.target.previousSibling.textContent;

        let formData = new FormData();
        formData.append('word_name', word);

        fetch('/deletewords_obfuscation', {
            method: 'POST',
            body: formData
        })
        .then(response => {
        if (!response.ok) {
            throw new Error('Erreur lors de la suppression du mot');
        }
        })
        .catch(error => {
            console.error(error);
        });

        event.target.parentElement.remove();
        let word_key = word.split('{')[0];
        delete dict_role_word[word_key];
    }
});


/*
    Function to download the file
*/
document.getElementById("download_image").addEventListener("click", () => {
    fetch("/downloadfile_obfuscation", {
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

        // Extract the list of roles from the filename
        const queryParams = new URLSearchParams(filename.split('?')[1]);
        const list_hash_json = queryParams.get('list_hash');
        // Add double quotes around keys
        jsonString = list_hash_json.replace(/(\w+):/g, '"$1":');

        // Add double quotes around values
        jsonString = list_hash_json.replace(/(\b\w+\b)/g, '"$1"');
        const obj = JSON.parse(jsonString);
        alerte = 'Voici les clés de déchiffrement pour chaque rôle notez les biens ou elles seront perdues : \n';
        // For all the keys of the obj we display the role and the key
        for (let key in obj) {
            alerte += key + ' : ' + obj[key] + '\n';
        }
        alert(alerte);

        return response.blob();
    })
    .then(blob => {
        var imageUrl = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = imageUrl;
        a.download = filename.split('?')[0];
        document.body.appendChild(a);
        a.click();
        a.remove();
    });
    //afficher les passphrases pour unlock
});


/*
    Function to retrieve the coordinates of the click on the image
*/
document.getElementById("image").addEventListener("mousedown", (event) => {
    // Retrieve click event coordinates
    const xStart = event.offsetX;
    const yStart = event.offsetY;

    // Prevent image selection when moving mouse
    event.preventDefault();
    
    // Get image size
    const img = event.target;
    const imgWidthReal = img.naturalWidth;
    const imgHeightReal = img.naturalHeight;
    const imgWidthClient = img.clientWidth;
    const imgHeightClient = img.clientHeight;

    xStartToSend = parseInt(xStart * imgWidthReal / imgWidthClient);
    yStartToSend = parseInt(yStart * imgHeightReal / imgHeightClient);
});

/*
    Function to retrieve the coordinates of the click on the image and display the "words_div" div next to it
*/
document.getElementById("image").addEventListener("mouseup", (event) => {
    // Retrieve coordinates from click release event
    const xEnd = event.offsetX;
    const yEnd = event.offsetY;
    
    // Convert coordinates taking into account the (0,0) at the bottom left
    const img = event.target;
    const imgWidthReal = img.naturalWidth;
    const imgHeightReal = img.naturalHeight;
    const imgWidthClient = img.clientWidth;
    const imgHeightClient = img.clientHeight;
    
    xEndToSend = parseInt(xEnd * imgWidthReal / imgWidthClient);
    yEndToSend = parseInt(yEnd * imgHeightReal / imgHeightClient);

    const wordsDiv = document.getElementById("words_div");
    // Defining the CSS styles of the div
    wordsDiv.style.position = "absolute";
    wordsDiv.style.display = "block";
    wordsDiv.style.top = img.offsetTop + yEnd + "px";
    wordsDiv.style.left = img.offsetLeft + xEnd + "px";
});

/*
    Function to hide the "words_div" div when clicking outside of it
*/
document.addEventListener("click", (event) => {
    const wordsDiv = document.getElementById("words_div");
    const imageDiv = document.getElementById("image_div");
    if (!wordsDiv.contains(event.target) && !imageDiv.contains(event.target)) {
      wordsDiv.style.display = "none";
    }
});