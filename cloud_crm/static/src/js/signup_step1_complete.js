// Incluir la funcionalidad select2 en el campo de código postal
$(document).ready(function() {
    $('#zip_id').select2({
        width: '100%',
        placeholder: 'Search Zip...',
        allowClear: true,
        tokenSeparators: [","],
        maximumSelectionSize: 1,
        minimumInputLength: 0,
        ajax: {
            url: "/get_zip_list",
            quietMillis: 600,
            dataType: 'json',
            data: function(term, page) {
                console.log(page)
                return {
                    searchTerm: term || '',
                    page: page || 1,
                    pageSize: 20
                };
            },
            results: function(data, page) {
                var results = data.map(function(x) {
                    return {
                        id: x.id,
                        text: x.name,
                    };
                });
                return {
                    results: results,
                    more: data.length === 20 
                };
            },
        },
    });
});