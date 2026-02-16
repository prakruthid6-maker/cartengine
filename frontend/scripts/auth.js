// Authentication utility functions

export function getUserSession() {
  const session = localStorage.getItem('userSession');
  return session ? JSON.parse(session) : null;
}

export function isLoggedIn() {
  return getUserSession() !== null;
}

export function isAdmin() {
  const session = getUserSession();
  return session && session.role === 'admin';
}

export function isUser() {
  const session = getUserSession();
  return session && session.role === 'user';
}

export function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = './login.html';
    return false;
  }
  return true;
}

export function logout() {
  localStorage.removeItem('userSession');
  window.location.href = './login.html';
}

export function getUsername() {
  const session = getUserSession();
  return session ? session.username : 'Guest';
}

export function getUserRole() {
  const session = getUserSession();
  return session ? session.role : null;
}
