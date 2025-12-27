let userEmail = "";

async function sendCode() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const msg = document.getElementById("msg-login");
    const stepLogin = document.getElementById("step-login");
    const stepVerify = document.getElementById("step-verify");

    if (!email || !name) {
        msg.style.color = "#ef4444"; 
        msg.innerText = "Please fill in all fields.";
        return;
    }

    msg.style.color = "#fbbf24"; 
    msg.innerText = "Processing...";
    
    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, name: name })
        });
        
        const data = await response.json();

        if (data.success) {
            userEmail = email;
            stepLogin.style.display = "none";
            stepVerify.style.display = "block";
            msg.innerText = "";
        } else {
            msg.style.color = "#ef4444";
            msg.innerText = data.message;
        }
    } catch (e) {
        msg.style.color = "#ef4444";
        msg.innerText = "Connection Error";
    }
}

async function verifyCode() {
    const code = document.getElementById("code").value.trim();
    const msg = document.getElementById("msg-verify");

    if (!code) {
        msg.style.color = "#ef4444";
        msg.innerText = "Please enter the code.";
        return;
    }

    msg.style.color = "#fbbf24";
    msg.innerText = "Verifying...";

    try {
        const response = await fetch("/api/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: userEmail, code: code })
        });

        const data = await response.json();

        if (data.success) {
            msg.style.color = "#22c55e"; 
            msg.innerText = "Success! Redirecting...";
            
            setTimeout(() => {
                window.location.href = `/gradio/?user=${encodeURIComponent(userEmail)}`;
            }, 1000);
        } else {
            msg.style.color = "#ef4444";
            msg.innerText = "Incorrect code.";
        }
    } catch (e) {
        msg.style.color = "#ef4444";
        msg.innerText = "Connection Error";
    }
}