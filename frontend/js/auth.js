document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const toggleAuth = document.getElementById('toggle-auth');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const usernameGroup = document.getElementById('username-group');
    const authBtn = document.getElementById('auth-btn');
    const toggleText = document.getElementById('toggle-text');
    const forgotPassword = document.getElementById('forgot-password');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const authError = document.getElementById('auth-error');

    let isLoginMode = true;
    const API_BASE_URL = 'http://localhost:8000'; // Adjust if backend is hosted elsewhere

    toggleAuth.addEventListener('click', (e) => {
        e.preventDefault();
        isLoginMode = !isLoginMode;
        
        authError.classList.add('hidden');
        authForm.reset();

        if (isLoginMode) {
            authTitle.textContent = 'Welcome Back';
            authSubtitle.textContent = 'Login to continue your preparation';
            usernameGroup.classList.add('hidden');
            usernameInput.removeAttribute('required');
            authBtn.textContent = 'Login';
            toggleText.innerHTML = 'Don\'t have an account? <a href="#" id="toggle-auth">Sign up</a>';
            forgotPassword.style.display = 'block';
        } else {
            authTitle.textContent = 'Create an Account';
            authSubtitle.textContent = 'Sign up to start your journey';
            usernameGroup.classList.remove('hidden');
            usernameInput.setAttribute('required', 'true');
            authBtn.textContent = 'Sign Up';
            toggleText.innerHTML = 'Already have an account? <a href="#" id="toggle-auth">Login</a>';
            forgotPassword.style.display = 'none';
        }

        // Re-attach listener since toggleText innerHTML was overwritten
        document.getElementById('toggle-auth').addEventListener('click', toggleAuth.onclick || function(ev) {
            ev.preventDefault();
            toggleAuth.click();
        });
    });

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        authBtn.disabled = true;
        authBtn.textContent = 'Processing...';
        authError.classList.add('hidden');

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        const username = usernameInput.value.trim();

        try {
            const endpoint = isLoginMode ? '/login' : '/register';
            const payload = isLoginMode 
                ? { email, password } 
                : { username, email, password };

            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Authentication failed');
            }

            // Save user details to localStorage for access across the app
            localStorage.setItem('user_id', data.user_id || data.id); // Login returns user_id, Register returns id
            localStorage.setItem('username', data.username);
            
            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        } catch (error) {
            authError.textContent = error.message;
            authError.classList.remove('hidden');
        } finally {
            authBtn.disabled = false;
            authBtn.textContent = isLoginMode ? 'Login' : 'Sign Up';
        }
    });
});
