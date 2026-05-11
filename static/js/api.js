// static/js/api.js

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrfToken = getCookie('csrftoken');

const api = {
    async request(url, method, data = null) {
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Fetch it dynamically each time just in case
        };

        const options = {
            method: method,
            headers: headers,
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            // Check if it's a 204 No Content response
            if (response.status === 204) {
                return { success: true };
            }

            const responseData = await response.json();
            
            if (!response.ok) {
                // Return structured error object
                return { success: false, status: response.status, data: responseData };
            }
            
            return { success: true, status: response.status, data: responseData };
        } catch (error) {
            console.error('API Request Error:', error);
            return { success: false, status: 500, error: error.message };
        }
    },

    async get(url) {
        return this.request(url, 'GET');
    },

    async post(url, data) {
        return this.request(url, 'POST', data);
    },

    async put(url, data) {
        return this.request(url, 'PUT', data);
    },

    async patch(url, data) {
        return this.request(url, 'PATCH', data);
    },

    async delete(url) {
        return this.request(url, 'DELETE');
    }
};

window.api = api;
