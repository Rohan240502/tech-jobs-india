// Indian Tech Job Market Intelligence - Core JS Controller

window.activeCharts = [];

document.addEventListener("DOMContentLoaded", function() {
    // 1. Activate Active Link in Navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-links a");
    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });

    // 2. Initialize Dashboard Charts (only if on dashboard page)
    if (document.getElementById("locationChart")) {
        initializeDashboardCharts();
    }

    // 3. Initialize Skills Analyzer Chart (only if on skills page)
    if (document.getElementById("skillsDemandChart")) {
        initializeSkillsChart();
    }

    // 4. Setup Theme Toggle Handler
    initializeThemeToggle();

    // 5. Setup AJAX Handlers
    setupAJAXHandlers();
});

// --- Dynamic Charts Setup for Dashboard (Screenshot 3) ---
function initializeDashboardCharts() {
    // Colors matching theme
    const colorOrange = '#f97316';
    const colorDark = '#0f172a';
    
    const isDark = document.body.classList.contains("dark-mode");
    
    const baseChartOptions = {
        theme: {
            mode: isDark ? 'dark' : 'light'
        },
        chart: {
            background: 'transparent',
            foreColor: isDark ? '#94a3b8' : '#64748b',
            toolbar: { show: false }
        },
        grid: {
            borderColor: isDark ? '#1f293d' : '#e2e8f0',
            strokeDashArray: 4
        }
    };

    // A. Top 10 In-Demand Roles Chart (Screenshot 3 - Left Column, dark navy horizontal bars)
    fetch('/api/stats/roles')
        .then(res => res.json())
        .then(data => {
            const options = {
                ...baseChartOptions,
                chart: { ...baseChartOptions.chart, type: 'bar', height: 350 },
                colors: [isDark ? '#3b82f6' : colorDark],
                series: [{ name: 'Job Openings', data: data.counts }],
                xaxis: { categories: data.labels },
                plotOptions: {
                    bar: {
                        borderRadius: 4,
                        horizontal: true,
                        barHeight: '40%'
                    }
                },
                title: { style: { fontFamily: 'Inter' } }
            };
            const chart = new ApexCharts(document.querySelector("#rolesChart"), options);
            chart.render();
            window.activeCharts.push(chart);
        });

    // B. Top Cities Chart (Screenshot 3 - Right Column, orange horizontal bars)
    fetch('/api/stats/locations')
        .then(res => res.json())
        .then(data => {
            const options = {
                ...baseChartOptions,
                chart: { ...baseChartOptions.chart, type: 'bar', height: 350 },
                colors: [colorOrange],
                series: [{ name: 'Job Openings', data: data.counts }],
                xaxis: { categories: data.labels },
                plotOptions: {
                    bar: {
                        borderRadius: 4,
                        horizontal: true,
                        barHeight: '40%'
                    }
                },
                title: { style: { fontFamily: 'Inter' } }
            };
            const chart = new ApexCharts(document.querySelector("#locationChart"), options);
            chart.render();
            window.activeCharts.push(chart);
        });

    // C. Average Salary by Role (Horizontal Bar)
    fetch('/api/stats/salary-by-role')
        .then(res => res.json())
        .then(data => {
            const options = {
                ...baseChartOptions,
                chart: { ...baseChartOptions.chart, type: 'bar', height: 320 },
                colors: ['#10b981'],
                series: [{ name: 'Average Salary (LPA)', data: data.salaries }],
                xaxis: { categories: data.labels },
                plotOptions: {
                    bar: {
                        borderRadius: 4,
                        horizontal: true,
                        barHeight: '55%'
                    }
                }
            };
            const chart = new ApexCharts(document.querySelector("#salaryRoleChart"), options);
            chart.render();
            window.activeCharts.push(chart);
        });

    // D. Salary vs Experience (Scatter Plot)
    fetch('/api/stats/salary-vs-experience')
        .then(res => res.json())
        .then(data => {
            const options = {
                ...baseChartOptions,
                chart: { ...baseChartOptions.chart, type: 'scatter', height: 320 },
                colors: [isDark ? '#818cf8' : '#6366f1'],
                series: [{
                    name: 'Jobs',
                    data: data.points.map(p => ({ x: p.experience, y: p.salary }))
                }],
                xaxis: {
                    title: { text: 'Experience Required (Years)' },
                    tickAmount: 10
                },
                yaxis: {
                    title: { text: 'Average Salary (LPA)' }
                }
            };
            const chart = new ApexCharts(document.querySelector("#salaryExperienceChart"), options);
            chart.render();
            window.activeCharts.push(chart);
        });
}

// --- Dynamic Chart for Skills Analyzer Page (Screenshot 4) ---
function initializeSkillsChart() {
    const chartColors = ['#0f172a', '#f97316', '#3b82f6', '#10b981', '#6366f1', '#ec4899', '#f59e0b', '#8b5cf6'];
    
    const isDark = document.body.classList.contains("dark-mode");
    
    fetch('/api/stats/skills-top-25')
        .then(res => res.json())
        .then(data => {
            const options = {
                chart: {
                    type: 'bar',
                    height: 900,
                    background: 'transparent',
                    foreColor: isDark ? '#94a3b8' : '#64748b',
                    toolbar: { show: false }
                },
                theme: {
                    mode: isDark ? 'dark' : 'light'
                },
                grid: {
                    borderColor: isDark ? '#1f293d' : '#e2e8f0',
                    strokeDashArray: 4
                },
                // Set custom colored bars dynamically
                colors: chartColors,
                plotOptions: {
                    bar: {
                        borderRadius: 4,
                        horizontal: true,
                        barHeight: '35%',
                        distributed: true
                    }
                },
                series: [{ name: 'Job Mentions', data: data.counts }],
                xaxis: { categories: data.labels },
                legend: { show: false }
            };
            const chart = new ApexCharts(document.querySelector("#skillsDemandChart"), options);
            chart.render();
            window.activeCharts.push(chart);
        });
}

// --- AJAX Form Handlers ---
function setupAJAXHandlers() {
    // A. Salary Predictor Form AJAX (Screenshot 2)
    const salaryForm = document.getElementById("salaryPredictorForm");
    if (salaryForm) {
        salaryForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const btn = this.querySelector("button[type='submit']");
            const originalText = btn.innerHTML;
            btn.innerHTML = "<i class='fa-solid fa-circle-notch fa-spin'></i> Predicting LPA...";
            btn.disabled = true;
            
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => { data[key] = value; });
            
            fetch('/api/predict-salary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(result => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                
                // Replace Right Column placeholder with actual dynamic predicted salary card!
                const rightCol = document.getElementById("predictionResultBox");
                rightCol.innerHTML = `
                    <h4 class="dark-card-title">Prediction Result</h4>
                    <div class="gauge-container" style="text-align: left; margin: 0 0 20px 0; max-width: 100%;">
                        <div class="gauge-title" style="font-size: 11px;">Expected average salary</div>
                        <div class="gauge-value" style="font-size: 54px; margin-top: 5px; font-weight: 900; color: #f97316;">₹ ${result.avg_lpa} LPA</div>
                    </div>
                    <div style="margin-bottom: 20px; padding: 10px 14px; border-radius: 6px; background: rgba(249, 115, 22, 0.08); border: 1px solid rgba(249, 115, 22, 0.2); font-size: 12px; color: #f97316; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
                        <i class="fa-solid fa-fire"></i> Hot Market Indicator: Top 20% in geographic demand
                    </div>
                    <div style="font-size: 16px; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                        Market range: ${result.min_lpa} LPA - ${result.max_lpa} LPA
                    </div>
                    <p style="font-size: 13px; color: #64748b; margin-bottom: 24px;">
                        Prediction engine: ${result.method}
                    </p>
                    <div style="border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 20px;">
                        <div style="font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;">
                            Market Analytics Breakdown
                        </div>
                        <p style="font-size: 13px; color: #64748b; line-height: 1.5; margin-bottom: 0;">
                            Your expected salary is successfully calculated by our AI-driven salary intelligence model. 
                            The pipeline evaluates:
                            <br>• <strong>Job Role:</strong> Title demand indexing.
                            <br>• <strong>Location:</strong> Geographical market factors.
                            <br>• <strong>Experience:</strong> Years of professional experience scaling.
                        </p>
                    </div>
                `;
            })
            .catch(err => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                alert("Error getting salary prediction. Please check server logs.");
            });
        });
    }

    // B. Resume Matcher Form AJAX (Screenshot 1)
    const resumeForm = document.getElementById("resumeParserForm");
    if (resumeForm) {
        resumeForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const btn = this.querySelector("button[type='submit']");
            const originalText = btn.innerHTML;
            btn.innerHTML = "<i class='fa-solid fa-circle-notch fa-spin'></i> Running ATS Scan...";
            btn.disabled = true;
            
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => { data[key] = value; });
            
            fetch('/api/analyze-resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(result => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                
                // Replace Right Column placeholder with ATS Gap Analysis details!
                const rightCol = document.getElementById("resumeResultBox");
                
                // Helper to render inline tags
                const makeTags = (list, cl) => {
                    if (!list || list.length === 0) return "<span style='font-size: 12px; color: #64748b;'>None detected</span>";
                    return list.map(item => `<span class="${cl}">${item}</span>`).join('');
                };

                // Helper to render jobs
                const makeJobs = (list) => {
                    if (!list || list.length === 0) return "<p style='font-size: 13px; color: #64748b;'>No job recommendations matches.</p>";
                    return list.map(job => `
                        <div class="glass-card stat-box" style="text-align: left; padding: 14px; margin-bottom: 10px; box-shadow: none; border-color: var(--border-light);">
                            <h4 style="color: var(--color-orange); font-size: 13px; margin-bottom: 2px;">${job.title}</h4>
                            <p style="font-size: 12px; font-weight: 700; margin-bottom: 4px;">${job.companyName} - ${job.location}</p>
                            <p style="font-size: 11px; color: var(--text-muted); margin-bottom: 0;">Skills: ${job.tagsAndSkills}</p>
                        </div>
                    `).join('');
                };

                rightCol.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; border-bottom: 1px solid var(--border-light); padding-bottom: 16px;">
                        <h3 style="font-size: 15px; font-weight: 800; color: var(--text-primary); margin-bottom: 0;">ATS Gap Analysis</h3>
                        <div style="font-family: var(--font-inter); font-size: 16px; font-weight: 800; color: var(--color-orange); background: rgba(249, 115, 22, 0.08); padding: 4px 10px; border-radius: 4px;">Fit Score: ${result.match_percentage}%</div>
                    </div>
                    
                    <!-- Career Lift Potential banner -->
                    <div style="padding: 12px 14px; border-radius: 8px; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); margin-bottom: 20px; display: flex; gap: 12px; align-items: center; transition: var(--transition-theme);">
                        <span style="color: #10b981; font-size: 18px;"><i class="fa-solid fa-arrow-trend-up"></i></span>
                        <div style="text-align: left;">
                            <div style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: var(--text-muted); letter-spacing: 0.05em; line-height: 1;">Career Lift Potential</div>
                            <div style="font-size: 12px; font-weight: 700; color: var(--text-primary); margin-top: 4px;">Acquiring missing skills could increase average salary potential by <strong>1.5 LPA - 3.2 LPA</strong>!</div>
                        </div>
                    </div>
                    
                    <div style="display: flex; flex-direction: column; gap: 20px; margin-bottom: 30px;">
                        <div>
                            <h4 style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: var(--color-orange); margin-bottom: 8px;">
                                <i class="fa-solid fa-circle-check"></i> Matching Skills (${result.matching_skills.length})
                            </h4>
                            <div class="tag-container">${makeTags(result.matching_skills, "tag selected")}</div>
                        </div>

                        <div>
                            <h4 style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #ef4444; margin-bottom: 8px;">
                                <i class="fa-solid fa-triangle-exclamation"></i> Skills Gap (Recommended to acquire)
                            </h4>
                            <div class="tag-container">${makeTags(result.missing_skills, "tag")}</div>
                        </div>

                        <div>
                            <h4 style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin-bottom: 8px;">
                                <i class="fa-solid fa-tags"></i> Total Detected Skills (${result.user_skills.length})
                            </h4>
                            <div class="tag-container">${makeTags(result.user_skills, "tag")}</div>
                        </div>
                    </div>

                    <div style="border-top: 1px solid var(--border-light); padding-top: 20px;">
                        <h4 style="font-size: 12px; font-weight: 800; color: var(--text-primary); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em;">
                            Best-Fit Job Openings
                        </h4>
                        <div>${makeJobs(result.recommended_jobs)}</div>
                    </div>
                `;
            })
            .catch(err => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                alert("Error analyzing resume. Please check server logs.");
            });
        });

        // Setup "Try sample" button click
        const trySampleBtn = document.getElementById("trySampleResumeBtn");
        if (trySampleBtn) {
            trySampleBtn.addEventListener("click", function() {
                const sampleText = "Highly accomplished Software Engineer with 3 years experience. Skilled in Python, SQL, REST APIs, Git, and Docker. Experience working with AWS cloud systems in an Agile DevOps environment.";
                document.getElementById("resume_text").value = sampleText;
            });
        }
    }

    // C. SQL Playground AJAX
    const sqlPlayForm = document.getElementById("sqlPlaygroundForm");
    if (sqlPlayForm) {
        sqlPlayForm.addEventListener("submit", function(e) {
            e.preventDefault();
            runActiveSQLQuery();
        });

        // Setup pre-made query clicks
        const queryButtons = document.querySelectorAll(".premade-query-btn");
        queryButtons.forEach(btn => {
            btn.addEventListener("click", function() {
                const queryText = this.getAttribute("data-query");
                document.getElementById("sqlQueryInput").value = queryText;
                runActiveSQLQuery();
            });
        });
    }
}

function runActiveSQLQuery() {
    const queryInput = document.getElementById("sqlQueryInput");
    const query = queryInput.value.trim();
    if (!query) return;

    const btn = document.getElementById("runSqlQueryBtn");
    btn.disabled = true;
    btn.innerText = "Querying Live DB...";
    
    fetch('/api/run-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(result => {
        btn.disabled = false;
        btn.innerText = "Execute Query";
        
        const resultsBox = document.getElementById("sqlResultsBox");
        resultsBox.style.display = "block";
        
        if (result.error) {
            resultsBox.innerHTML = `<div class="glass-card" style="border-color: #f43f5e; color: #f43f5e;"><strong>SQL Error:</strong><br>${result.error}</div>`;
            return;
        }

        if (result.rows.length === 0) {
            resultsBox.innerHTML = `<div class="glass-card" style="text-align: center;">Query successfully executed. Returned 0 rows.</div>`;
            return;
        }

        // Build HTML Table dynamically
        let tableHtml = `
            <p style="font-size: 14px; color: #10b981; margin-bottom: 12px;">Returned ${result.rows.length} rows successfully.</p>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            ${result.columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${result.rows.map(row => `
                            <tr>
                                ${result.columns.map(col => `<td>${row[col] !== null ? row[col] : '<em>NULL</em>'}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        resultsBox.innerHTML = tableHtml;
    })
    .catch(err => {
        btn.disabled = false;
        btn.innerText = "Execute Query";
        alert("Server failed to process query.");
    });
}

// --- Theme Toggling & Dynamic ApexCharts Synchronizer ---
function initializeThemeToggle() {
    const themeBtn = document.getElementById("themeToggleBtn");
    const themeIcon = document.getElementById("themeToggleIcon");
    if (!themeBtn || !themeIcon) return;

    // Check saved theme or system preference
    const savedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = savedTheme === "dark" || (!savedTheme && systemPrefersDark);

    if (isDark) {
        document.body.classList.add("dark-mode");
        themeIcon.className = "fa-solid fa-sun";
    } else {
        document.body.classList.remove("dark-mode");
        themeIcon.className = "fa-solid fa-moon";
    }

    // Toggle theme on click
    themeBtn.addEventListener("click", function() {
        if (document.body.classList.contains("dark-mode")) {
            document.body.classList.remove("dark-mode");
            themeIcon.className = "fa-solid fa-moon";
            localStorage.setItem("theme", "light");
            updateApexChartsTheme('light');
        } else {
            document.body.classList.add("dark-mode");
            themeIcon.className = "fa-solid fa-sun";
            localStorage.setItem("theme", "dark");
            updateApexChartsTheme('dark');
        }
    });
}

function updateApexChartsTheme(themeMode) {
    const isDark = themeMode === 'dark';
    
    // Dynamic series color swaps for roles and experience plots
    const roleBarColor = isDark ? '#3b82f6' : '#0f172a'; // blue bars on dark, slate on light
    const scatterColor = isDark ? '#818cf8' : '#6366f1'; // indigo shifts
    
    if (window.activeCharts && window.activeCharts.length > 0) {
        window.activeCharts.forEach(chart => {
            try {
                // Find if the chart element is Roles chart or Experience chart to update specific color sets
                const elId = chart.el ? chart.el.id : '';
                let customColors = null;
                
                if (elId === 'rolesChart') {
                    customColors = [roleBarColor];
                } else if (elId === 'salaryExperienceChart') {
                    customColors = [scatterColor];
                }
                
                const updateOpts = {
                    theme: {
                        mode: themeMode
                    },
                    chart: {
                        foreColor: isDark ? '#94a3b8' : '#64748b'
                    },
                    grid: {
                        borderColor: isDark ? '#1f293d' : '#e2e8f0'
                    }
                };
                
                if (customColors) {
                    updateOpts.colors = customColors;
                }
                
                chart.updateOptions(updateOpts);
            } catch (e) {
                console.error("Error updating active chart theme mode:", e);
            }
        });
    }
}
