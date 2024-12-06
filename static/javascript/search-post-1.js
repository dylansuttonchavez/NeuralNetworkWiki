document.addEventListener('DOMContentLoaded', () => {
    const searchInputPage = document.getElementById('search-input-page');
    const searchResultsContainer = document.getElementById('search-results-container');
    const searchFeedback = document.getElementById('search-feedback');

    const handleSearch = debounce(() => {
        const query = searchInputPage.value.trim();

        if (query) {
            fetch(`/search_ajax?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResultsContainer.innerHTML = '';

                    if (data.length > 0) {
                        const limitedData = data.slice(0, 4);

                        limitedData.forEach(post => {
                            const card = document.createElement('a');
                            card.href = `/archive/${post.slug}`;
                            card.className = 'block p-6 border rounded-lg hover:bg-gray-50 transition-colors';
                            card.innerHTML = `
                                <div class="text-left">
                                    <h2 class="text-lg text-black">${post.title}</h2>
                                    <p class="text-sm text-gray-600 mt-1">
                                        ${post.content.substring(0, 76)}...
                                    </p>
                                    <div class="mt-2 flex justify-between items-center text-xs text-gray-500">
                                        <div class="flex space-x-2">
                                            <span class="px-2 py-0.5 bg-blue-200 text-blue-500 rounded">Science</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                            searchResultsContainer.appendChild(card);
                        });
                        searchFeedback.textContent = `Showing ${limitedData.length} results for "${query}".`;
                    } else {
                        searchResultsContainer.innerHTML = '<div class="p-4 text-gray-600 text-sm">No results found.</div>';
                        searchFeedback.textContent = `No results found for "${query}".`;
                    }
                })
                .catch(error => {
                    console.error('AJAX search error:', error);
                    searchResultsContainer.innerHTML = '<div class="p-4 text-gray-600 text-sm">An error occurred while searching.</div>';
                    searchFeedback.textContent = `An error occurred while searching.`;
                });
        } else {
            searchResultsContainer.innerHTML = '';
            searchFeedback.textContent = '';
        }
    }, 300);

    searchInputPage.addEventListener('input', handleSearch);

    document.addEventListener('click', (event) => {
        if (!searchResultsContainer.contains(event.target) && !searchInputPage.contains(event.target)) {
        }
    });
});