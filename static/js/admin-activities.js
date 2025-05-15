// Admin Activities - Real-time activity tracking for admin dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize activity feed if we're on the admin dashboard
    if (document.getElementById('activity-feed')) {
        initializeActivityFeed();
        setupSocketListeners();
        setupClearActivitiesButton();
    }
});

// Initialize the activity feed by loading recent activities
function initializeActivityFeed() {
    fetch('/admin/activities')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching activities');
            }
            return response.json();
        })
        .then(data => {
            if (data.success || Array.isArray(data.activities)) {
                renderActivities(data.activities);
            } else {
                showNoActivitiesMessage();
            }
        })
        .catch(error => {
            console.error('Error loading activities:', error);
            showNoActivitiesMessage();
        });
}

// Render activities in the activity feed
function renderActivities(activities) {
    const activityFeed = document.getElementById('activity-feed');
    const noActivitiesMessage = document.getElementById('no-activities-message');
    
    // Clear the current activity feed
    activityFeed.innerHTML = '';
    
    // If there are no activities, show a message
    if (!activities || activities.length === 0) {
        noActivitiesMessage.style.display = 'block';
        activityFeed.appendChild(noActivitiesMessage);
        return;
    }
    
    // Hide the no activities message
    noActivitiesMessage.style.display = 'none';
    
    // Add activities to the feed
    activities.forEach(activity => {
        const activityItem = createActivityItem(activity);
        activityFeed.appendChild(activityItem);
    });
}

// Create an activity item element
function createActivityItem(activity) {
    const activityItem = document.createElement('div');
    activityItem.className = 'activity-item';
    
    const activityIcon = document.createElement('div');
    activityIcon.className = 'activity-icon';
    activityIcon.innerHTML = `<i class="fas ${activity.icon || 'fa-info-circle'}"></i>`;
    
    const activityContent = document.createElement('div');
    activityContent.className = 'activity-content';
    
    const activityTitle = document.createElement('div');
    activityTitle.className = 'activity-title';
    activityTitle.textContent = activity.title;
    
    const activityDescription = document.createElement('div');
    activityDescription.className = 'activity-description';
    activityDescription.innerHTML = activity.description;
    
    const activityTime = document.createElement('div');
    activityTime.className = 'activity-time';
    // Handle both function and property versions of time_ago
    if (typeof activity.time_ago === 'function') {
        activityTime.textContent = activity.time_ago();
    } else {
        activityTime.textContent = activity.time_ago || ''; 
    }
    
    activityContent.appendChild(activityTitle);
    activityContent.appendChild(activityDescription);
    activityContent.appendChild(activityTime);
    
    activityItem.appendChild(activityIcon);
    activityItem.appendChild(activityContent);
    
    return activityItem;
}

// Set up WebSocket listeners for real-time updates
function setupSocketListeners() {
    // Make sure socket.io is loaded
    if (typeof io === 'undefined') {
        console.error('Socket.IO not loaded');
        return;
    }
    
    // Connect with reconnection enabled and timeout increased
    const socket = io({
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 10,
        timeout: 20000
    });
    
    // Handle connection errors
    socket.on('connect_error', function(error) {
        console.error('Socket.IO connection error:', error);
    });
    
    // Handle disconnection
    socket.on('disconnect', function(reason) {
        console.log('Socket.IO disconnected:', reason);
        if (reason === 'io server disconnect') {
            // Reconnect if the server disconnected us
            socket.connect();
        }
    });
    
    // Listen for new activity events
    socket.on('new_activity', function(activityData) {
        // Convert activity_type to type for consistency
        const activity = activityData;
        if (activityData.activity_type && !activityData.type) {
            activity.type = activityData.activity_type;
        }
        // Get the activity feed
        const activityFeed = document.getElementById('activity-feed');
        const noActivitiesMessage = document.getElementById('no-activities-message');
        
        // Hide the no activities message if it's visible
        noActivitiesMessage.style.display = 'none';
        
        // Create the new activity item
        const activityItem = createActivityItem(activity);
        
        // Add the new activity to the top of the feed
        if (activityFeed.firstChild) {
            activityFeed.insertBefore(activityItem, activityFeed.firstChild);
        } else {
            activityFeed.appendChild(activityItem);
        }
        
        // Highlight the new activity
        setTimeout(() => {
            activityItem.classList.add('highlight');
            setTimeout(() => {
                activityItem.classList.remove('highlight');
            }, 2000);
        }, 100);
        
        // Trim the feed if it gets too long (keep the most recent 20)
        const activityItems = activityFeed.querySelectorAll('.activity-item');
        if (activityItems.length > 20) {
            for (let i = 20; i < activityItems.length; i++) {
                activityFeed.removeChild(activityItems[i]);
            }
        }
    });
    
    // Listen for activities cleared event
    socket.on('activities_cleared', function() {
        showNoActivitiesMessage();
    });
}

// Set up the clear activities button
function setupClearActivitiesButton() {
    const clearButton = document.getElementById('clearActivitiesBtn');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            // Confirm before clearing
            if (confirm('Are you sure you want to clear all activities?')) {
                clearActivities();
            }
        });
    }
}

// Clear all activities
function clearActivities() {
    fetch('/admin/activities/clear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error clearing activities');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNoActivitiesMessage();
        }
    })
    .catch(error => {
        console.error('Error clearing activities:', error);
        alert('An error occurred while clearing activities.');
    });
}

// Show the no activities message
function showNoActivitiesMessage() {
    const activityFeed = document.getElementById('activity-feed');
    const noActivitiesMessage = document.getElementById('no-activities-message');
    
    // Clear the current activity feed
    activityFeed.innerHTML = '';
    
    // Show the no activities message
    noActivitiesMessage.style.display = 'block';
    activityFeed.appendChild(noActivitiesMessage);
}

// Get CSRF token from the cookie
function getCSRFToken() {
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookies = decodedCookie.split(';');
    
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    
    return '';
}