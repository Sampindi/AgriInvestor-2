// Dashboard.js - Enhanced dashboard visualizations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts and dashboard components
    initializeCharts();
    // Disabled animations per user request
    // initializeAnimations();
    // initializeDashboardCards();
});

// Initialize Chart.js visualizations
function initializeCharts() {
    // Only initialize if Chart.js is loaded and we have canvas elements
    if (typeof Chart === 'undefined') {
        console.log('Chart.js not loaded');
        loadChartJsScript();
        return;
    }

    // Set global chart options for a futuristic look
    Chart.defaults.color = '#94A1B2';
    Chart.defaults.font.family = "'Montserrat', 'Segoe UI', sans-serif";
    
    // Disable all animations globally
    Chart.defaults.animation = false;
    Chart.defaults.animations = false;
    
    // Initialize various chart types depending on the dashboard
    initializeAdminCharts();
    initializeInvestorCharts();
    initializeFarmerCharts();
}

// Load Chart.js dynamically if not already available
function loadChartJsScript() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = initializeCharts;
    document.head.appendChild(script);
}

// Admin dashboard charts
function initializeAdminCharts() {
    // User Growth Chart (Admin Dashboard)
    const userGrowthCanvas = document.getElementById('userGrowthChart');
    if (userGrowthCanvas) {
        const ctx = userGrowthCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: userGrowthLabels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Farmers',
                    data: farmerGrowthData || [12, 19, 25, 30, 35, 38],
                    borderColor: '#2CB67D',
                    backgroundColor: 'rgba(44, 182, 125, 0.2)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Investors',
                    data: investorGrowthData || [5, 10, 15, 20, 25, 27],
                    borderColor: '#7F5AF0',
                    backgroundColor: 'rgba(127, 90, 240, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'User Growth',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(36, 38, 41, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                animations: false
            }
        });
    }

    // Funding Distribution Chart (Admin Dashboard)
    const fundingDistCanvas = document.getElementById('fundingDistributionChart');
    if (fundingDistCanvas) {
        const ctx = fundingDistCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: fundingCategoryLabels || ['Equipment', 'Expansion', 'Technology', 'Infrastructure', 'Organic Transition', 'Startup'],
                datasets: [{
                    data: fundingCategoryData || [30, 25, 15, 10, 10, 10],
                    backgroundColor: [
                        '#2CB67D', // Primary
                        '#7F5AF0', // Secondary
                        '#FF8906', // Accent
                        '#4EA8DE', // Info
                        '#F9C846', // Warning
                        '#E53170'  // Danger
                    ],
                    borderColor: 'rgba(22, 22, 26, 0.8)',
                    borderWidth: 3,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Funding Distribution by Category',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(36, 38, 41, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.formattedValue;
                                return `${label}: ${value}%`;
                            }
                        }
                    }
                },
                cutout: '65%',
                animation: false
            }
        });
    }

    // Project Status Chart (Admin Dashboard)
    const projectStatusCanvas = document.getElementById('projectStatusChart');
    if (projectStatusCanvas) {
        const ctx = projectStatusCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Active', 'Funded', 'Expired'],
                datasets: [{
                    data: projectStatusData || [60, 30, 10],
                    backgroundColor: [
                        '#4EA8DE', // Info
                        '#2CB67D', // Success
                        '#E53170'  // Danger
                    ],
                    borderColor: 'rgba(22, 22, 26, 0.8)',
                    borderWidth: 3,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Project Status Distribution',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(36, 38, 41, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                animation: false
            }
        });
    }
}

// Investor dashboard charts
function initializeInvestorCharts() {
    // Investment Performance Chart (Investor Dashboard)
    const investmentPerformanceCanvas = document.getElementById('investmentPerformanceChart');
    if (investmentPerformanceCanvas) {
        const ctx = investmentPerformanceCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: investmentProjectLabels || ['Project A', 'Project B', 'Project C', 'Project D', 'Project E'],
                datasets: [{
                    label: 'Amount Invested ($)',
                    data: investmentAmountData || [5000, 7500, 3000, 10000, 8000],
                    backgroundColor: 'rgba(44, 182, 125, 0.7)',
                    borderColor: '#2CB67D',
                    borderWidth: 2,
                    borderRadius: 5,
                    barPercentage: 0.6
                }, {
                    label: 'Project Funding Goal ($)',
                    data: investmentGoalData || [10000, 15000, 5000, 20000, 12000],
                    backgroundColor: 'rgba(127, 90, 240, 0.3)',
                    borderColor: '#7F5AF0',
                    borderWidth: 2,
                    borderRadius: 5,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Investment Performance',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(36, 38, 41, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        title: {
                            display: true,
                            text: 'Amount ($)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                },
                animations: {
                    y: {
                        duration: 2000,
                        delay: function(context) {
                            return context.dataIndex * 100;
                        }
                    }
                }
            }
        });
    }

    // Investment Category Distribution (Investor Dashboard)
    const investmentCategoryCanvas = document.getElementById('investmentCategoryChart');
    if (investmentCategoryCanvas) {
        const ctx = investmentCategoryCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: investmentCategoryLabels || ['Equipment', 'Expansion', 'Technology', 'Infrastructure', 'Organic'],
                datasets: [{
                    data: investmentCategoryData || [15, 30, 25, 10, 20],
                    backgroundColor: [
                        'rgba(44, 182, 125, 0.7)',   // Primary
                        'rgba(127, 90, 240, 0.7)',   // Secondary
                        'rgba(255, 137, 6, 0.7)',    // Accent
                        'rgba(78, 168, 222, 0.7)',   // Info
                        'rgba(249, 200, 70, 0.7)'    // Warning
                    ],
                    borderColor: [
                        '#2CB67D',
                        '#7F5AF0',
                        '#FF8906',
                        '#4EA8DE',
                        '#F9C846'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Investment Category Distribution',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(36, 38, 41, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            backdropColor: 'rgba(22, 22, 26, 0.8)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            }
        });
    }
}

// Farmer dashboard charts
function initializeFarmerCharts() {
    // Project Funding Progress Chart (Farmer Dashboard)
    const fundingProgressCanvas = document.getElementById('fundingProgressChart');
    if (fundingProgressCanvas) {
        const ctx = fundingProgressCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: projectTitleLabels || ['Project 1', 'Project 2', 'Project 3'],
                datasets: [{
                    label: 'Current Funding',
                    data: currentFundingData || [8000, 5000, 3000],
                    backgroundColor: 'rgba(44, 182, 125, 0.7)',
                    borderColor: '#2CB67D',
                    borderWidth: 2,
                    borderRadius: 5,
                    barPercentage: 0.6
                }, {
                    label: 'Funding Goal',
                    data: fundingGoalData || [10000, 15000, 12000],
                    backgroundColor: 'rgba(127, 90, 240, 0.3)',
                    borderColor: '#7F5AF0',
                    borderWidth: 2,
                    borderRadius: 5,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Project Funding Progress',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(36, 38, 41, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        title: {
                            display: true,
                            text: 'Amount ($)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                },
                animations: {
                    y: {
                        duration: 2000,
                        delay: function(context) {
                            return context.dataIndex * 100;
                        }
                    }
                }
            }
        });
    }

    // Investor Interest Chart (Farmer Dashboard)
    const investorInterestCanvas = document.getElementById('investorInterestChart');
    if (investorInterestCanvas) {
        const ctx = investorInterestCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Sustainable Agriculture', 'Organic Farming', 'Technology', 'Livestock', 'Crops', 'Processing'],
                datasets: [{
                    label: 'Connected Investors',
                    data: investorInterestData || [90, 80, 70, 60, 85, 55],
                    backgroundColor: 'rgba(44, 182, 125, 0.3)',
                    borderColor: '#2CB67D',
                    borderWidth: 2,
                    pointBackgroundColor: '#2CB67D',
                    pointBorderColor: '#FFFFFE',
                    pointHoverBackgroundColor: '#FFFFFE',
                    pointHoverBorderColor: '#2CB67D',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Investor Interest Areas',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(36, 38, 41, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            backdropColor: 'rgba(22, 22, 26, 0.8)'
                        },
                        pointLabels: {
                            font: {
                                size: 12
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            }
        });
    }
}

// Initialize animations for the dashboard
function initializeAnimations() {
    // Add pulsing effect to stats cards
    const statsCards = document.querySelectorAll('.stats-card');
    statsCards.forEach(card => {
        card.classList.add('pulse-on-hover');
    });

    // Add bubble effect to dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach(card => {
        // Create bubble elements
        for (let i = 0; i < 5; i++) {
            const bubble = document.createElement('div');
            bubble.className = 'dashboard-bubble';
            bubble.style.left = `${Math.random() * 100}%`;
            bubble.style.top = `${Math.random() * 100}%`;
            bubble.style.width = `${Math.random() * 50 + 10}px`;
            bubble.style.height = bubble.style.width;
            bubble.style.animationDelay = `${Math.random() * 5}s`;
            bubble.style.animationDuration = `${Math.random() * 10 + 5}s`;
            card.appendChild(bubble);
        }
    });
    
    // Gradual reveal of dashboard elements
    const dashboardElements = document.querySelectorAll('.dashboard-card, .stats-card, canvas');
    dashboardElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        element.style.transitionDelay = `${index * 0.1}s`;
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100);
    });
}

// Initialize interactive dashboard cards
function initializeDashboardCards() {
    // Add tilt effect to dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    
    dashboardCards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;
            
            const tiltX = deltaY * 5;
            const tiltY = -deltaX * 5;
            
            card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
            card.style.boxShadow = `
                ${-tiltY * 5}px ${tiltX * 5}px 20px rgba(0, 0, 0, 0.2),
                0 4px 20px rgba(0, 0, 0, 0.2)
            `;
        });
        
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            card.style.boxShadow = 'var(--box-shadow)';
        });
    });
    
    // Add click effect to stats cards
    const statsCards = document.querySelectorAll('.stats-card');
    statsCards.forEach(card => {
        card.addEventListener('click', function() {
            card.classList.add('stats-card-clicked');
            setTimeout(() => {
                card.classList.remove('stats-card-clicked');
            }, 300);
        });
    });
}