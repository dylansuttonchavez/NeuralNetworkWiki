let currentPage = 1;

function loadPosts() {
    fetch(`/api/posts?page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                document.getElementById('load-more').style.display = 'none';
                return;
            }

            const postsContainer = document.getElementById('posts-container');
            data.forEach(post => {
                const postHtml = `
                    <a href="/archive/${post.slug}" class="block p-6 border rounded-lg hover:bg-gray-50 transition-colors">
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
                    </a>
                `;
                postsContainer.innerHTML += postHtml;
            });

            document.getElementById('load-more').style.display = 'inline-block';
            currentPage++;
        });
}

document.addEventListener('DOMContentLoaded', () => {
    loadPosts();

    document.getElementById('load-more').addEventListener('click', () => {
        loadPosts();
    });
});