// Function to handle sign-up process
document.getElementById("signup-form").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const username = document.getElementById("first-name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (username && email && password) {
        // Retrieve the current user data from localStorage, or create a new object if none exists
        let users = JSON.parse(localStorage.getItem("users")) || {};

        // Store the username and password as key-value pairs in the users dictionary
        users[email] = {
            username: username,
            password: password
        };

        // Save the updated users dictionary back to localStorage
        localStorage.setItem("users", JSON.stringify(users));

        alert("Sign-up successful! You can now sign in.");
        window.location.href = "signin.html";  // Redirect to sign-in page
    } else {
        alert("Please fill out all fields.");
    }
});

// Function to handle sign-in process
document.getElementById("login-form").addEventListener("submit", function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Retrieve the stored users data from localStorage
    let users = JSON.parse(localStorage.getItem("users"));

    // Check if the entered email exists and the password matches
    if (users && users[email] && users[email].password === password) {
        alert("Sign-in successful! Welcome, " + users[email].username);
        // Redirect to a welcome page or dashboard
        window.location.href = "welcome.html";
    } else {
        alert("Incorrect email or password. Please try again.");
    }
});
