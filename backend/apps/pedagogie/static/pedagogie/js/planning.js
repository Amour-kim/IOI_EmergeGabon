document.addEventListener('DOMContentLoaded', function() {
    // Configuration du calendrier
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        locale: 'fr',
        slotMinTime: '07:00:00',
        slotMaxTime: '20:00:00',
        allDaySlot: false,
        height: 'auto',
        expandRows: true,
        stickyHeaderDates: true,
        nowIndicator: true,
        dayMaxEvents: true,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        slotLabelFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        
        // Chargement des événements
        events: function(info, successCallback, failureCallback) {
            const filters = new URLSearchParams(
                new FormData(document.getElementById('filterForm'))
            ).toString();
            
            fetch(`/pedagogie/api/seances/?${filters}`)
                .then(response => response.json())
                .then(data => {
                    const events = data.map(seance => ({
                        id: seance.id,
                        title: `${seance.ecue_details.code} - ${seance.type_seance}`,
                        start: seance.date_debut,
                        end: seance.date_fin,
                        backgroundColor: getEventColor(seance.type_seance),
                        borderColor: getEventColor(seance.type_seance),
                        extendedProps: {
                            ecue: seance.ecue_details,
                            salle: seance.salle,
                            enseignant: seance.enseignant_nom,
                            statut: seance.statut,
                            description: seance.description
                        }
                    }));
                    successCallback(events);
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    failureCallback(error);
                });
        },
        
        // Gestion du clic sur un événement
        eventClick: function(info) {
            showSeanceDetails(info.event);
        },
        
        // Gestion du glisser-déposer
        editable: isUserAuthorized(),
        eventDrop: function(info) {
            updateSeance(info.event);
        },
        eventResize: function(info) {
            updateSeance(info.event);
        },
        
        // Gestion de la sélection de plage horaire
        selectable: isUserAuthorized(),
        select: function(info) {
            showAddSeanceModal(info);
        }
    });
    
    calendar.render();

    // Gestion des filtres
    document.getElementById('filterForm')?.addEventListener('change', function() {
        calendar.refetchEvents();
    });

    // Couleurs selon le type de séance
    function getEventColor(type) {
        switch (type) {
            case 'CM':
                return '#007bff';  // Bleu
            case 'TD':
                return '#28a745';  // Vert
            case 'TP':
                return '#ffc107';  // Jaune
            default:
                return '#6c757d';  // Gris
        }
    }

    // Vérification des autorisations
    function isUserAuthorized() {
        return document.body.hasAttribute('data-user-staff') || 
               document.body.hasAttribute('data-user-enseignant');
    }

    // Affichage des détails d'une séance
    function showSeanceDetails(event) {
        const modal = document.getElementById('seanceDetailsModal');
        const detailsContainer = document.getElementById('seanceDetails');
        
        const details = `
            <h6>${event.extendedProps.ecue.code} - ${event.extendedProps.ecue.intitule}</h6>
            <p><strong>Type :</strong> ${event.extendedProps.type_seance}</p>
            <p><strong>Enseignant :</strong> ${event.extendedProps.enseignant}</p>
            <p><strong>Salle :</strong> ${event.extendedProps.salle}</p>
            <p><strong>Date :</strong> ${formatDate(event.start)}</p>
            <p><strong>Horaire :</strong> ${formatTime(event.start)} - ${formatTime(event.end)}</p>
            <p><strong>Statut :</strong> ${event.extendedProps.statut}</p>
            ${event.extendedProps.description ? 
              `<p><strong>Description :</strong> ${event.extendedProps.description}</p>` : ''}
        `;
        
        detailsContainer.innerHTML = details;
        
        // Gestion des boutons d'action
        updateActionButtons(event);
        
        new bootstrap.Modal(modal).show();
    }

    // Mise à jour des boutons d'action
    function updateActionButtons(event) {
        if (!isUserAuthorized()) return;
        
        const startBtn = document.getElementById('startSeanceBtn');
        const endBtn = document.getElementById('endSeanceBtn');
        const cancelBtn = document.getElementById('cancelSeanceBtn');
        
        // Affichage conditionnel des boutons selon le statut
        switch (event.extendedProps.statut) {
            case 'PLANIFIE':
                startBtn.style.display = 'inline-block';
                endBtn.style.display = 'none';
                cancelBtn.style.display = 'inline-block';
                break;
            case 'EN_COURS':
                startBtn.style.display = 'none';
                endBtn.style.display = 'inline-block';
                cancelBtn.style.display = 'inline-block';
                break;
            case 'TERMINE':
                startBtn.style.display = 'none';
                endBtn.style.display = 'none';
                cancelBtn.style.display = 'none';
                break;
            case 'ANNULE':
                startBtn.style.display = 'none';
                endBtn.style.display = 'none';
                cancelBtn.style.display = 'none';
                break;
        }
        
        // Gestion des événements des boutons
        startBtn.onclick = () => updateSeanceStatus(event.id, 'commencer');
        endBtn.onclick = () => updateSeanceStatus(event.id, 'terminer');
        cancelBtn.onclick = () => updateSeanceStatus(event.id, 'annuler');
    }

    // Mise à jour du statut d'une séance
    async function updateSeanceStatus(seanceId, action) {
        try {
            const response = await fetch(
                `/pedagogie/api/seances/${seanceId}/${action}/`,
                {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            if (response.ok) {
                calendar.refetchEvents();
                bootstrap.Modal.getInstance(
                    document.getElementById('seanceDetailsModal')
                ).hide();
            } else {
                throw new Error('Erreur lors de la mise à jour du statut');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue lors de la mise à jour du statut');
        }
    }

    // Mise à jour d'une séance (drag & drop)
    async function updateSeance(event) {
        try {
            const response = await fetch(
                `/pedagogie/api/seances/${event.id}/`,
                {
                    method: 'PATCH',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        date_debut: event.start.toISOString(),
                        date_fin: event.end.toISOString()
                    })
                }
            );
            
            if (!response.ok) {
                throw new Error('Erreur lors de la mise à jour');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue lors de la mise à jour');
            calendar.refetchEvents();
        }
    }

    // Affichage du modal d'ajout de séance
    function showAddSeanceModal(info) {
        const modal = document.getElementById('addSeanceModal');
        if (!modal) return;
        
        // Pré-remplissage des dates
        document.getElementById('date_debut').value = 
            formatDateTimeForInput(info.start);
        document.getElementById('date_fin').value = 
            formatDateTimeForInput(info.end);
        
        new bootstrap.Modal(modal).show();
    }

    // Utilitaires de formatage
    function formatDate(date) {
        return new Intl.DateTimeFormat('fr-FR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(date);
    }

    function formatTime(date) {
        return new Intl.DateTimeFormat('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    function formatDateTimeForInput(date) {
        return date.toISOString().slice(0, 16);
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
