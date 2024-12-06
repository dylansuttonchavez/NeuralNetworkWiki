function debounce(func, delay) {
    let debounceTimer
    return function() {
        const context = this
        const args = arguments
        clearTimeout(debounceTimer)
        debounceTimer = setTimeout(() => func.apply(context, args), delay)
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    searchInput.addEventListener('input', debounce(() => {
        const query = searchInput.value.trim();

        if (query) {
            fetch(`/search_ajax?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = '';

                    if (data.length > 0) {
                        data.forEach(post => {
                            const resultItem = document.createElement('a');
                            resultItem.href = `/archive/${post.slug}`;
                            resultItem.className = 'block p-2 border-b last:border-b-0 hover:bg-gray-100';
                            resultItem.innerHTML = `
                                <h3 class="text-sm text-gray-800">${post.title}</h3>
                                <p class="text-xs text-gray-600">${post.content.substring(0, 50)}...</p>
                            `;
                            searchResults.appendChild(resultItem);
                        });
                        searchResults.classList.remove('hidden');
                    } else {
                        searchResults.innerHTML = '<div class="p-2 text-gray-600 text-sm">No results found.</div>';
                        searchResults.classList.remove('hidden');
                    }
                })
                .catch(error => {
                    console.error('AJAX search error:', error);
                    searchResults.innerHTML = '<div class="p-2 text-gray-600 text-sm">An error occurred while searching.</div>';
                    searchResults.classList.remove('hidden');
                });
        } else {
            searchResults.classList.add('hidden');
        }
    }, 300));

    document.addEventListener('click', (event) => {
        if (!searchResults.contains(event.target) && !searchInput.contains(event.target)) {
            searchResults.classList.add('hidden');
        }
    });
});