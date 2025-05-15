// Admin Activities - Activity tracking for admin dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize activity feed if we're on the admin dashboard
    if (document.getElementById('activity-feed')) {
        initializeActivityFeed();
        setupPolling();
        setupClearActivitiesButton();
    }
});

// Initialize the activity feed by loading recent activities
function initializeActivityFeed() {
    loadActivities();
}

// Load activities from the server
function loadActivities() {
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

// Set up polling for activity updates
function setupPolling() {
    // Poll for new activities every 5 seconds
    setInterval(loadActivities, 5000);
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
    activityTime.textContent = activity.time_ago || '';
    
    activityContent.appendChild(activityTitle);
    activityContent.appendChild(activityDescription);
    activityContent.appendChild(activityTime);
    
    activityItem.appendChild(activityIcon);
    activityItem.appendChild(activityContent);
    
    return activityItem;
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
        // Reload activities after clearing
        loadActivities();
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