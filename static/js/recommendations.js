// GovConnect interactive AJAX engines

// --- 1. SCHEME ELIGIBILITY CHECKER ---
const eligibilityForm = document.getElementById('eligibilityCheckForm');
const eligibilityResults = document.getElementById('eligibilityResultsBox');

if (eligibilityForm && eligibilityResults) {
  eligibilityForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const schemeId = eligibilityForm.getAttribute('data-scheme-id');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData(eligibilityForm);

    // Show loading indicator
    eligibilityResults.innerHTML = `
      <div class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Calculating...</span>
        </div>
        <p class="mt-2 text-muted">Analyzing demographic criteria...</p>
      </div>
    `;
    eligibilityResults.style.display = 'block';

    fetch(`/schemes/${schemeId}/check/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const res = data.result;
        
        let headerColor = res.eligible ? 'var(--accent)' : 'var(--danger)';
        let statusText = res.eligible ? '✅ Eligible' : '❌ Not Eligible';
        let benefitHtml = res.eligible ? `
          <div class="alert alert-success d-flex justify-content-between align-items-center mt-3">
            <span>Estimated Benefit:</span>
            <strong class="fs-4">Rs. ${res.benefit_amount.toLocaleString('en-IN')}</strong>
          </div>
        ` : '';

        let reasonsList = res.reasons.map(r => `<li>${r}</li>`).join('');

        eligibilityResults.innerHTML = `
          <div class="p-3 border rounded" style="border-color: ${headerColor} !important;">
            <h4 style="color: ${headerColor};" class="mb-2">${statusText}</h4>
            <div class="progress mb-3" style="height: 20px;">
              <div class="progress-bar ${res.eligible ? 'bg-success' : 'bg-danger'}" 
                   role="progressbar" 
                   style="width: ${res.match_percentage}%;" 
                   aria-valuenow="${res.match_percentage}" 
                   aria-valuemin="0" 
                   aria-valuemax="100">
                   Score: ${res.match_percentage}%
              </div>
            </div>
            ${benefitHtml}
            <h6 class="mt-3">Criteria Analysis:</h6>
            <ul class="ps-3 text-muted">
              ${reasonsList}
            </ul>
          </div>
        `;
      } else {
        eligibilityResults.innerHTML = `
          <div class="alert alert-danger">Error: ${data.error}</div>
        `;
      }
    })
    .catch(err => {
      console.error(err);
      eligibilityResults.innerHTML = `
        <div class="alert alert-danger">An unexpected error occurred. Please try again.</div>
      `;
    });
  });
}

// --- 2. INTERACTIVE QUIZ ENGINE ---
const quizCard = document.getElementById('interactiveQuizCard');
const submitQuizBtn = document.getElementById('submitQuizBtn');
const quizResultsBox = document.getElementById('quizResultsBox');

if (quizCard && submitQuizBtn) {
  let selectedAnswers = {};

  // Setup click listeners on options
  const optionElements = quizCard.querySelectorAll('.quiz-option');
  optionElements.forEach(opt => {
    opt.addEventListener('click', () => {
      const qId = opt.getAttribute('data-question-id');
      const ans = opt.getAttribute('data-value');

      // Unselect other options in this question
      quizCard.querySelectorAll(`.quiz-option[data-question-id="${qId}"]`).forEach(sibling => {
        sibling.classList.remove('selected');
      });

      // Select clicked option
      opt.classList.add('selected');
      selectedAnswers[qId] = ans;
    });
  });

  submitQuizBtn.addEventListener('click', () => {
    const quizId = quizCard.getAttribute('data-quiz-id');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Check if all questions are answered
    const totalQuestions = quizCard.querySelectorAll('.quiz-question-card').length;
    if (Object.keys(selectedAnswers).length < totalQuestions) {
      alert('Please answer all questions before submitting.');
      return;
    }

    submitQuizBtn.disabled = true;
    submitQuizBtn.innerText = 'Grading...';

    fetch(`/quiz/${quizId}/submit/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ answers: selectedAnswers })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Disable option selection
        optionElements.forEach(opt => {
          opt.style.pointerEvents = 'none';
        });

        // Highlight correct and incorrect options
        data.results.forEach(res => {
          const qId = res.question_id;
          const userAns = res.user_answer;
          const correctAns = res.correct_answer;

          // Highlight correct option in green
          const correctOpt = quizCard.querySelector(`.quiz-option[data-question-id="${qId}"][data-value="${correctAns}"]`);
          if (correctOpt) {
            correctOpt.classList.add('correct');
          }

          // If user was wrong, highlight user option in red
          if (!res.is_correct) {
            const userOpt = quizCard.querySelector(`.quiz-option[data-question-id="${qId}"][data-value="${userAns}"]`);
            if (userOpt) {
              userOpt.classList.add('incorrect');
            }
          }
        });

        // Show results overlay
        let feedbackClass = data.percentage >= 60 ? 'alert-success' : 'alert-warning';
        quizResultsBox.innerHTML = `
          <div class="alert ${feedbackClass} text-center p-4 mt-4">
            <h3 class="mb-2">Quiz Completed!</h3>
            <p class="fs-4">You Scored <strong>${data.score} / ${data.total}</strong></p>
            <p class="text-muted mb-0">Grade Percentage: <strong>${data.percentage.toFixed(1)}%</strong></p>
          </div>
        `;
        quizResultsBox.style.display = 'block';
        submitQuizBtn.style.display = 'none';
      } else {
        alert('Grading failed: ' + data.error);
        submitQuizBtn.disabled = false;
        submitQuizBtn.innerText = 'Submit Quiz';
      }
    })
    .catch(err => {
      console.error(err);
      alert('Network failure occurred.');
      submitQuizBtn.disabled = false;
      submitQuizBtn.innerText = 'Submit Quiz';
    });
  });
}
