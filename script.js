document.addEventListener('DOMContentLoaded', function() {
    const scanBtn = document.getElementById('scanBtn');
    const progressBar = document.getElementById('progressBar');
    const progressFill = document.querySelector('.progress-fill');
    const resultsTable = document.getElementById('resultsTable');
    const resultsBody = document.getElementById('resultsBody');
    const noResults = document.getElementById('noResults');
    const exportJson = document.getElementById('exportJson');
    const exportCsv = document.getElementById('exportCsv');
    const spinner = document.querySelector('.spinner');
    const btnText = document.querySelector('.btn-text');
    
    let scanInterval;
    
    // Scan button event listener
    scanBtn.addEventListener('click', startScan);
    
    // Export button event listeners
    exportJson.addEventListener('click', () => exportResults('json'));
    exportCsv.addEventListener('click', () => exportResults('csv'));
    
    function startScan() {
        // Disable button and show spinner
        scanBtn.disabled = true;
        spinner.classList.remove('hidden');
        btnText.textContent = 'Scanning...';
        
        // Show progress bar
        progressBar.classList.remove('hidden');
        progressFill.style.width = '0%';
        
        // Start progress simulation
        let progress = 0;
        scanInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(scanInterval);
            }
            progressFill.style.width = `${progress}%`;
        }, 200);
        
        // Call backend to start scan
        fetch('/scan')
            .then(response => response.json())
            .then(data => {
                // Start polling for results
                pollForResults();
            })
            .catch(error => {
                console.error('Error starting scan:', error);
                resetScanButton();
            });
    }
    
    function pollForResults() {
        // Poll every 1 second for results
        const pollInterval = setInterval(() => {
            fetch('/results')
                .then(response => response.json())
                .then(data => {
                    if (!data.in_progress) {
                        clearInterval(pollInterval);
                        displayResults(data.results);
                        resetScanButton();
                        
                        // Enable export buttons
                        exportJson.disabled = false;
                        exportCsv.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error fetching results:', error);
                    clearInterval(pollInterval);
                    resetScanButton();
                });
        }, 1000);
    }
    
    function displayResults(results) {
        // Clear existing results
        resultsBody.innerHTML = '';
        
        if (results.length === 0) {
            noResults.classList.remove('hidden');
            resultsTable.classList.add('hidden');
            return;
        }
        
        // Hide no results message and show table
        noResults.classList.add('hidden');
        resultsTable.classList.remove('hidden');
        
        // Populate table with results
        results.forEach(network => {
            const row = document.createElement('tr');
            
            // Check if this is an error message
            if (network.Error) {
                row.innerHTML = `
                    <td colspan="6" style="text-align: center; color: #ff3366;">
                        ${network.Error}
                    </td>
                `;
            } else {
                // Add vulnerability class for styling
                let scoreClass = '';
                if (network.SecurityScore.includes('Secure')) {
                    scoreClass = 'score-secure';
                } else if (network.SecurityScore.includes('Moderate')) {
                    scoreClass = 'score-moderate';
                } else if (network.SecurityScore.includes('Vulnerable')) {
                    scoreClass = 'score-vulnerable';
                }
                
                row.innerHTML = `
                    <td>${network.SSID || 'N/A'}</td>
                    <td>${network.BSSID || 'N/A'}</td>
                    <td>${network.SignalStrength || 'N/A'}</td>
                    <td>${network.Channel || 'N/A'}</td>
                    <td>${network.Encryption || 'N/A'}</td>
                    <td class="${scoreClass}">${network.SecurityScore || 'N/A'}</td>
                `;
            }
            
            resultsBody.appendChild(row);
        });
    }
    
    function resetScanButton() {
        // Re-enable button and hide spinner
        scanBtn.disabled = false;
        spinner.classList.add('hidden');
        btnText.textContent = 'Scan Networks';
        
        // Hide progress bar
        setTimeout(() => {
            progressBar.classList.add('hidden');
        }, 500);
    }
    
    function exportResults(format) {
        // Create a temporary link to trigger download
        const link = document.createElement('a');
        link.href = `/export/${format}`;
        link.download = `scan_results.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});