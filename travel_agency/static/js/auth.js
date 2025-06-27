function loginUser(email, password) {
    $.ajax({
        url: '/api/login/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            email: email,
            password: password
        }),
        success: function(response) {
            // Store tokens (simplified - in a real app, use HttpOnly cookies)
            localStorage.setItem('access_token', response.access);
            localStorage.setItem('refresh_token', response.refresh);
            
            // Redirect or reload
            window.location.href = '/app/';
        },
        error: function(xhr) {
            $('#loginMessage').html('<div class="alert alert-danger">Invalid credentials</div>');
        }
    });
}

function logoutUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/app/login/';
}

// Add token to all AJAX requests
$.ajaxSetup({
    beforeSend: function(xhr) {
        const token = localStorage.getItem('access_token');
        if (token) {
            xhr.setRequestHeader('Authorization', 'Basic ' + token);
        }
    }
});

$(document).ready(function() {
    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');
    
    // Set up AJAX defaults
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || !(/^https:.*/.test(settings.url)))) {
                // Only send the token to relative URLs
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                
                // Add Authorization header if token exists
                const accessToken = localStorage.getItem('access_token') || 
                                    sessionStorage.getItem('access_token');
                if (accessToken) {
                    xhr.setRequestHeader("Authorization", `Bearer ${accessToken}`);
                }
            }
        }
    });
});


const Auth = {
    // Check authentication status
    checkAuth: async function() {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            return { isAuthenticated: false };
        }

        try {
            const response = await $.ajax({
                url: '/api/users/me/',
                type: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + accessToken
                }
            });
            
            return {
                isAuthenticated: true,
                user: response,
                accessToken: accessToken
            };
        } catch (error) {
            // Token is invalid or expired
            this.clearAuth();
            return { isAuthenticated: false };
        }
    },

    // Clear authentication
    clearAuth: function() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    // Redirect if not authenticated
    requireAuth: async function(redirectUrl = '/app/login/') {
        const auth = await this.checkAuth();
        if (!auth.isAuthenticated) {
            window.location.href = redirectUrl;
        }
        return auth;
    },

    // Update UI based on auth status
    updateAuthUI: async function() {
        const auth = await this.checkAuth();
        
        if (auth.isAuthenticated) {
            // Show authenticated elements
            $('.auth-only').show();
            $('.guest-only').hide();
            
            // Update user info
            if (auth.user) {
                $('.user-name').text(auth.user.username || '');
                $('.user-email').text(auth.user.email || '');
                
                if (auth.user.is_staff) {
                    $('.staff-only').show();
                }
            }
        } else {
            // Show guest elements
            $('.auth-only').hide();
            $('.guest-only').show();
        }
    }
};

// Make it available globally
window.Auth = Auth;