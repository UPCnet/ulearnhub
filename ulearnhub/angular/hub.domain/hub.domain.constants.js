(function() {
    'use strict';

    angular
        .module('hub.domain')
        .constant('DTTranslations', {
            es: {
                'sProcessing': 'Procesando...',
                'sLengthMenu': 'Mostrar _MENU_ registros',
                'sZeroRecords': 'No se encontraron resultados',
                'sEmptyTable': 'Ningún dato disponible en esta tabla',
                'sInfo': 'Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros',
                'sInfoEmpty': 'Mostrando registros del 0 al 0 de un total de 0 registros',
                'sInfoFiltered': '(filtrado de un total de _MAX_ registros)',
                'sInfoPostFix': '',
                'sSearch': 'Buscar:',
                'sUrl': '',
                'sInfoThousands': '.',
                'sLoadingRecords': 'Cargando...',
                'oPaginate': {
                    'sFirst': 'Primero',
                    'sLast': 'Último',
                    'sNext': 'Siguiente',
                    'sPrevious': 'Anterior'
                },
                'oAria': {
                    'sSortAscending': ': Activar para ordenar la columna de manera ascendente',
                    'sSortDescending': ': Activar para ordenar la columna de manera descendente'
                }
            },
            ca: {
                'sProcessing': 'Processant...',
                'sLengthMenu': 'Mostra _MENU_ registres',
                'sZeroRecords': 'No s\'han trobat registres.',
                'sEmptyTable': 'No hi ha cap dada disponible en aquesta taula',
                'sInfo': 'Mostrant de _START_ a _END_ de _TOTAL_ registres',
                'sInfoEmpty': 'Mostrant de 0 a 0 de 0 registres',
                'sInfoFiltered': '(filtrat de _MAX_ total registres)',
                'sInfoPostFix': '',
                'sSearch': 'Filtrar:',
                'sUrl': '',
                'sInfoThousands': '.',
                'sLoadingRecords': 'Carregant...',
                'oPaginate': {
                    'sFirst': 'Primer',
                    'sPrevious': 'Anterior',
                    'sNext': 'Següent',
                    'sLast': 'Últim'
                },
                'oAria': {
                    'sSortAscending': ': Activa per ordenar la columna de manera ascendente',
                    'sSortDescending': ': Activa per ordenar la columna de manera descendente'
                }
            },
            en: {
                'sEmptyTable': 'No data available in table',
                'sInfo': 'Showing _START_ to _END_ of _TOTAL_ entries',
                'sInfoEmpty': 'Showing 0 to 0 of 0 entries',
                'sInfoFiltered': '(filtered from _MAX_ total entries)',
                'sInfoPostFix': '',
                'sInfoThousands': ',',
                'sLengthMenu': 'Show _MENU_ entries',
                'sLoadingRecords': 'Loading...',
                'sProcessing': 'Processing...',
                'sSearch': 'Search:',
                'sZeroRecords': 'No matching records found',
                'oPaginate': {
                    'sFirst': 'First',
                    'sLast': 'Last',
                    'sNext': 'Next',
                    'sPrevious': 'Previous'
                },
                'oAria': {
                    'sSortAscending': ': activate to sort column ascending',
                    'sSortDescending': ': activate to sort column descending'
                }
            }
        });
})();
