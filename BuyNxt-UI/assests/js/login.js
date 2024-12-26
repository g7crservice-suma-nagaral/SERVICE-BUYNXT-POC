// Login function
async function login() {
  debugger
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Input validation
    if (username === "") {
        showToast("Please enter username.", "warning");
        return;
    }
    if (password === "") {
        showToast("Please enter password.", "warning");
        return;
    }

    const obj = {
        username: username,
        password: password
    };
    const jsonreq = JSON.stringify(obj);

    try {
        const response = await fetch(`${API_URL}login`, {
            method: 'POST',
            body: jsonreq,
            headers: {
                'Content-type': 'application/json; charset=UTF-8'
            }
        });
        const responseData = await response.json();

        if (!response.ok) {
            showToast(responseData.message || "Error logging in", "error");
            return;
        }

        // Check for successful login
        if (responseData.success) {
            localStorage.setItem("session_id", responseData.authid); // Store session ID or token
            localStorage.setItem("userName", username)
            window.location.href = "index.html"; // Redirect to the dashboard
        } else {
            showToast(responseData.message, "error");
        }
    } catch (error) {
        showToast("An error occurred: " + error.message, "error");
    }
}


// Event listener for Enter key on password field
document.getElementById("password").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("btn_login").click(); // Trigger the login button click
    }
});



