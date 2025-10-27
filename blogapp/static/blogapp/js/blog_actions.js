function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const csrftoken = getCookie('csrftoken');

    // Like button
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = likeBtn.dataset.url;
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                const likeCountSpan = document.getElementById('like-count');
                if (likeCountSpan) {
                    likeCountSpan.textContent = '❤️ ' + data.like_count;
                }
                likeBtn.textContent = data.is_liked ? 'Unlike' : 'Like';
            })
            .catch(err => {
                console.error('Error toggling like:', err);
                alert('Could not update like. Try again.');
            });
        });
    }

    // Comment form
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const url = commentForm.dataset.url || commentForm.action;
            const input = document.getElementById('comment-input');
            const content = input ? input.value.trim() : '';
            if (!content) {
                alert('Comment cannot be empty.');
                return;
            }

            const body = new URLSearchParams();
            body.append('content', content);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                },
                body: body.toString(),
            })
            .then(response => {
                if (!response.ok) return response.json().then(err => { throw err; });
                return response.json();
            })
            .then(data => {
                // Append new comment to the list
                const commentsList = document.getElementById('comments-list');
                const commentsCount = document.getElementById('comments-count');
                if (commentsList) {
                    const div = document.createElement('div');
                    div.className = 'border rounded p-2 mb-2 comment-item';
                    div.dataset.commentId = data.id;
                    const header = document.createElement('div');
                    header.className = 'd-flex justify-content-between';
                    const strong = document.createElement('strong');
                    strong.textContent = data.user;
                    const small = document.createElement('small');
                    small.className = 'text-muted';
                    // Try to humanize created_at if available
                    try {
                        const dt = new Date(data.created_at);
                        small.textContent = dt.toLocaleString();
                    } catch (e) {
                        small.textContent = '';
                    }
                    header.appendChild(strong);
                    header.appendChild(small);

                    const contentDiv = document.createElement('div');
                    contentDiv.textContent = data.content;

                    div.appendChild(header);
                    div.appendChild(contentDiv);

                        // If the user can modify the comment, append edit/delete buttons
                        if (data.can_modify) {
                            const actions = document.createElement('div');
                            actions.className = 'mt-2';

                            const editBtn = document.createElement('button');
                            editBtn.type = 'button';
                            editBtn.className = 'btn btn-sm btn-outline-secondary comment-edit-btn';
                            editBtn.dataset.editUrl = data.edit_url || '';
                            editBtn.textContent = 'Edit';

                            const delBtn = document.createElement('button');
                            delBtn.type = 'button';
                            delBtn.className = 'btn btn-sm btn-outline-danger comment-delete-btn';
                            delBtn.dataset.deleteUrl = data.delete_url || '';
                            delBtn.textContent = 'Delete';

                            actions.appendChild(editBtn);
                            actions.appendChild(delBtn);
                            div.appendChild(actions);
                        }

                        commentsList.insertBefore(div, commentsList.firstChild);
                }

                if (commentsCount) {
                    commentsCount.textContent = data.comment_count;
                }

                // Clear input
                if (input) input.value = '';
            })
            .catch(err => {
                console.error('Error posting comment:', err);
                if (err && err.error) alert(err.error);
                else alert('Could not post comment. Try again.');
            });
        });
    }

    // Event delegation for comment actions (delete/edit)
    const commentsList = document.getElementById('comments-list');
    if (commentsList) {
        commentsList.addEventListener('click', function(e) {
            const deleteBtn = e.target.closest('.comment-delete-btn');
            const editBtn = e.target.closest('.comment-edit-btn');

            // DELETE
            if (deleteBtn) {
                const url = deleteBtn.dataset.deleteUrl;
                if (!url) return;
                if (!confirm('Delete this comment?')) return;

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => {
                    if (!response.ok) return response.json().then(err => { throw err; });
                    return response.json();
                })
                .then(data => {
                    if (data.deleted) {
                        // remove comment element
                        const container = deleteBtn.closest('.comment-item');
                        if (container) container.remove();
                        const commentsCount = document.getElementById('comments-count');
                        if (commentsCount) commentsCount.textContent = data.comment_count;
                    }
                })
                .catch(err => {
                    console.error('Error deleting comment:', err);
                    alert('Could not delete comment.');
                });
            }

            // EDIT
            if (editBtn) {
                const url = editBtn.dataset.editUrl;
                if (!url) return;
                const item = editBtn.closest('.comment-item');
                if (!item) return;

                const contentDiv = item.querySelector('.comment-content');
                if (!contentDiv) return;

                // If already in edit mode, ignore
                if (item.querySelector('.comment-edit-input')) return;

                const originalText = contentDiv.textContent.trim();
                // create textarea and action buttons
                const input = document.createElement('textarea');
                input.className = 'form-control comment-edit-input mb-2';
                input.value = originalText;

                const saveBtn = document.createElement('button');
                saveBtn.type = 'button';
                saveBtn.className = 'btn btn-sm btn-primary me-2';
                saveBtn.textContent = 'Save';

                const cancelBtn = document.createElement('button');
                cancelBtn.type = 'button';
                cancelBtn.className = 'btn btn-sm btn-secondary';
                cancelBtn.textContent = 'Cancel';

                // replace contentDiv with input and buttons
                contentDiv.style.display = 'none';
                const editContainer = document.createElement('div');
                editContainer.className = 'comment-edit-container';
                editContainer.appendChild(input);
                editContainer.appendChild(saveBtn);
                editContainer.appendChild(cancelBtn);
                contentDiv.parentNode.insertBefore(editContainer, contentDiv.nextSibling);

                cancelBtn.addEventListener('click', function() {
                    editContainer.remove();
                    contentDiv.style.display = '';
                });

                saveBtn.addEventListener('click', function() {
                    const newContent = input.value.trim();
                    if (!newContent) { alert('Comment cannot be empty.'); return; }

                    const body = new URLSearchParams();
                    body.append('content', newContent);

                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'X-Requested-With': 'XMLHttpRequest',
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                        },
                        body: body.toString(),
                    })
                    .then(response => {
                        if (!response.ok) return response.json().then(err => { throw err; });
                        return response.json();
                    })
                    .then(data => {
                        // update content
                        contentDiv.textContent = data.content;
                        editContainer.remove();
                        contentDiv.style.display = '';
                    })
                    .catch(err => {
                        console.error('Error editing comment:', err);
                        if (err && err.error) alert(err.error);
                        else alert('Could not update comment.');
                    });
                });
            }
        });
    }
});
