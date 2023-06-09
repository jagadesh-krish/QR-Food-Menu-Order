function changeToForm(){
    var myElement = document.getElementById("myElement");
    var myElement_content = myElement.textContent;
    var id_number = myElement_content.match(/\d+/);

    var form = document.createElement("form");
    form.setAttribute("id", "myForm");
    form.setAttribute("method" , "post");
    form.setAttribute("action", "/submit/".concat(id_number[0]));
    var textArea = document.createElement("textarea");
    textArea.setAttribute("name", "review_area");
    textArea.setAttribute("placeholder", "Feedback - ".concat(id_number[0]));
    var submitButton = document.createElement("input");
    submitButton.setAttribute("type", "submit");
    form.appendChild(textArea);
    form.appendChild(submitButton);
    myElement.parentNode.replaceChild(form, myElement);
}


