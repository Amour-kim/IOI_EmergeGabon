document.addEventListener('DOMContentLoaded', function() {
    // Timer functionality
    const timerElement = document.getElementById('quiz-timer');
    if (timerElement) {
        const duration = parseInt(timerElement.dataset.duration);
        let timeLeft = duration * 60; // Convert to seconds
        
        const timer = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                document.getElementById('quiz-form').submit();
            }
            
            timeLeft--;
        }, 1000);
    }
    
    // Question navigation
    const questions = document.querySelectorAll('.question');
    const navButtons = document.querySelectorAll('.question-nav-btn');
    
    function showQuestion(index) {
        questions.forEach((q, i) => {
            q.style.display = i === index ? 'block' : 'none';
        });
        
        navButtons.forEach((btn, i) => {
            btn.classList.toggle('active', i === index);
        });
    }
    
    navButtons.forEach((btn, index) => {
        btn.addEventListener('click', () => showQuestion(index));
    });
    
    // Auto-save responses
    let autoSaveTimeout;
    const formInputs = document.querySelectorAll('#quiz-form input, #quiz-form textarea');
    
    function autoSave() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            const formData = new FormData(document.getElementById('quiz-form'));
            
            fetch('/quiz/autosave/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const timestamp = new Date().toLocaleTimeString();
                    document.getElementById('autosave-status').textContent = 
                        `Sauvegardé automatiquement à ${timestamp}`;
                }
            })
            .catch(error => {
                console.error('Erreur de sauvegarde automatique:', error);
            });
        }, 5000); // Sauvegarde après 5 secondes d'inactivité
    }
    
    formInputs.forEach(input => {
        input.addEventListener('input', autoSave);
    });
    
    // Question flagging
    const flagButtons = document.querySelectorAll('.flag-question');
    
    flagButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const questionId = btn.dataset.questionId;
            const navButton = document.querySelector(
                `.question-nav-btn[data-question-id="${questionId}"]`
            );
            
            btn.classList.toggle('flagged');
            navButton.classList.toggle('flagged');
            
            // Mettre à jour le stockage local
            const flaggedQuestions = JSON.parse(
                localStorage.getItem('flaggedQuestions') || '[]'
            );
            
            if (btn.classList.contains('flagged')) {
                if (!flaggedQuestions.includes(questionId)) {
                    flaggedQuestions.push(questionId);
                }
            } else {
                const index = flaggedQuestions.indexOf(questionId);
                if (index > -1) {
                    flaggedQuestions.splice(index, 1);
                }
            }
            
            localStorage.setItem(
                'flaggedQuestions',
                JSON.stringify(flaggedQuestions)
            );
        });
    });
    
    // Restaurer les questions marquées au chargement
    const flaggedQuestions = JSON.parse(
        localStorage.getItem('flaggedQuestions') || '[]'
    );
    
    flaggedQuestions.forEach(questionId => {
        const flagBtn = document.querySelector(
            `.flag-question[data-question-id="${questionId}"]`
        );
        const navBtn = document.querySelector(
            `.question-nav-btn[data-question-id="${questionId}"]`
        );
        
        if (flagBtn) flagBtn.classList.add('flagged');
        if (navBtn) navBtn.classList.add('flagged');
    });
    
    // Confirmation avant de quitter
    window.addEventListener('beforeunload', function(e) {
        const form = document.getElementById('quiz-form');
        if (form && form.dataset.modified === 'true') {
            e.preventDefault();
            e.returnValue = '';
        }
    });
    
    // Marquer le formulaire comme modifié
    formInputs.forEach(input => {
        input.addEventListener('change', () => {
            document.getElementById('quiz-form').dataset.modified = 'true';
        });
    });
});
