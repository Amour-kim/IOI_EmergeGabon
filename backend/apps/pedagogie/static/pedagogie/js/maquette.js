document.addEventListener('DOMContentLoaded', function() {
    // Gestion de la modal de suppression
    const deleteUEModal = document.getElementById('deleteUEModal');
    if (deleteUEModal) {
        deleteUEModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const ueId = button.getAttribute('data-ue-id');
            const ueCode = button.getAttribute('data-ue-code');
            
            // Mise à jour du formulaire et du texte
            document.getElementById('ueCodeToDelete').textContent = ueCode;
            document.getElementById('deleteUEForm').action = `/pedagogie/ues/${ueId}/delete/`;
        });
    }

    // Initialisation des tooltips
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Gestion des filtres
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }

    // Calcul des totaux
    function updateTotals() {
        const semestres = document.querySelectorAll('[data-semestre]');
        let creditsTotaux = 0;
        let volumeTotalCM = 0;
        let volumeTotalTD = 0;
        let volumeTotalTP = 0;

        semestres.forEach(semestre => {
            const credits = parseInt(semestre.getAttribute('data-credits')) || 0;
            const volumeCM = parseInt(semestre.getAttribute('data-volume-cm')) || 0;
            const volumeTD = parseInt(semestre.getAttribute('data-volume-td')) || 0;
            const volumeTP = parseInt(semestre.getAttribute('data-volume-tp')) || 0;

            creditsTotaux += credits;
            volumeTotalCM += volumeCM;
            volumeTotalTD += volumeTD;
            volumeTotalTP += volumeTP;
        });

        // Mise à jour des totaux dans l'interface
        document.getElementById('creditsTotaux').textContent = creditsTotaux;
        document.getElementById('volumeTotalCM').textContent = volumeTotalCM;
        document.getElementById('volumeTotalTD').textContent = volumeTotalTD;
        document.getElementById('volumeTotalTP').textContent = volumeTP;
        document.getElementById('volumeTotal').textContent = 
            volumeTotalCM + volumeTotalTD + volumeTotalTP;
    }

    // Appel initial pour calculer les totaux
    updateTotals();

    // Gestion de l'impression
    document.getElementById('printMaquette')?.addEventListener('click', function() {
        window.print();
    });

    // Gestion de l'export PDF
    document.getElementById('exportPDF')?.addEventListener('click', async function() {
        try {
            const response = await fetch(
                window.location.pathname + 'export-pdf/',
                {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                }
            );
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'maquette.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            } else {
                throw new Error('Erreur lors de l\'export PDF');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue lors de l\'export PDF');
        }
    });

    // Gestion des prérequis
    const prerequisSelect = document.querySelector('.prerequis-select');
    if (prerequisSelect) {
        $(prerequisSelect).select2({
            placeholder: 'Sélectionner les prérequis',
            allowClear: true,
            multiple: true,
            ajax: {
                url: '/pedagogie/ues/search/',
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        q: params.term,
                        page: params.page
                    };
                },
                processResults: function(data, params) {
                    params.page = params.page || 1;
                    return {
                        results: data.items,
                        pagination: {
                            more: (params.page * 30) < data.total_count
                        }
                    };
                },
                cache: true
            }
        });
    }
});
