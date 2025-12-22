// DPDP Act Compliance Scorecard - Frontend Display Layer
// All calculations are done in the backend (scorer.py)
// This file ONLY displays the data sent from backend

(function() {
  'use strict';

  // =========================================
  // TABLE RENDERING FUNCTIONS
  // =========================================

  /**
   * Render Table A: Overall Summary
   * Displays the executive summary with overall score, grade, and status
   */
  function renderOverallSummary(provider, overallData) {
    const container = document.getElementById('summary-table');
    if (!container) return;

    const statusClass = overallData.status === 'COMPLIANT'
      ? 'status-compliant'
      : 'status-needs-improvement';

    const statusIcon = overallData.status === 'COMPLIANT' ? '✓' : '⚠';

    const html = `
      <div class="summary-card">
        <div class="summary-row">
          <span class="summary-label">Provider:</span>
          <span class="summary-value">${provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Overall DPDP Score:</span>
          <span class="summary-value score-highlight">${overallData.score.toFixed(2)} / 100</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Compliance Grade:</span>
          <span class="summary-value grade-${overallData.grade.toLowerCase()}">${overallData.grade}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Status:</span>
          <span class="summary-value ${statusClass}">${statusIcon} ${overallData.status}</span>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  /**
   * Render Table B: Category Scorecard
   * Displays all DPDP categories with their scores and status
   */
  function renderCategoryScorecard(categories) {
    const container = document.getElementById('category-table');
    if (!container) return;

    let tableRows = '';

    categories.forEach(cat => {
      const scoreDisplay = cat.implemented
        ? `${cat.score_percent}%`
        : 'Not Evaluated';

      const contributionDisplay = cat.implemented
        ? cat.contribution.toFixed(2)
        : '—';

      const statusIcon = cat.implemented
        ? (cat.score_percent >= 60 ? '✓' : '✗')
        : '—';

      const rowClass = cat.implemented
        ? (cat.score_percent >= 60 ? 'row-pass' : 'row-fail')
        : 'row-pending';

      tableRows += `
        <tr class="${rowClass}">
          <td class="col-category">${cat.category}</td>
          <td class="col-score">${scoreDisplay}</td>
          <td class="col-weight">${cat.weight.toFixed(2)}</td>
          <td class="col-contribution">${contributionDisplay}</td>
          <td class="col-status">${statusIcon}</td>
        </tr>
      `;
    });

    const html = `
      <table class="scorecard-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Score (%)</th>
            <th>Weight</th>
            <th>Weighted Points</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${tableRows}
        </tbody>
      </table>
    `;

    container.innerHTML = html;
  }

  /**
   * Render Table C: Category Tabs
   * Creates tabs for all implemented categories
   */
  function renderCategoryTabs(categories) {
    const tabsContainer = document.getElementById('category-tabs');
    if (!tabsContainer) return;

    const implementedCategories = categories.filter(cat => cat.implemented);

    if (implementedCategories.length === 0) {
      tabsContainer.innerHTML = '<p class="no-data">No detailed breakdowns available yet.</p>';
      return;
    }

    let tabsHtml = '<div class="tabs-container">';

    implementedCategories.forEach((cat, index) => {
      const activeClass = index === 0 ? 'tab-active' : '';
      tabsHtml += `
        <button class="category-tab ${activeClass}"
                data-category="${cat.category}"
                onclick="switchCategoryBreakdown('${cat.category}')">
          ${cat.category}
        </button>
      `;
    });

    tabsHtml += '</div>';
    tabsContainer.innerHTML = tabsHtml;

    // Render the first category's breakdown by default
    if (implementedCategories.length > 0) {
      renderCategoryBreakdown(implementedCategories[0]);
    }
  }

  /**
   * Render breakdown for a specific category
   */
  function renderCategoryBreakdown(category) {
    const container = document.getElementById('breakdown-content');
    if (!container) return;

    const breakdown = category.breakdown || [];

    if (breakdown.length === 0) {
      container.innerHTML = '<p class="no-data">No checks available for this category.</p>';
      return;
    }

    let tableRows = '';
    let totalScore = 0;

    breakdown.forEach(check => {
      const passIcon = check.passed ? '✓' : '✗';
      const rowClass = check.passed ? 'row-pass' : 'row-fail';
      totalScore += check.contribution;

      tableRows += `
        <tr class="${rowClass}">
          <td class="col-check">
            <div class="check-name">${check.label}</div>
            <div class="check-message">${check.message}</div>
          </td>
          <td class="col-passed">${passIcon}</td>
          <td class="col-raw-score">${check.raw_score.toFixed(1)}</td>
          <td class="col-weight">${(check.weight * 100).toFixed(0)}%</td>
          <td class="col-contribution">${check.contribution.toFixed(2)}</td>
        </tr>
      `;
    });

    const html = `
      <table class="breakdown-table">
        <thead>
          <tr>
            <th>Check</th>
            <th>Passed</th>
            <th>Raw Score</th>
            <th>Weight</th>
            <th>Contribution</th>
          </tr>
        </thead>
        <tbody>
          ${tableRows}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="4" class="footer-label">Total ${category.category} Score</td>
            <td class="footer-value">${totalScore.toFixed(2)}</td>
          </tr>
        </tfoot>
      </table>
    `;

    container.innerHTML = html;
  }

  /**
   * Switch to a different category breakdown (called when tab clicked)
   */
  window.switchCategoryBreakdown = function(categoryName) {
    console.log('REPORT.JS: Switching to category:', categoryName);

    // Update active tab
    document.querySelectorAll('.category-tab').forEach(tab => {
      if (tab.dataset.category === categoryName) {
        tab.classList.add('tab-active');
      } else {
        tab.classList.remove('tab-active');
      }
    });

    // Find and render the category
    const category = window._currentScoringData.categories.find(
      cat => cat.category === categoryName && cat.implemented
    );

    if (category) {
      renderCategoryBreakdown(category);
    }
  };

  // =========================================
  // PDF DOWNLOAD
  // =========================================

  /**
   * Download compliance report as PDF
   * Sends the scoring data back to backend for PDF generation
   */
  function downloadReport(actualProviderName, scoringData) {
    const downloadBtn = document.getElementById('downloadBtn');
    const originalText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = 'Generating PDF...';
    downloadBtn.disabled = true;

    fetch('/download_pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        provider: actualProviderName,
        scoring_data: scoringData
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
      link.download = `${actualProviderName}_dpdp_compliance_report_${timestamp}.pdf`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      downloadBtn.innerHTML = originalText;
      downloadBtn.disabled = false;
    })
    .catch(error => {
      console.error('Error downloading PDF:', error);
      alert('Failed to generate PDF report. Please try again.');

      downloadBtn.innerHTML = originalText;
      downloadBtn.disabled = false;
    });
  }

  // =========================================
  // UTILITIES
  // =========================================

  /**
   * Map policy ID to provider name
   */
  function getProviderName(provider) {
    const providerMap = {
      '1': 'chatgpt',
      '2': 'claude',
      '3': 'gemini',
      '4': 'grok',
      'chatgpt': 'chatgpt',
      'claude': 'claude',
      'gemini': 'gemini',
      'grok': 'grok'
    };
    return providerMap[String(provider)] || provider;
  }

  // =========================================
  // INITIALIZATION
  // =========================================

  /**
   * Initialize the compliance scorecard
   * This function ONLY displays data - all calculations are done in backend
   */
  function init() {
    console.log('\n=== REPORT.JS: Initializing ===');
    console.log('REPORT.JS: Checking for scoringData...');
    console.log('REPORT.JS: typeof scoringData =', typeof scoringData);
    console.log('REPORT.JS: typeof providerName =', typeof providerName);

    // Validate data availability
    if (typeof scoringData === 'undefined' || typeof providerName === 'undefined') {
      console.error('REPORT.JS ERROR: Required data not found');
      console.error('REPORT.JS: scoringData =', typeof scoringData !== 'undefined' ? scoringData : 'UNDEFINED');
      console.error('REPORT.JS: providerName =', typeof providerName !== 'undefined' ? providerName : 'UNDEFINED');

      const container = document.getElementById('summary-table');
      if (container) {
        container.innerHTML = '<p class="error-message">Error: Scoring data not available</p>';
      }
      return;
    }

    console.log('REPORT.JS: Data validation passed');

    // Store globally for tab switching
    window._currentScoringData = scoringData;

    // Convert provider ID to name if needed
    const actualProviderName = getProviderName(providerName);
    console.log('REPORT.JS: Provider name:', actualProviderName);

    console.log('\n=== REPORT.JS: DISPLAYING BACKEND SCORING DATA ===');
    console.log('REPORT.JS: Overall Score:', scoringData.overall.score);
    console.log('REPORT.JS: Grade:', scoringData.overall.grade);
    console.log('REPORT.JS: Status:', scoringData.overall.status);
    console.log('REPORT.JS: Categories:', scoringData.categories.length);

    // Render all tables using backend-calculated data
    renderOverallSummary(actualProviderName, scoringData.overall);
    renderCategoryScorecard(scoringData.categories);

    // Render dynamic category tabs and breakdowns
    renderCategoryTabs(scoringData.categories);

    // Setup download button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', function() {
        downloadReport(actualProviderName, scoringData);
      });
      console.log('REPORT.JS: Download button event listener attached');
    }

    console.log('=== REPORT.JS: FRONTEND INITIALIZED - DISPLAY ONLY MODE ===\n');
  }

  // Run when page loads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
