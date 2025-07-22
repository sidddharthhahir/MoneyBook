const usernameField = document.querySelector('#usernameField');
const feedBackArea = document.querySelector('.invalid_feedback');
const emailField = document.querySelector('#emailField');
const emailFeedBackArea = document.querySelector('.emailFeedBackArea');
const passwordField = document.querySelector('#passwordField');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn=document.querySelector(".submit-btn");
const handleToggleInput = (e) => {

    if(showPasswordToggle.textContent === 'SHOW') {
        showPasswordToggle.textContent = 'HIDE';
        passwordField.type = 'text';

        passwordField.setAttribute('type', 'text');
    } else {
        showPasswordToggle.textContent = 'SHOW';
        passwordField.type = 'password';
        passwordField.setAttribute('type', 'password');
    }
    
};
showPasswordToggle.addEventListener("click",handleToggleInput);
emailField.addEventListener("keyup", (e) => {
    console.log('7777', 7777);
    const emailVal = e.target.value;
   

    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = "none";

if (emailVal.length > 0) {
    fetch('/authentication/validate-email', {
        body: JSON.stringify({ email: emailVal }),
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
       
    })
    .then(res => res.json())
    .then(data => {
        console.log("data", data);
        if (data.email_error) {
            submitBtn.setAttribute('disabled',"disabled");
            submitBtn.disabled = true;
            emailField.classList.add("is-invalid");
            feedBackArea.style.display = "none";
            emailFeedBackArea.style.display = 'block';  
            emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
        } else {
            emailField.classList.remove("is-invalid");
            emailFeedBackArea.style.display = 'block'; 
            emailFeedBackArea.innerHTML = '';
            submitBtn.removeAttribute("disabled");
        }
    })
    
}
});

usernameField.addEventListener("keyup", (e) => {
    console.log('7777', 7777);
    const usernameVal = e.target.value;

    usernameSuccessOutput.style.display = 'block';

    usernameSuccessOutput.textContent=`Checking ${usernameVal}`;

    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = "block";

    if (usernameVal.length > 0) {
        fetch('/authentication/validate-username', {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
           
        })
        .then(res => {
            if (!res.ok) {
                throw new Error('Server error');
            }
            return res.json();
        })
        .then(data => {
            console.log("data", data);
            usernameSuccessOutput.style.display = 'none';
            if (data.username_error) {
                usernameField.classList.add("is-invalid");
                feedBackArea.computedStyleMap.display = "block";
                feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
                submitBtn.disabled = true;
            } else {
                usernameField.classList.remove("is-invalid");
                feedBackArea.innerHTML = '';
                submitBtn.removeAttribute("disabled");
                
                
            }
        })
        
    }
});
