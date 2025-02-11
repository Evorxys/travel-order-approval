document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loader = document.querySelector('.loader-container');
    
    try {
        loader.style.display = 'flex';  // Show loader
        
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const result = await response.json();
            window.location.href = result.redirect;
        } else {
            const data = await response.json();
            document.getElementById('errorMessage').textContent = data.message;
        }
    } catch (error) {
        document.getElementById('errorMessage').textContent = 'An error occurred. Please try again.';
    } finally {
        loader.style.display = 'none';  // Hide loader
    }
});
