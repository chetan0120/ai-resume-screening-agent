/* ==========================================================================
   AI RESUME SCREENING AGENT - FRONTEND JAVASCRIPT LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    
    // --------------------------------------------------------------------------
    // 1. STATE VARIABLES & APPS INITIALIZATION
    // --------------------------------------------------------------------------
    let selectedFiles = [];
    let activeChartInstance = null;
    let screeningHistory = [];
    
    // DOM Elements - General & Theme
    const bodyEl = document.body;
    const themeToggleBtn = document.getElementById('theme-toggle');
    const toastContainer = document.getElementById('toast-container');
    
    // DOM Elements - Sections
    const landingSection = document.getElementById('landing-section');
    const loadingSection = document.getElementById('loading-section');
    const resultsSection = document.getElementById('results-section');
    
    // DOM Elements - Uploader
    const analysisForm = document.getElementById('analysis-form');
    const dropzone = document.getElementById('dropzone');
    const resumeFileInput = document.getElementById('resume-file');
    const fileInfoPanel = document.getElementById('file-info');
    const fileNameText = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const jobDescriptionInput = document.getElementById('job-description');
    
    // DOM Elements - Loader
    const loadingProgress = document.getElementById('loading-progress');
    const loadingStatusText = document.getElementById('loading-status');
    
    // DOM Elements - Actions
    const btnDownloadReport = document.getElementById('btn-download-report');
    const btnReset = document.getElementById('btn-reset');
    
    // DOM Elements - History Drawer
    const historyToggleBtn = document.getElementById('history-toggle');
    const historySidebar = document.getElementById('history-sidebar');
    const historyCloseBtn = document.getElementById('history-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const historyListContainer = document.getElementById('history-list');
    const btnClearHistory = document.getElementById('btn-clear-history');
    
    // Theme setup from localStorage
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        bodyEl.classList.remove('dark-theme');
        bodyEl.classList.add('light-theme');
        themeToggleBtn.querySelector('i').className = 'fa-solid fa-sun';
    }

    // Toggle Theme Handler
    themeToggleBtn.addEventListener('click', () => {
        if (bodyEl.classList.contains('dark-theme')) {
            bodyEl.classList.remove('dark-theme');
            bodyEl.classList.add('light-theme');
            themeToggleBtn.querySelector('i').className = 'fa-solid fa-sun';
            localStorage.setItem('theme', 'light');
            showToast('Switched to light theme', 'info');
        } else {
            bodyEl.classList.remove('light-theme');
            bodyEl.classList.add('dark-theme');
            themeToggleBtn.querySelector('i').className = 'fa-solid fa-moon';
            localStorage.setItem('theme', 'dark');
            showToast('Switched to dark theme', 'info');
        }
        
        // Re-render chart if loaded to match theme styles
        if (resultsSection.classList.contains('hidden') === false) {
            updateRadarChartStyles();
        }
    });

    // --------------------------------------------------------------------------
    // 2. TOAST NOTIFICATION UTILITY
    // --------------------------------------------------------------------------
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let iconClass = 'fa-circle-info';
        if (type === 'success') iconClass = 'fa-circle-check';
        if (type === 'error') iconClass = 'fa-circle-exclamation';
        
        toast.innerHTML = `
            <i class="fa-solid ${iconClass}"></i>
            <span class="toast-message">${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Slide out and remove toast after 4s
        setTimeout(() => {
            toast.classList.add('removing');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 4000);
    }

    // --------------------------------------------------------------------------
    // 3. FILE UPLOAD & DRAG-AND-DROP HANDLERS
    // --------------------------------------------------------------------------
    const preventDefaults = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    // Handle dropped files
    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleSelectedFiles(files);
        }
    });

    // Handle browsed files
    resumeFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleSelectedFiles(e.target.files);
        }
    });

    function handleSelectedFiles(files) {
        selectedFiles = [];
        let invalidCount = 0;
        let largeCount = 0;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
                invalidCount++;
                continue;
            }
            
            if (file.size > 8 * 1024 * 1024) {
                largeCount++;
                continue;
            }
            
            selectedFiles.push(file);
        }
        
        if (invalidCount > 0) {
            showToast(`${invalidCount} file(s) skipped (only PDF format allowed).`, 'error');
        }
        if (largeCount > 0) {
            showToast(`${largeCount} file(s) skipped (exceeded 8MB limit).`, 'error');
        }
        
        if (selectedFiles.length > 0) {
            if (selectedFiles.length === 1) {
                fileNameText.textContent = selectedFiles[0].name;
            } else {
                fileNameText.textContent = `${selectedFiles.length} PDF resumes selected`;
            }
            
            // Hide browse visual elements, reveal selected file box
            dropzone.querySelector('.dropzone-content').classList.add('hidden');
            fileInfoPanel.classList.remove('hidden');
            showToast(`${selectedFiles.length} file(s) loaded successfully`, 'success');
        } else {
            fileInfoPanel.classList.add('hidden');
            dropzone.querySelector('.dropzone-content').classList.remove('hidden');
        }
    }

    // Remove selected file click handler
    removeFileBtn.addEventListener('click', (e) => {
        preventDefaults(e); // stop event bubbling to dropzone trigger
        selectedFiles = [];
        resumeFileInput.value = '';
        
        fileInfoPanel.classList.add('hidden');
        dropzone.querySelector('.dropzone-content').classList.remove('hidden');
        showToast('All files removed', 'info');
    });

    // Clicking dropzone triggers hidden file browser click
    dropzone.addEventListener('click', () => {
        if (selectedFiles.length === 0) {
            resumeFileInput.click();
        }
    });

    // --------------------------------------------------------------------------
    // 4. SUBMIT FORM & PIPELINE PROGRESS RUNNER
    // --------------------------------------------------------------------------
    analysisForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        if (selectedFiles.length === 0) {
            showToast('Please attach at least one resume PDF before starting analysis.', 'error');
            return;
        }
        
        const jdVal = jobDescriptionInput.value.trim();
        if (!jdVal) {
            showToast('Please enter a job description.', 'error');
            return;
        }
        
        // Transition to loader
        landingSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        
        const isBatch = selectedFiles.length > 1;
        
        // Reset loader status
        const uploadMsg = isBatch ? `Uploading ${selectedFiles.length} resumes...` : 'Uploading resume PDF...';
        updateLoaderProgress(5, uploadMsg);
        
        // Construct upload payload
        const formData = new FormData();
        formData.append('job_description', jdVal);
        
        if (isBatch) {
            for (let i = 0; i < selectedFiles.length; i++) {
                formData.append('resumes', selectedFiles[i]);
            }
        } else {
            formData.append('resume', selectedFiles[0]);
        }
        
        // Fake intervals to show pipeline execution progress in UI
        let progressVal = 5;
        const progressInterval = setInterval(() => {
            if (progressVal < 90) {
                progressVal += Math.floor(Math.random() * 8) + 2;
                let text = isBatch ? 'Processing batch resumes...' : 'Running parsing routines...';
                if (progressVal > 20 && progressVal <= 45) {
                    text = isBatch ? 'Extracting texts in parallel...' : 'Extracting resume text structures...';
                } else if (progressVal > 45 && progressVal <= 65) {
                    text = isBatch ? 'Measuring semantic vector space similarities...' : 'Measuring local semantic similarity vectors...';
                } else if (progressVal > 65 && progressVal <= 85) {
                    text = isBatch ? 'Consulting Groq Llama-3.3 on batch models...' : 'Consulting Groq Llama-3.3 API model...';
                } else if (progressVal > 85) {
                    text = 'Compiling ranked shortlist matrices...';
                }
                updateLoaderProgress(progressVal, text);
            }
        }, 800);
        
        const endpoint = isBatch ? '/analyze_batch' : '/analyze';
        
        // API Fetch
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Server screening analysis failed.');
                });
            }
            return response.json();
        })
        .then(data => {
            clearInterval(progressInterval);
            updateLoaderProgress(100, 'Analysis complete!');
            
            setTimeout(() => {
                loadingSection.classList.add('hidden');
                
                if (isBatch) {
                    showBatchDashboard(data);
                } else {
                    document.getElementById('leaderboard-container').classList.add('hidden');
                    showDashboard(data);
                }
                
                showToast(isBatch ? 'Batch screening completed!' : 'Hiring analysis report generated!', 'success');
                
                // Refresh screening history log
                loadScreeningHistory();
            }, 600);
        })
        .catch(err => {
            clearInterval(progressInterval);
            loadingSection.classList.add('hidden');
            landingSection.classList.remove('hidden');
            
            showToast(err.message, 'error');
            console.error(err);
        });
    });

    function updateLoaderProgress(pct, statusText) {
        loadingProgress.style.width = `${pct}%`;
        loadingStatusText.textContent = statusText;
    }

    // Reset Dashboard visual states
    btnReset.addEventListener('click', () => {
        resetDashboard();
    });

    function resetDashboard() {
        resultsSection.classList.add('hidden');
        landingSection.classList.remove('hidden');
        
        // Reset uploader form states
        selectedFiles = [];
        resumeFileInput.value = '';
        jobDescriptionInput.value = '';
        fileInfoPanel.classList.add('hidden');
        dropzone.querySelector('.dropzone-content').classList.remove('hidden');
        
        // Destroy existing Chart instances
        if (activeChartInstance) {
            activeChartInstance.destroy();
            activeChartInstance = null;
        }
    }

    // --------------------------------------------------------------------------
    // 5. RENDER SCORE GAUGES & DASHBOARD CARDS
    // --------------------------------------------------------------------------
    function showBatchDashboard(data) {
        // Toggle view blocks
        landingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Show Leaderboard container
        const lbContainer = document.getElementById('leaderboard-container');
        lbContainer.classList.remove('hidden');
        
        const lbRows = document.getElementById('leaderboard-rows');
        lbRows.innerHTML = '';
        
        const leaderboard = data.leaderboard;
        
        leaderboard.forEach((candidate, idx) => {
            const tr = document.createElement('tr');
            
            // Score colors
            const score = candidate.overall_match_score;
            const scoreClass = score >= 70 ? 'text-green' : (score >= 50 ? 'text-yellow' : 'text-rose');
            
            // Verdict badge classes
            const rec = candidate.hiring_recommendation;
            let badgeClass = 'bg-yellow';
            if (rec.toLowerCase().includes('strong hire')) badgeClass = 'bg-green';
            else if (rec.toLowerCase().includes('hire')) badgeClass = 'bg-purple';
            else if (rec.toLowerCase().includes('reject')) badgeClass = 'bg-red';
            
            tr.innerHTML = `
                <td><strong>#${idx + 1}</strong></td>
                <td><span class="candidate-table-name">${candidate.candidate_name}</span></td>
                <td class="${scoreClass}"><strong>${score}%</strong></td>
                <td>${candidate.semantic_similarity_score}%</td>
                <td>${candidate.ats_score}%</td>
                <td><span class="badge ${badgeClass}">${rec}</span></td>
                <td>
                    <button class="btn-secondary btn-sm btn-view-dashboard" data-index="${idx}">
                        <i class="fa-solid fa-chart-simple"></i> View Details
                    </button>
                </td>
            `;
            
            // Click to load dashboard details
            tr.querySelector('.btn-view-dashboard').addEventListener('click', () => {
                // Remove active styling on other rows
                lbRows.querySelectorAll('tr').forEach(r => r.classList.remove('active-row'));
                tr.classList.add('active-row');
                
                // Load details
                showDashboard(candidate);
                showToast(`Viewing report: ${candidate.candidate_name}`, 'info');
                
                // Scroll to details dashboard smoothly
                document.getElementById('overall-gauge').scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
            
            lbRows.appendChild(tr);
        });
        
        // Set first row as active
        if (lbRows.children.length > 0) {
            lbRows.children[0].classList.add('active-row');
        }
        
        // Load the 1st ranked candidate details by default
        showDashboard(leaderboard[0]);
    }

    function showDashboard(data) {
        // Toggle view blocks
        landingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Basic Metadata
        document.getElementById('result-candidate-name').textContent = data.candidate_name;
        
        // Recommendation Badge styling
        const recBadge = document.getElementById('result-recommendation-badge');
        recBadge.textContent = data.hiring_recommendation;
        recBadge.className = 'badge'; // clear previous colors
        
        const recLower = data.hiring_recommendation.toLowerCase();
        if (recLower.includes('strong hire')) {
            recBadge.classList.add('bg-green');
        } else if (recLower.includes('hire')) {
            recBadge.classList.add('bg-purple');
        } else if (recLower.includes('borderline')) {
            recBadge.classList.add('bg-yellow');
        } else {
            recBadge.classList.add('bg-red');
        }
        
        // Readiness Badge
        const readinessBadge = document.getElementById('result-readiness-badge');
        readinessBadge.textContent = `Readiness: ${data.interview_readiness}`;
        readinessBadge.className = 'badge';
        const readyLower = data.interview_readiness.toLowerCase();
        if (readyLower.includes('high')) {
            readinessBadge.classList.add('bg-green');
        } else if (readyLower.includes('medium')) {
            readinessBadge.classList.add('bg-purple');
        } else {
            readinessBadge.classList.add('bg-red');
        }
        
        // Set report download route
        btnDownloadReport.href = `/download/${data.download_filename}`;
        
        // Animate circular progress gauges
        animateCircularGauge('overall-gauge', 'overall-score-text', data.overall_match_score);
        animateCircularGauge('semantic-gauge', 'semantic-score-text', data.semantic_similarity_score);
        animateCircularGauge('ats-gauge', 'ats-score-text', data.ats_score);
        
        // Animate linear progress bars
        animateLinearProgress('experience-progress-bar', 'experience-score-text', data.experience_score);
        animateLinearProgress('education-progress-bar', 'education-score-text', data.education_score);
        animateLinearProgress('keyword-progress-bar', 'keyword-score-text', data.overall_match_score); // keyword match uses overall match/keyword counts
        
        // Set texts and checklists
        document.getElementById('result-candidate-summary').textContent = data.candidate_summary;
        document.getElementById('result-recruiter-verdict').textContent = data.recruiter_verdict;
        
        // Render Strengths list
        renderList('result-strengths-list', data.strengths);
        // Render Weaknesses list
        renderList('result-weaknesses-list', data.weaknesses);
        // Render Improvements list
        renderList('result-improvements-list', data.suggested_improvements);
        
        // Render Keywords tag links
        const keywordsContainer = document.getElementById('result-keywords-container');
        keywordsContainer.innerHTML = '';
        if (data.missing_keywords && data.missing_keywords.length > 0) {
            data.missing_keywords.forEach(keyword => {
                const span = document.createElement('span');
                span.className = 'tag tag-violet';
                span.textContent = keyword;
                keywordsContainer.appendChild(span);
            });
        } else {
            keywordsContainer.innerHTML = '<span class="tag tag-green">All key terms match</span>';
        }
        
        // Set checklist classes
        setChecklistState('check-exp', data.ats_checklist.experience);
        setChecklistState('check-edu', data.ats_checklist.education);
        setChecklistState('check-ski', data.ats_checklist.skills);
        setChecklistState('check-eml', data.ats_contacts.email_found);
        setChecklistState('check-phn', data.ats_contacts.phone_found);
        setChecklistState('check-lnk', data.ats_contacts.linkedin_found);
        
        // Render formatting issues warnings
        renderList('result-formatting-list', data.formatting_issues, 'No formatting issues detected! Structural elements look solid.');
        
        // Categorized Skills Overlaps
        renderCategorizedSkills('found-skills-container', data.found_skills, 'tag-green', 'No matching skills found from standard categories.');
        renderCategorizedSkills('missing-skills-container', data.missing_skills, 'tag-red', 'No missing required skills detected in taxonomy.');
        
        // Render target interview questions
        renderInterviewQuestions(data.suggested_interview_questions);
        
        // Trigger Radar Chart
        renderRadarChart(data.found_skills, data.missing_skills);
        
        // Confetti Spray for outstanding candidates (Match > 90%)
        if (data.overall_match_score >= 90.0) {
            setTimeout(() => {
                triggerConfettiExplosion();
            }, 1000);
        }
    }

    function animateCircularGauge(elementId, textId, score) {
        const ring = document.getElementById(elementId);
        const textVal = document.getElementById(textId);
        const radius = ring.r.baseVal.value;
        const circumference = 2 * Math.PI * radius; // 439.8
        
        // Set dash properties
        ring.style.strokeDasharray = `${circumference} ${circumference}`;
        
        const offset = circumference - (score / 100) * circumference;
        ring.style.strokeDashoffset = circumference; // start empty
        
        // Trigger transition rendering
        setTimeout(() => {
            ring.style.strokeDashoffset = offset;
        }, 100);
        
        // Animate counter text
        let count = 0;
        const step = score / 50; // increment step
        const timer = setInterval(() => {
            count += step;
            if (count >= score) {
                textVal.textContent = `${Math.round(score)}%`;
                clearInterval(timer);
            } else {
                textVal.textContent = `${Math.round(count)}%`;
            }
        }, 15);
    }

    function animateLinearProgress(elementId, textId, score) {
        const barFill = document.getElementById(elementId);
        const labelText = document.getElementById(textId);
        
        barFill.style.width = '0%';
        labelText.textContent = '0%';
        
        setTimeout(() => {
            barFill.style.width = `${score}%`;
            labelText.textContent = `${Math.round(score)}%`;
        }, 150);
    }

    function renderList(listId, items, emptyText = 'None identified.') {
        const listEl = document.getElementById(listId);
        listEl.innerHTML = '';
        if (items && items.length > 0) {
            items.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                listEl.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = emptyText;
            listEl.appendChild(li);
        }
    }

    function setChecklistState(prefix, checkVal) {
        const icon = document.getElementById(`${prefix}-icon`);
        if (checkVal) {
            icon.className = 'fa-solid fa-circle-check check-yes';
        } else {
            icon.className = 'fa-solid fa-circle-xmark check-no';
        }
    }

    function renderCategorizedSkills(containerId, skillsDict, tagClass, emptyMsg) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        let hasSkills = false;
        if (skillsDict) {
            for (const [category, skills] of Object.entries(skillsDict)) {
                if (skills && skills.length > 0) {
                    hasSkills = true;
                    
                    const box = document.createElement('div');
                    box.className = 'skill-category-box';
                    
                    // Human readable header
                    const title = document.createElement('div');
                    title.className = 'skill-cat-title';
                    title.textContent = category.replace('_', ' ').toUpperCase();
                    box.appendChild(title);
                    
                    const tags = document.createElement('div');
                    tags.className = 'tags-container';
                    
                    skills.forEach(skill => {
                        const span = document.createElement('span');
                        span.className = `tag ${tagClass}`;
                        span.textContent = skill;
                        tags.appendChild(span);
                    });
                    
                    box.appendChild(tags);
                    container.appendChild(box);
                }
            }
        }
        
        if (!hasSkills) {
            container.innerHTML = `<p class="no-skills-msg">${emptyMsg}</p>`;
        }
    }

    function renderInterviewQuestions(questions) {
        const accordion = document.getElementById('result-questions-accordion');
        accordion.innerHTML = '';
        
        if (questions && questions.length > 0) {
            questions.forEach((qItem, idx) => {
                const item = document.createElement('div');
                item.className = 'accordion-item';
                
                item.innerHTML = `
                    <button class="accordion-header">
                        <span>Q${idx+1}: ${qItem.question}</span>
                        <i class="fa-solid fa-chevron-down"></i>
                    </button>
                    <div class="accordion-content">
                        <div class="accordion-inner">
                            <span class="badge bg-purple" style="align-self: flex-start;">Difficulty: ${qItem.difficulty || 'Medium'}</span>
                            <div class="answer-block">
                                <span class="answer-label">Target Answer Guidelines</span>
                                <p>${qItem.expected_answer}</p>
                            </div>
                        </div>
                    </div>
                `;
                
                // Toggle Accordion Click Event
                const header = item.querySelector('.accordion-header');
                const content = item.querySelector('.accordion-content');
                header.addEventListener('click', () => {
                    // Close other open accordions
                    document.querySelectorAll('.accordion-item').forEach(otherItem => {
                        if (otherItem !== item && otherItem.classList.contains('active')) {
                            otherItem.classList.remove('active');
                            otherItem.querySelector('.accordion-content').style.maxHeight = null;
                        }
                    });
                    
                    item.classList.toggle('active');
                    if (item.classList.contains('active')) {
                        content.style.maxHeight = content.scrollHeight + 'px';
                    } else {
                        content.style.maxHeight = null;
                    }
                });
                
                accordion.appendChild(item);
            });
        } else {
            accordion.innerHTML = '<p class="no-skills-msg">No targeted questions suggested.</p>';
        }
    }

    // Toggle skill overlap matrix tabs
    const tabBtnFound = document.getElementById('tab-btn-found');
    const tabBtnMissing = document.getElementById('tab-btn-missing');
    const tabContentFound = document.getElementById('tab-content-found');
    const tabContentMissing = document.getElementById('tab-content-missing');

    tabBtnFound.addEventListener('click', () => {
        tabBtnFound.classList.add('active');
        tabBtnMissing.classList.remove('active');
        tabContentFound.classList.add('active');
        tabContentMissing.classList.remove('active');
    });

    tabBtnMissing.addEventListener('click', () => {
        tabBtnMissing.classList.add('active');
        tabBtnFound.classList.remove('active');
        tabContentMissing.classList.add('active');
        tabContentFound.classList.remove('active');
    });

    // --------------------------------------------------------------------------
    // 6. CHART.JS INTERACTION CONFIGURATIONS
    // --------------------------------------------------------------------------
    function renderRadarChart(foundDict, missingDict) {
        if (activeChartInstance) {
            activeChartInstance.destroy();
        }
        
        // Labels for radar axes
        const categories = Object.keys(foundDict);
        const axesLabels = categories.map(cat => cat.replace('_', ' ').toUpperCase());
        
        // Calculate counts
        const foundCounts = [];
        const missingCounts = [];
        
        categories.forEach(cat => {
            const fCount = foundDict[cat] ? foundDict[cat].length : 0;
            const mCount = missingDict[cat] ? missingDict[cat].length : 0;
            
            foundCounts.push(fCount);
            missingCounts.push(fCount + mCount); // Max JD requirements is found + missing
        });
        
        // Setup configuration theme styles
        const isDark = bodyEl.classList.contains('dark-theme');
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)';
        const angleLineColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)';
        const pointLabelColor = isDark ? '#94a3b8' : '#475569';
        
        const ctx = document.getElementById('skillsRadarChart').getContext('2d');
        activeChartInstance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: axesLabels,
                datasets: [
                    {
                        label: 'Candidate Match Profile',
                        data: foundCounts,
                        backgroundColor: 'rgba(0, 255, 255, 0.15)',
                        borderColor: '#00ffff',
                        pointBackgroundColor: '#00ffff',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: '#00ffff',
                        borderWidth: 2
                    },
                    {
                        label: 'Job Requirements Profile',
                        data: missingCounts,
                        backgroundColor: 'rgba(138, 43, 226, 0.05)',
                        borderColor: 'rgba(138, 43, 226, 0.4)',
                        pointBackgroundColor: 'rgba(138, 43, 226, 0.6)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(138, 43, 226, 1)',
                        borderWidth: 1.5,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: angleLineColor },
                        grid: { color: gridColor },
                        pointLabels: {
                            color: pointLabelColor,
                            font: { family: 'Inter', size: 10, weight: 600 }
                        },
                        ticks: {
                            display: false, // hide counts axis
                            stepSize: 1
                        },
                        suggestedMin: 0
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: pointLabelColor,
                            font: { family: 'Inter', size: 11 }
                        }
                    }
                }
            }
        });
    }

    function updateRadarChartStyles() {
        if (!activeChartInstance) return;
        
        const isDark = bodyEl.classList.contains('dark-theme');
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)';
        const angleLineColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)';
        const pointLabelColor = isDark ? '#94a3b8' : '#475569';
        
        activeChartInstance.options.scales.r.grid.color = gridColor;
        activeChartInstance.options.scales.r.angleLines.color = angleLineColor;
        activeChartInstance.options.scales.r.pointLabels.color = pointLabelColor;
        activeChartInstance.options.plugins.legend.labels.color = pointLabelColor;
        
        activeChartInstance.update();
    }

    // --------------------------------------------------------------------------
    // 7. CONFETTI SUCCESS EXPLOSIONS
    // --------------------------------------------------------------------------
    function triggerConfettiExplosion() {
        const count = 200;
        const defaults = {
            origin: { y: 0.6 }
        };

        function fire(particleRatio, opts) {
            confetti(Object.assign({}, defaults, opts, {
                particleCount: Math.floor(count * particleRatio)
            }));
        }

        fire(0.25, {
            spread: 26,
            startVelocity: 55,
        });
        fire(0.2, {
            spread: 60,
        });
        fire(0.35, {
            spread: 100,
            decay: 0.91,
            scalar: 0.8
        });
        fire(0.1, {
            spread: 120,
            startVelocity: 25,
            decay: 0.92,
            scalar: 1.2
        });
        fire(0.1, {
            spread: 120,
            startVelocity: 45,
        });
        
        showToast('Top tier candidate match identified! (>90%)', 'success');
    }

    // --------------------------------------------------------------------------
    // 8. SIDEBAR HISTORY DRAWER LOGIC
    // --------------------------------------------------------------------------
    // Open History
    historyToggleBtn.addEventListener('click', () => {
        historySidebar.classList.add('open');
        sidebarOverlay.classList.remove('hidden');
        setTimeout(() => {
            sidebarOverlay.classList.add('open');
        }, 50);
        
        loadScreeningHistory();
    });

    // Close History
    const closeSidebar = () => {
        historySidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
        setTimeout(() => {
            sidebarOverlay.classList.add('hidden');
        }, 300);
    };

    historyCloseBtn.addEventListener('click', closeSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);

    function loadScreeningHistory() {
        fetch('/history')
            .then(res => res.json())
            .then(history => {
                screeningHistory = history;
                renderHistoryList();
            })
            .catch(err => {
                console.error("Failed to load history list:", err);
            });
    }

    function renderHistoryList() {
        historyListContainer.innerHTML = '';
        if (screeningHistory && screeningHistory.length > 0) {
            screeningHistory.forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `
                    <div class="history-item-header">
                        <span class="history-name" title="${item.candidate_name}">${item.candidate_name}</span>
                        <span class="history-score">${Math.round(item.overall_match_score)}%</span>
                    </div>
                    <div class="history-meta">
                        <span class="history-rec">${item.hiring_recommendation}</span>
                        <span class="history-date"><i class="fa-regular fa-calendar"></i> ${item.timestamp}</span>
                    </div>
                `;
                
                // Clicking history card loads full JSON report
                div.addEventListener('click', () => {
                    closeSidebar();
                    loadFullReport(item.id);
                });
                
                historyListContainer.appendChild(div);
            });
        } else {
            historyListContainer.innerHTML = '<p class="empty-history-text">No screening records found.</p>';
        }
    }

    function loadFullReport(reportId) {
        landingSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        updateLoaderProgress(50, 'Loading history record from server...');
        
        fetch(`/load-report/${reportId}`)
            .then(res => {
                if (!res.ok) throw new Error('Report could not be retrieved.');
                return res.json();
            })
            .then(data => {
                loadingSection.classList.add('hidden');
                showDashboard(data);
                showToast(`Loaded candidate: ${data.candidate_name}`, 'success');
            })
            .catch(err => {
                loadingSection.classList.add('hidden');
                landingSection.classList.remove('hidden');
                showToast(err.message, 'error');
            });
    }

    // Clear History handler
    btnClearHistory.addEventListener('click', () => {
        if (confirm("Are you sure you want to permanently clear the screening history? This does not delete actual report files but empties this panel view.")) {
            fetch('/clear-history', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        showToast(data.message, 'success');
                        loadScreeningHistory();
                    } else {
                        showToast(data.error, 'error');
                    }
                })
                .catch(err => {
                    showToast('Clear action failed.', 'error');
                    console.error(err);
                });
        }
    });

    // Initial history list retrieve
    loadScreeningHistory();
});
