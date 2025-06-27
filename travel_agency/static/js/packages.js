// static/js/packages.js
function loadPackages(search = '', page = 1) {
    $.ajax({
        url: '/api/packages/',
        type: 'GET',
        data: {
            search: search,
            page: page
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader(
                "Authorization", 
                "Bearer " + localStorage.getItem('access_token')
            );
        },
        success: function(response) {
            renderPackages(response.results);
            renderPagination(response);
        },
        error: function(xhr) {
            alert('Error loading packages: ' + xhr.responseText);
        }
    });
}

function renderPackages(packages) {
    const container = $('#packagesContainer');
    container.empty();
    
    if (packages.length === 0) {
        container.html('<div class="col-12"><div class="alert alert-info">No packages found.</div></div>');
        return;
    }
    
    packages.forEach(pkg => {
        const card = `
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <img src="https://placehold.co/300x200?text=Travel" class="card-img-top" alt="${pkg.title}">
                <div class="card-body">
                    <h5 class="card-title">${pkg.title}</h5>
                    <p class="card-text">${pkg.description.substring(0, 100)}...</p>
                    <p class="text-muted">${pkg.start_date} to ${pkg.end_date}</p>
                    <p class="fw-bold">$${pkg.price}</p>
                    <a href="/app/packages/${pkg.id}/" class="btn btn-primary">View Details</a>
                </div>
            </div>
        </div>`;
        container.append(card);
    });
}

function renderPagination(data) {
    const pagination = $('#pagination');
    pagination.empty();
    
    if (data.previous) {
        pagination.append(`<li class="page-item"><a class="page-link" href="#" onclick="loadPackages('${$('#searchInput').val()}', ${data.current_page - 1})">Previous</a></li>`);
    }
    
    // Add page numbers (simplified)
    for (let i = 1; i <= data.total_pages; i++) {
        const active = i === data.current_page ? 'active' : '';
        pagination.append(`<li class="page-item ${active}"><a class="page-link" href="#" onclick="loadPackages('${$('#searchInput').val()}', ${i})">${i}</a></li>`);
    }
    
    if (data.next) {
        pagination.append(`<li class="page-item"><a class="page-link" href="#" onclick="loadPackages('${$('#searchInput').val()}', ${data.current_page + 1})">Next</a></li>`);
    }
}