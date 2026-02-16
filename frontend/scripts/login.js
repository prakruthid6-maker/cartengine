// Demo credentials
const CREDENTIALS = {
  admin: { username: 'admin', password: 'admin123', role: 'admin' },
  user: { username: 'user', password: 'user123', role: 'user' }
};

document.getElementById('loginForm').addEventListener('submit', (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const role = document.getElementById('role').value;
  
  // Remove any existing error message
  const existingError = document.querySelector('.error-message');
  if (existingError) existingError.remove();
  
  // Validate credentials
  const validUser = Object.values(CREDENTIALS).find(
    cred => cred.username === username && cred.password === password && cred.role === role
  );
  
  if (validUser) {
    // Store user session
    const userSession = {
      username: validUser.username,
      role: validUser.role,
      loginTime: new Date().toISOString()
    };
    
    localStorage.setItem('userSession', JSON.stringify(userSession));
    
    // Show success and redirect
    showSuccess(`Welcome ${role === 'admin' ? 'Administrator' : 'Customer'}!`);
    
    setTimeout(() => {
      window.location.href = './index.html';
    }, 1000);
  } else {
    // Show error
    showError('Invalid username, password, or role. Please check the demo credentials.');
  }
});

function showError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message show';
  errorDiv.innerHTML = `<i class="fa-solid fa-exclamation-circle"></i> ${message}`;
  
  const form = document.getElementById('loginForm');
  form.insertBefore(errorDiv, form.firstChild);
}

function showSuccess(message) {
  const successDiv = document.createElement('div');
  successDiv.className = 'error-message show';
  successDiv.style.background = '#d4edda';
  successDiv.style.color = '#155724';
  successDiv.innerHTML = `<i class="fa-solid fa-check-circle"></i> ${message}`;
  
  const form = document.getElementById('loginForm');
  form.insertBefore(successDiv, form.firstChild);
}

// Check if already logged in
const session = localStorage.getItem('userSession');
if (session) {
  window.location.href = './index.html';
}
